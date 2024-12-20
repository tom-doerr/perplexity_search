import pytest
from unittest.mock import patch, MagicMock
from plexsearch.core import clear_new_area, get_terminal_size
from plexsearch import core

def test_get_terminal_size():
    """Test terminal size detection"""
    with patch('shutil.get_terminal_size', return_value=(24, 80)):
        height, width = get_terminal_size()
        assert height == 24
        assert width == 80

def test_get_terminal_size_fallback():
    """Test terminal size fallback values"""
    with patch('shutil.get_terminal_size', side_effect=Exception):
        height, width = get_terminal_size()
        assert height == 24  # Default fallback
        assert width == 80   # Default fallback

def test_clear_new_area_output(mock_terminal):
    """Test that clear_new_area produces expected terminal output"""
    with patch('plexsearch.core.get_terminal_size', return_value=(10, 80)):
        clear_new_area()
        output = mock_terminal.getvalue()
        
        # Should see:
        # 1. Debug message about clearing
        # 2. Newlines to push content up
        assert "Clearing screen" in output.replace("\x1b[36m", "").replace("\x1b[0m", "")
        assert "\n" * 10 in output  # Check for newlines

def test_interactive_mode_clearing(mock_terminal):
    """Test terminal clearing in interactive mode"""
    with patch('builtins.input', side_effect=['test query', 'exit']), \
         patch('plexsearch.core.perform_search', return_value=['test response']), \
         patch('plexsearch.core.get_terminal_size', return_value=(10, 80)), \
         patch('sys.argv', ['plexsearch']):
        
        from plexsearch.core import main
        main()
        
        output = mock_terminal.getvalue()
        # Verify clearing happens between queries
        assert "Clearing screen" in output.replace("\x1b[36m", "").replace("\x1b[0m", "")
        assert "\n" * 10 in output

def test_no_stream_mode_clearing(mock_terminal):
    """Test terminal clearing in no-stream mode"""
    with patch('sys.argv', ['plexsearch', '--no-stream', 'test query']), \
         patch('plexsearch.core.perform_search', return_value=['test response']), \
         patch('plexsearch.core.get_terminal_size', return_value=(10, 80)), \
         patch('plexsearch.update_checker.UpdateChecker') as mock_checker, \
         patch("plexsearch.config.Config") as mock_config:
        
        mock_checker.return_value.check_and_notify.return_value = None
        mock_args = MagicMock()        
        mock_args.model = "llama-3.1-sonar-large-128k-online"
        mock_config.return_value.args = mock_args
        core.main()
        
        output = mock_terminal.getvalue()
        # Verify clearing happens before showing results
        assert "Clearing screen" in output.replace("\x1b[36m", "").replace("\x1b[0m", "")
        assert "\n" * 10 in output
