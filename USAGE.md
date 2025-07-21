# 📖 Usage Guide - Gemini Multi-Agent Heavy

## 🚀 Getting Started

### First Run
1. Set your Google AI Studio API key:
```bash
export GOOGLE_API_KEY=your_api_key_here
```

2. Start the interactive session:
```bash
python make_it_heavy.py
```

3. Enter your query when prompted:
```
User: Analyze the impact of artificial intelligence on modern education
```

## 🎯 Query Examples

### Research & Analysis
```
Analyze the latest developments in renewable energy technology
Research the psychological effects of social media on teenagers
Compare different approaches to climate change mitigation
```

### Technical Topics
```
Explain quantum computing principles and current applications
Analyze the security implications of blockchain technology
Compare machine learning frameworks for natural language processing
```

### Creative & Strategic
```
Develop a comprehensive marketing strategy for a sustainable fashion brand
Create a detailed business plan for an AI-powered healthcare startup
Design an educational curriculum for digital literacy
```

## 📊 Understanding the Output

### Real-time Progress Display
```
GEMINI-2.0-FLASH HEAVY
● RUNNING • 5M23S

AGENT 01  ● ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
AGENT 02  ● ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
AGENT 03  ● ::::::::::····························································
AGENT 04  ● ○ ·······································································
```

**Status Indicators:**
- `○` - Queued
- `◐` - Initializing
- `●` - Active/Processing
- `:::` - Progress bars
- `✗` - Failed/Error

### Final Results Structure
The system provides:
1. **Comprehensive Analysis** - Combined insights from all agents
2. **Multiple Perspectives** - Different angles on the same topic
3. **Detailed Research** - In-depth information gathering
4. **Structured Output** - Organized and readable format

## ⚙️ Advanced Configuration

### Adjusting Agent Count
Edit `config.yaml`:
```yaml
orchestrator:
  parallel_agents: 2  # Reduce for quota conservation
  # or
  parallel_agents: 4  # Maximum for comprehensive analysis
```

### Model Priority Customization
```yaml
worker_models:
  - "gemini-2.0-flash-lite"    # Fastest, highest quota
  - "gemini-2.0-flash"         # Good balance
  - "gemini-2.5-flash-lite-preview-06-17"
  - "gemini-2.5-flash"         # Fallback
```

### Timeout Adjustment
```yaml
orchestrator:
  task_timeout: 1200  # 20 minutes (default)
  # Increase for complex queries:
  task_timeout: 1800  # 30 minutes
```

## 🔧 Quota Management

### Understanding Free Tier Limits
| Model | RPM | Daily | Best For |
|-------|-----|-------|----------|
| `gemini-2.0-flash-lite` | 30 | 1500 | Quick analysis |
| `gemini-2.0-flash` | 15 | 1500 | Balanced tasks |
| `gemini-2.5-flash-lite-preview` | 15 | 500 | Preview features |
| `gemini-2.5-flash` | 10 | 500 | Complex reasoning |

### Quota Exhaustion Handling
When you see:
```
429 You exceeded your current quota
```

**Solutions:**
1. **Wait for reset** - Quotas reset every minute/day
2. **Switch models** - System automatically tries other models
3. **Reduce agents** - Lower `parallel_agents` in config
4. **Spread usage** - Use throughout the day instead of bursts

### Usage Monitoring
After each run, check the usage summary:
```
📊 RESUMEN DE USO DE MODELOS - CAPA GRATUITA
🤖 gemini-2.0-flash-lite: 15 requests
🤖 gemini-2.0-flash: 8 requests
```

## 🛠️ Tool Usage

### Available Tools
The system automatically uses these tools when needed:

#### Web Search
```python
# Automatically triggered for research queries
search_web(query="latest AI developments", max_results=6)
```

#### File Operations
```python
# Create analysis reports
write_file(path="analysis_report.md", content="...")

# Read existing data
read_file(path="data.txt", head=100)
```

#### Calculations
```python
# Mathematical analysis
calculate(expression="(1500 * 0.8) / 30")  # Quota calculations
```

#### Task Completion
```python
# Signals when analysis is complete
mark_task_complete(
    task_summary="Completed AI impact analysis",
    completion_message="Analysis saved to ai_impact_report.md"
)
```

## 🎯 Best Practices

### Query Optimization
1. **Be Specific**: "Analyze renewable energy in Europe 2024" vs "Tell me about energy"
2. **Set Context**: "For a university research paper, analyze..."
3. **Define Scope**: "Focus on economic impacts of..."

### Quota Conservation
1. **Batch Related Queries**: Group similar questions
2. **Use Off-Peak Hours**: Spread usage throughout the day
3. **Monitor Progress**: Watch for quota warnings
4. **Adjust Agent Count**: Reduce for simple queries

### Output Management
1. **Save Important Results**: Copy outputs to files
2. **Review Tool-Generated Files**: Check for auto-created reports
3. **Track Usage**: Monitor daily consumption

## 🚨 Troubleshooting

### Common Issues

#### "No response generated"
**Cause**: All models hit quota limits
**Solution**: Wait 1 hour or reduce agent count

#### "Task failed. Please try again."
**Cause**: Network issues or API problems
**Solution**: Check internet connection and retry

#### Slow Performance
**Cause**: Rate limiting or high load
**Solution**: Reduce `parallel_agents` or increase delays

#### Empty Results
**Cause**: Query too vague or API errors
**Solution**: Be more specific in your query

### Performance Tips
1. **Start Small**: Begin with 2 agents for testing
2. **Monitor Timing**: Note which models are fastest
3. **Use Appropriate Models**: Match model to task complexity
4. **Cache Results**: Save outputs to avoid re-processing

## 📈 Optimization Strategies

### For Speed
```yaml
parallel_agents: 2
worker_models:
  - "gemini-2.0-flash-lite"
  - "gemini-2.0-flash"
```

### For Comprehensiveness
```yaml
parallel_agents: 4
task_timeout: 1800
worker_models:
  - "gemini-2.0-flash-lite"
  - "gemini-2.0-flash"
  - "gemini-2.5-flash-lite-preview-06-17"
  - "gemini-2.5-flash"
```

### For Quota Conservation
```yaml
parallel_agents: 1
rate_limits:
  "gemini-2.0-flash-lite":
    delay: 5.0  # Slower but safer
```

---

**Happy analyzing! 🚀**