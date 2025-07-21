import json
import os
import yaml
import time
import threading
import google.generativeai as genai
from tools import discover_tools
from usage_tracker import UsageTracker

class RateLimiter:
    """Thread-safe rate limiter for API calls"""
    def __init__(self, delay_seconds: float):
        self.delay_seconds = delay_seconds
        self.last_call_time = 0
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits"""
        with self.lock:
            current_time = time.time()
            time_since_last_call = current_time - self.last_call_time
            
            if time_since_last_call < self.delay_seconds:
                sleep_time = self.delay_seconds - time_since_last_call
                time.sleep(sleep_time)
            
            self.last_call_time = time.time()

class OpenRouterAgent:
    def __init__(self, config_path="config.yaml", silent=False, model: str = None):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Silent mode for orchestrator (suppresses debug output)
        self.silent = silent
        
        # Resolve API key from environment variable
        api_key = self.config['google_ai_studio']['api_key']
        if api_key.startswith('${') and api_key.endswith('}'):
            env_var = api_key[2:-1]
            api_key = os.getenv(env_var)
            if not api_key:
                raise ValueError(f"Environment variable {env_var} not found.")
        
        # Configure Google Generative AI
        genai.configure(api_key=api_key)
        
        # Set model for this agent instance
        if model:
            self.model_name = model
        else:
            self.model_name = self.config['google_ai_studio']['models']['heavy_duty_model']
        
        # Initialize rate limiter for this model
        rate_limits = self.config['google_ai_studio']['models'].get('rate_limits', {})
        model_limits = rate_limits.get(self.model_name, {'delay': 0.1})
        self.rate_limiter = RateLimiter(model_limits['delay'])
        
        # Initialize usage tracker
        self.usage_tracker = UsageTracker()
        self.model_limits = model_limits
        
        if not self.silent:
            rpm_limit = model_limits.get('rpm', 'unknown')
            delay = model_limits['delay']
            print(f"Agent initialized with model: {self.model_name} (RPM limit: {rpm_limit}, delay: {delay}s)")

        # Discover tools dynamically
        self.discovered_tools = discover_tools(self.config, silent=self.silent)
        
        # Build Gemini tools using simple format
        self.function_declarations = [tool.to_gemini_schema() for tool in self.discovered_tools.values()]
        self.tools = self.function_declarations
        
        # Build tool mapping for execution
        self.tool_mapping = {name: tool.execute for name, tool in self.discovered_tools.items()}
        
        # Configure generation parameters for deeper thinking
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,  # Balanced creativity and consistency
            top_p=0.95,       # High diversity in token selection
            top_k=40,         # Moderate vocabulary restriction
            max_output_tokens=8192,  # Allow longer, more detailed responses
            candidate_count=1
        )
        
        # Initialize model with tools and enhanced generation config
        self.model = genai.GenerativeModel(
            self.model_name, 
            tools=self.tools,
            generation_config=generation_config
        )
    
    def run(self, user_input: str):
        """Run the agent with user input using Gemini's chat interface"""
        max_iterations = self.config.get('agent', {}).get('max_iterations', 10)
        iteration = 0
        
        # Start a chat session
        chat = self.model.start_chat()
        full_response_content = []
        
        while iteration < max_iterations:
            iteration += 1
            if not self.silent:
                print(f"Agent iteration {iteration}/{max_iterations} (Model: {self.model_name})")
            
            # Apply rate limiting
            self.rate_limiter.wait_if_needed()
            
            # Record API usage
            self.usage_tracker.record_request(self.model_name, "generate")
            
            try:
                # Send message to chat with enhanced prompting for depth
                if iteration == 1:
                    # Enhanced first message for deeper analysis
                    enhanced_prompt = f"""
{user_input}

INSTRUCCIONES ADICIONALES PARA RESPUESTA PROFUNDA:
- Piensa paso a paso antes de responder
- Realiza investigacion exhaustiva usando todas las herramientas disponibles
- Proporciona analisis detallado y completo
- Responde EXCLUSIVAMENTE en ESPANOL CASTELLANO
- Estructura tu respuesta de manera logica y comprensible
"""
                    response = chat.send_message(enhanced_prompt)
                else:
                    # Continue with depth emphasis
                    continue_prompt = "Continua con la tarea. Asegurate de proporcionar analisis profundo y detallado en ESPANOL."
                    response = chat.send_message(continue_prompt)
                
                # Process response safely - avoid response.text when there are function calls
                response_text = None
                has_function_calls = False
                
                if response.candidates and response.candidates[0].content.parts:
                    # Check each part to extract text and detect function calls
                    text_parts = []
                    for part in response.candidates[0].content.parts:
                        try:
                            # Check for text content first
                            if hasattr(part, 'text') and part.text and part.text.strip():
                                text_parts.append(part.text.strip())
                            # Check for function calls
                            elif hasattr(part, 'function_call') and part.function_call:
                                has_function_calls = True
                                if not self.silent:
                                    print(f"Detected function call: {part.function_call.name}")
                        except AttributeError as e:
                            # Handle cases where part doesn't have expected attributes
                            if not self.silent:
                                print(f"Part attribute error: {str(e)}")
                            continue
                        except Exception as e:
                            if not self.silent:
                                print(f"Error processing part: {str(e)}")
                            continue
                    
                    if text_parts:
                        response_text = "\n".join(text_parts)
                
                if not self.silent:
                    print(f"Extracted text: {response_text[:100] if response_text else 'None'}...")
                    print(f"Has function calls: {has_function_calls}")
                
                if response_text:
                    full_response_content.append(response_text)
                    if not self.silent:
                        print(f"Added response: {response_text[:100]}...")
                
                # Handle function calls if detected
                if has_function_calls and response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        try:
                            if hasattr(part, 'function_call') and part.function_call:
                                func_call = part.function_call
                                if not self.silent:
                                    print(f"Calling tool: {func_call.name}")
                                
                                # Execute the function
                                if func_call.name in self.tool_mapping:
                                    try:
                                        # Convert args to dict if needed
                                        args = dict(func_call.args) if func_call.args else {}
                                        result = self.tool_mapping[func_call.name](**args)
                                        
                                        # Check if this was the completion tool
                                        if func_call.name == "mark_task_complete":
                                            if not self.silent:
                                                print("Task completion tool called - exiting")
                                            return "\n\n".join(full_response_content)
                                        
                                        # Send function result back to chat as simple text
                                        result_text = f"Function {func_call.name} returned: {json.dumps(result)}"
                                        continue_response = chat.send_message(result_text)
                                        
                                        # Process the continuation response safely
                                        if continue_response.candidates and continue_response.candidates[0].content.parts:
                                            continue_text_parts = []
                                            for continue_part in continue_response.candidates[0].content.parts:
                                                try:
                                                    if hasattr(continue_part, 'text') and continue_part.text and continue_part.text.strip():
                                                        continue_text_parts.append(continue_part.text.strip())
                                                except AttributeError as e:
                                                    if not self.silent:
                                                        print(f"Continue part attribute error: {str(e)}")
                                                    continue
                                                except Exception as e:
                                                    if not self.silent:
                                                        print(f"Error processing continuation part: {str(e)}")
                                                    continue
                                            
                                            if continue_text_parts:
                                                continue_text = "\n".join(continue_text_parts)
                                                full_response_content.append(continue_text)
                                            
                                    except Exception as e:
                                        if not self.silent:
                                            print(f"Tool execution error: {str(e)}")
                                else:
                                    if not self.silent:
                                        print(f"Unknown tool: {func_call.name}")
                        except AttributeError as e:
                            if not self.silent:
                                print(f"Function call attribute error: {str(e)}")
                            continue
                        except Exception as e:
                            if not self.silent:
                                print(f"Error processing function call: {str(e)}")
                            continue
                
                # Check if we should continue or break
                if not has_function_calls:
                    # If we have accumulated content, we're done
                    if full_response_content:
                        break
                    # If no content and no function calls, something went wrong
                    elif iteration > 1:
                        if not self.silent:
                            print("No content generated and no function calls - stopping")
                        break
                        
            except Exception as e:
                if not self.silent:
                    print(f"Error in iteration {iteration}: {str(e)}")
                break
        
        final_result = "\n\n".join(full_response_content) if full_response_content else "No response generated"
        if not self.silent:
            print(f"Final result length: {len(final_result)}")
            print(f"Full response content items: {len(full_response_content)}")
        return final_result