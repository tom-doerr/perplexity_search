import pytest
from plexsearch.config import Config
from unittest.mock import patch
import argparse

import pytest
from plexsearch.config import Config
from unittest.mock import patch
import argparse

def test_invalid_model():
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        query=None,
        api_key=None,
        model="invalid-model",
        no_stream=False,
        citations=False,
        log_file=None,
        markdown_file=None,
        debug=False
    )):
        with pytest.raises(ValueError) as exc_info:
            config = Config()
            _ = config.model
        assert "Invalid model: invalid-model" in str(exc_info.value)
