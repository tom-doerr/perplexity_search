import os
import pytest
from plexsearch.core import perform_search

@pytest.mark.integration
def test_basic_search():
    """Test a basic search with the API"""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        pytest.skip("PERPLEXITY_API_KEY environment variable not set")
    
    result = perform_search("What is Python?", api_key=api_key)
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.integration
def test_search_with_model_selection():
    """Test search with different model selection"""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        pytest.skip("PERPLEXITY_API_KEY environment variable not set")
    
    result = perform_search(
        "What is Python?",
        api_key=api_key,
        model="llama-3.1-sonar-small-128k-online"
    )
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.integration
def test_error_handling():
    """Test error handling with invalid API key"""
    with pytest.raises(Exception):
        perform_search("test query", api_key="invalid_key")
