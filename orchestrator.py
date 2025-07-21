import json
import yaml
import time
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from agent import OpenRouterAgent
from usage_tracker import UsageTracker

class TaskOrchestrator:
    def __init__(self, config_path="config.yaml", silent=False):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.num_agents = self.config['orchestrator']['parallel_agents']
        self.task_timeout = self.config['orchestrator']['task_timeout']
        self.aggregation_strategy = self.config['orchestrator']['aggregation_strategy']
        self.silent = silent
        
        # Load models from config
        self.heavy_duty_model = self.config['google_ai_studio']['models']['heavy_duty_model']
        self.worker_models = self.config['google_ai_studio']['models']['worker_models']
        
        # Validate configuration
        if not self.worker_models:
            raise Exception("No worker models configured in config.yaml")
        if self.num_agents > len(self.worker_models):
            if not self.silent:
                print(f"Warning: {self.num_agents} agents requested but only {len(self.worker_models)} models available")
        
        if not self.silent:
            print(f"Orchestrator initialized: {self.num_agents} agents, {len(self.worker_models)} models")
            for i, model in enumerate(self.worker_models):
                print(f"  Model {i}: {model}")

        # Track agent progress
        self.agent_progress = {}
        self.agent_results = {}
        self.progress_lock = threading.Lock()
        
        # Initialize usage tracker
        self.usage_tracker = UsageTracker()
    
    def decompose_task(self, user_input: str, num_agents: int) -> List[str]:
        """Use AI to dynamically generate different questions based on user input"""
        
        try:
            # Create question generation agent with the heavy-duty model
            question_agent = OpenRouterAgent(
                silent=True, 
                model=self.heavy_duty_model
            )
            
            # Get question generation prompt from config
            prompt_template = self.config['orchestrator']['question_generation_prompt']
            generation_prompt = prompt_template.format(
                user_input=user_input,
                num_agents=num_agents
            )
            
            # Remove task completion tool to avoid issues
            question_agent.tools = [tool for tool in question_agent.tools if tool.name != 'mark_task_complete']
            question_agent.tool_mapping = {name: func for name, func in question_agent.tool_mapping.items() if name != 'mark_task_complete'}
            
            # Get AI-generated questions
            response = question_agent.run(generation_prompt)
            
            # Parse JSON response
            questions = json.loads(response.strip())
            
            # Validate we got the right number of questions
            if len(questions) != num_agents:
                raise ValueError(f"Expected {num_agents} questions, got {len(questions)}")
            
            return questions
            
        except Exception as e:
            if not self.silent:
                print(f"Question generation failed: {str(e)}")
            # Fallback: create simple variations if AI fails
            return [
                f"Research comprehensive information about: {user_input}",
                f"Analyze and provide insights about: {user_input}",
                f"Find alternative perspectives on: {user_input}",
                f"Verify and cross-check facts about: {user_input}",
                f"Provide additional context about: {user_input}"
            ][:num_agents]
    
    def update_agent_progress(self, agent_id: int, status: str, result: str = None):
        """Thread-safe progress tracking"""
        with self.progress_lock:
            self.agent_progress[agent_id] = status
            if result is not None:
                self.agent_results[agent_id] = result
    
    def run_agent_parallel(self, agent_id: int, subtask: str) -> Dict[str, Any]:
        """
        Run a single agent with the given subtask.
        Returns result dictionary with agent_id, status, and response.
        """
        worker_model = "unknown"
        try:
            self.update_agent_progress(agent_id, "PROCESSING...")
            
            # Validate worker_models list
            if not self.worker_models or len(self.worker_models) == 0:
                raise Exception("No worker models configured")
            
            # Assign a specific worker model to each agent (round-robin)
            worker_model = self.worker_models[agent_id % len(self.worker_models)]
            
            if not self.silent:
                print(f"Agent {agent_id} using model: {worker_model}")

            # Create an agent with debug logging for troubleshooting
            agent = OpenRouterAgent(silent=False, model=worker_model)
            
            start_time = time.time()
            response = agent.run(subtask)
            execution_time = time.time() - start_time
            
            if not response or len(response.strip()) == 0:
                raise Exception("Agent returned empty response")
            
            self.update_agent_progress(agent_id, "COMPLETED", response)
            
            if not self.silent:
                print(f"Agent {agent_id} completed successfully in {execution_time:.2f}s")
            
            return {
                "agent_id": agent_id,
                "status": "success", 
                "response": response,
                "execution_time": execution_time,
                "model": worker_model
            }
            
        except Exception as e:
            # Detailed error handling for debugging
            error_msg = f"Agent {agent_id} failed with model {worker_model}: {str(e)}"
            if not self.silent:
                print(f"ERROR: {error_msg}")
                traceback.print_exc()
            
            self.update_agent_progress(agent_id, f"FAILED: {str(e)}")
            return {
                "agent_id": agent_id,
                "status": "error",
                "response": f"Error: {str(e)}",
                "execution_time": 0,
                "model": worker_model
            }
    
    def aggregate_results(self, agent_results: List[Dict[str, Any]]) -> str:
        """
        Combine results from all agents into a comprehensive final answer.
        """
        successful_results = [r for r in agent_results if r["status"] == "success"]
        
        if not successful_results:
            # Provide detailed failure information
            error_summary = "All agents failed to provide results:\n\n"
            for result in agent_results:
                error_summary += f"Agent {result['agent_id']} ({result['model']}): {result['response']}\n"
            return error_summary
        
        # Extract responses for aggregation
        responses = [r["response"] for r in successful_results]
        
        if len(responses) == 1:
            return responses[0]
        
        # Simple concatenation if synthesis fails
        combined = []
        for i, result in enumerate(successful_results):
            combined.append(f"=== Agent {result['agent_id']} Response ({result['model']}) ===")
            combined.append(result['response'])
            combined.append("")
        
        return "\n".join(combined)
    
    def get_progress_status(self) -> Dict[int, str]:
        """Get current progress status for all agents"""
        with self.progress_lock:
            return self.agent_progress.copy()
    
    def orchestrate(self, user_input: str):
        """
        Main orchestration method.
        Takes user input, delegates to parallel agents, and returns aggregated result.
        """
        
        # Reset progress tracking
        self.agent_progress = {}
        self.agent_results = {}
        
        # Decompose task into subtasks
        subtasks = self.decompose_task(user_input, self.num_agents)
        
        if not self.silent:
            print(f"Generated {len(subtasks)} subtasks for {self.num_agents} agents")
        
        # Ensure we have enough subtasks
        while len(subtasks) < self.num_agents:
            subtasks.append(f"Additional analysis of: {user_input}")
        
        # Initialize progress tracking
        for i in range(self.num_agents):
            self.agent_progress[i] = "QUEUED"
        
        # Execute agents in parallel
        agent_results = []
        
        with ThreadPoolExecutor(max_workers=self.num_agents) as executor:
            # Submit all agent tasks
            future_to_agent = {
                executor.submit(self.run_agent_parallel, i, subtasks[i]): i 
                for i in range(self.num_agents)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent, timeout=self.task_timeout):
                try:
                    result = future.result()
                    agent_results.append(result)
                except Exception as e:
                    agent_id = future_to_agent[future]
                    if not self.silent:
                        print(f"Future execution failed for agent {agent_id}: {str(e)}")
                    agent_results.append({
                        "agent_id": agent_id,
                        "status": "timeout",
                        "response": f"Agent {agent_id + 1} timed out or failed: {str(e)}",
                        "execution_time": self.task_timeout,
                        "model": "unknown"
                    })
        
        # Sort results by agent_id for consistent output
        agent_results.sort(key=lambda x: x["agent_id"])
        
        # Aggregate results
        final_result = self.aggregate_results(agent_results)
        
        # Print usage summary after orchestration
        if not self.silent:
            rate_limits = self.config['google_ai_studio']['models']['rate_limits']
            self.usage_tracker.print_usage_summary(rate_limits)
        
        return final_result