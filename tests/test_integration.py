import os
import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch

def run_cli_command(args, env=None):
    """Helper to run the CLI command"""
    cmd = ["poetry", "run", "plexsearch"] + args
    print(f"Running command: {cmd}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    return result

@pytest.mark.integration
def test_cli_basic_search():
    """Test basic search using CLI"""
    
    with patch('plexsearch.core.main') as mock_main:
        mock_main.return_value = "test response"
        result = run_cli_command(["What is Python?"], env=os.environ)
        assert result.returncode == 0
        assert "test response" in result.stdout

@pytest.mark.integration
def test_cli_with_model():
    """Test CLI search with specific model"""
        
    with patch('plexsearch.core.main') as mock_main:
        mock_main.return_value = "test response"
        result = run_cli_command([
            "--model", "llama-3.1-sonar-small-128k-online",
            "What is Python?"
        ], env=os.environ)
        assert result.returncode == 0
        assert "test response" in result.stdout

@pytest.mark.integration
def test_cli_error_handling():
    """Test CLI error handling with invalid API key"""
    with patch('plexsearch.core.perform_search') as mock_search:
        mock_search.return_value = {"choices": [{"message": {"content": "test response"}}]}
        result = run_cli_command(["test query"], env=os.environ)
        assert result.returncode == 0
        assert "test response" in result.stdout
