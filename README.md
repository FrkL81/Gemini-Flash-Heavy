# 🚀 Gemini Multi-Agent Heavy

A powerful multi-agent system optimized for Google AI Studio's free tier, delivering comprehensive analysis through intelligent agent orchestration. This project maximizes the potential of Gemini models by strategically utilizing multiple agents in parallel.

## 🌟 Features

- **🧠 Multi-Agent Intelligence**: Deploy up to 4 specialized agents simultaneously for maximum insight coverage
- **⚡ Smart Quota Management**: Optimized configuration to maximize Google AI Studio free tier usage
- **🎯 Dynamic Question Generation**: AI creates custom research questions tailored to each query
- **🔄 Intelligent Load Balancing**: Automatically prioritizes models with best available quotas
- **🛠️ Hot-Swappable Tools**: Automatically discovers and loads tools from the `tools/` directory
- **🎮 Real-time Progress**: Live visual feedback during multi-agent execution
- **📊 Usage Tracking**: Monitor API usage across all models

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google AI Studio API key (free tier)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd gemini-multi-agent-heavy
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up your API key:**
```bash
# Windows
set GOOGLE_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_API_KEY=your_api_key_here
```

4. **Run the system:**
```bash
python make_it_heavy.py
```

## 🎯 Optimized Configuration

This system is specifically optimized for Google AI Studio's free tier limits:

| Model | RPM Limit | Daily Limit | Optimization |
|-------|-----------|-------------|--------------|
| `gemini-2.0-flash-lite` | 30 | 1500 | **Primary** - Best performance |
| `gemini-2.0-flash` | 15 | 1500 | **Secondary** - High capacity |
| `gemini-2.5-flash-lite-preview` | 15 | 500 | **Tertiary** - Balanced |
| `gemini-2.5-flash` | 10 | 500 | **Fallback** - When others exhausted |

## 🛠️ Architecture

### Core Components

#### 1. Multi-Agent Orchestrator (`orchestrator.py`)
- **Dynamic Question Generation**: AI creates specialized questions for each agent
- **Parallel Execution**: Runs multiple agents simultaneously with quota awareness
- **Response Synthesis**: Combines all agent outputs into comprehensive results
- **Error Handling**: Graceful fallbacks when quotas are exceeded

#### 2. Intelligent Agent (`agent.py`)
- **Rate Limiting**: Respects Google AI Studio quotas automatically
- **Tool Integration**: Access to web search, file operations, and calculations
- **Spanish Language Support**: Optimized for Spanish language analysis
- **Usage Tracking**: Monitors API consumption across all models

#### 3. Tool System (`tools/`)
- **Auto-Discovery**: Automatically loads all tools from directory
- **Standardized Interface**: All tools inherit from `BaseTool`
- **Extensible**: Add new tools by dropping files in `tools/`

### Available Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `search_web` | Web search with DuckDuckGo | `query`, `max_results` |
| `calculate` | Safe mathematical calculations | `expression` |
| `read_file` | Read file contents | `path`, `head`, `tail` |
| `write_file` | Create/overwrite files | `path`, `content` |
| `mark_task_complete` | Signal task completion | `task_summary`, `completion_message` |

## 📊 Usage Examples

### Basic Usage
```bash
python make_it_heavy.py
```

### Example Queries
- "Analyze the latest developments in artificial intelligence"
- "Research sustainable energy solutions for urban environments"
- "Compare different machine learning frameworks"

## ⚙️ Configuration

The system automatically optimizes for free tier usage, but you can customize:

### Model Priority
Edit `config.yaml` to adjust model priorities:
```yaml
worker_models:
  - "gemini-2.0-flash-lite"    # Highest priority
  - "gemini-2.0-flash"         # Second priority
  - "gemini-2.5-flash-lite-preview-06-17"
  - "gemini-2.5-flash"         # Fallback
```

### Rate Limiting
Adjust rate limits based on your usage patterns:
```yaml
rate_limits:
  "gemini-2.0-flash-lite":
    rpm: 25      # Conservative limit
    daily: 1400  # Daily safety margin
    delay: 2.5   # Seconds between requests
```

## 🔧 Troubleshooting

### Common Issues

#### Quota Exceeded (429 Error)
```
429 You exceeded your current quota
```
**Solution**: Wait for quota reset or switch to different models

#### API Key Issues
```
TypeError: 'NoneType' object is not subscriptable
```
**Solution**: Ensure `GOOGLE_API_KEY` environment variable is set

#### Model Unavailable
```
Invalid model error
```
**Solution**: Check Google AI Studio for model availability

## 📈 Performance Optimization

### Free Tier Maximization
- **Model Rotation**: Automatically switches between models when quotas are reached
- **Smart Delays**: Optimized timing between requests to avoid rate limits
- **Parallel Processing**: Uses multiple models simultaneously for faster results
- **Usage Tracking**: Monitors consumption to prevent unexpected quota exhaustion

### Best Practices
1. **Monitor Usage**: Check the usage summary after each run
2. **Spread Workload**: Use different models throughout the day
3. **Batch Queries**: Group related questions for efficiency
4. **Cache Results**: Save important outputs to avoid re-processing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
```bash
git clone <repository-url>
cd gemini-multi-agent-heavy
pip install -r requirements.txt
```

### Adding New Tools
1. Create a new file in `tools/` directory
2. Inherit from `BaseTool`
3. Implement required methods
4. The system will auto-discover your tool

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project is inspired by and builds upon the original [Make It Heavy](https://github.com/Doriandarko/make-it-heavy) by [@Doriandarko](https://github.com/Doriandarko). 

**Key Adaptations:**
- Optimized for Google AI Studio instead of OpenRouter
- Enhanced quota management for free tier usage
- Improved multi-agent coordination
- Spanish language optimization
- Real-time progress monitoring

Special thanks to the original author for the foundational architecture and inspiration.

## 🔗 Related Projects

- [Original Make It Heavy](https://github.com/Doriandarko/make-it-heavy) - OpenRouter-based multi-agent system
- [Google AI Studio](https://ai.google.dev/aistudio) - Free access to Gemini models

---

**Made with ❤️ for the AI community**