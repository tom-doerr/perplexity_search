# 🔍 Perplexity Search

A powerful CLI tool for technical search powered by Perplexity's advanced language models.

> 📝 **Note:** If a model is offline or unavailable, the tool automatically falls back to DuckDuckGo search to ensure continuous operation.

## ✨ Features

- **Perplexity Models**
  - Fast, accurate responses
  - Support for code and documentation
  - Multiple model sizes
- **Flexible Access**
  - Direct Perplexity API
  - OpenRouter integration
  - DuckDuckGo fallback
  - Local Ollama support
- **Beautiful Interface**
  - Rich terminal UI
  - Markdown formatting
  - Progress indicators

## 🚀 Quick Start

1. Install:

```bash
pip install -r requirements.txt
pip install -e .
```

2. Set up `.env`:

```bash
# Required for Perplexity API (Recommended)
PERPLEXITY_API_KEY=your-key-here

# Alternative: OpenRouter API
OPENROUTER_API_KEY=your-key-here
```

> 💡 See `example.env` for detailed model configurations and additional options

## 📘 Using Perplexity Models

### Direct API Access (Recommended)

Get your API key from [Perplexity](https://www.perplexity.ai/)

Available models:
- `llama-3.1-sonar-small-128k-online` (Fast)
- `llama-3.1-sonar-large-128k-online` (Default)
- `llama-3.1-sonar-huge-128k-online` (Most capable)

```bash
# Basic search with default model
plexsearch "your question here"

# Choose specific model
plexsearch --model llama-3.1-sonar-huge-128k-online "your question"

# Filter results
plexsearch --result-type code "python async examples"
plexsearch --result-type docs "react server components"
```

### Via OpenRouter

Access Perplexity models through OpenRouter:

1. Get API key from [OpenRouter](https://openrouter.ai/)
2. Use Perplexity models:

```bash
plexsearch --model perplexity/llama-3.1-sonar-huge-128k-online "your question"
```

### Local Ollama Support

Run queries using your local Ollama models:

```bash
# Use any installed Ollama model
plexsearch --model ollama:codellama "explain async/await"
plexsearch --model ollama:mistral "python design patterns"
```

## 🔧 Configuration

### Command Line Options

```bash
--model        Choose model to use
--result-type  "code", "docs", or "mixed" (default)
--api-key      Override API key from .env
--no-stream    Disable streaming output
```

### Note on Free Models

For users without API access, some free models are available through OpenRouter:
- `gryphe/mythomist-7b`
- `mistralai/mistral-7b`

```bash
plexsearch --model gryphe/mythomist-7b "your question"
```

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details
