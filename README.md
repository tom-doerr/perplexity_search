# Perplexity Search

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub stars](https://img.shields.io/github/stars/tom-doerr/perplexity_search?style=social)](https://github.com/tom-doerr/perplexity_search)

A Python tool for performing technical searches using the Perplexity API, optimized for retrieving precise facts, code examples, and numerical data.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [As a Python Module](#as-a-python-module)
  - [Command Line Interface](#command-line-interface)
- [Configuration](#configuration)
  - [API Key](#api-key)
  - [Available Models](#available-models)
- [Requirements](#requirements)
- [Error Handling](#error-handling)
- [License](#license)

## Features

- Perform searches using different LLaMA models (small, large, huge)
- Configurable API key support via environment variable or direct input
- Customizable search queries with temperature and other parameters
- Command-line interface for easy usage
- Focused on retrieving technical information with code examples
- Returns responses formatted in markdown
- Optimized for factual and numerical data

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
result = perform_search("What is Python's time complexity for list operations?")

# Or passing API key directly
result = perform_search("What are the differences between Python 3.11 and 3.12?", api_key="your-api-key")

# Specify a different model
result = perform_search("Show me example code for Python async/await", model="llama-3.1-sonar-huge-128k-online")
```

### Command Line Interface

```bash
# Basic search
python perplexity_search.py "What is Python's time complexity for list operations?"

# Specify model
python perplexity_search.py --model huge "What are the differences between Python 3.11 and 3.12?"

# Use specific API key
python perplexity_search.py --api-key your-api-key "Show me example code for Python async/await"
```

## Configuration

### API Key

Set your Perplexity API key in one of these ways:
1. Environment variable: 
   ```bash
   export PERPLEXITY_API_KEY=your-api-key
   # Or add to your ~/.bashrc or ~/.zshrc for persistence
   echo 'export PERPLEXITY_API_KEY=your-api-key' >> ~/.bashrc
   ```
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
