# Perplexity Search

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python tool for performing searches using the Perplexity API, optimized for retrieving accurate pricing information.

## Features

- Perform searches using different LLaMA models (small, large, huge)
- Configurable API key support via environment variable or direct input
- Customizable search queries with temperature and other parameters
- Command-line interface for easy usage
- Focused on retrieving precise pricing information

## Installation

```bash
git clone https://github.com/tom-doerr/perplexity_search.git
cd perplexity_search
pip install requests
```

## Usage

### As a Python Module

```python
from perplexity_search import perform_search

# Using environment variable for API key
result = perform_search("What is the price of Bitcoin?")

# Or passing API key directly
result = perform_search("What is the price of Bitcoin?", api_key="your-api-key")

# Specify a different model
result = perform_search("What is the price of Bitcoin?", model="llama-3.1-sonar-huge-128k-online")
```

### Command Line Interface

```bash
# Basic search
python perplexity_search.py "What is the price of Bitcoin?"

# Specify model
python perplexity_search.py --model huge "What is the price of Bitcoin?"

# Use specific API key
python perplexity_search.py --api-key your-api-key "What is the price of Bitcoin?"
```

## Configuration

### API Key

Set your Perplexity API key in one of two ways:
1. Environment variable: `export PERPLEXITY_API_KEY=your-api-key`
2. Pass directly in code or CLI: `--api-key your-api-key`

### Available Models

- small: llama-3.1-sonar-small-128k-online
- large: llama-3.1-sonar-large-128k-online
- huge: llama-3.1-sonar-huge-128k-online

## Requirements

- Python 3.x
- requests library
- Perplexity API key (obtain from [Perplexity API](https://docs.perplexity.ai/))

## Error Handling

The tool includes error handling for:
- Missing API keys
- Invalid API responses
- Network issues
- Invalid model selections

## License

MIT License - see the [LICENSE](LICENSE) file for details
