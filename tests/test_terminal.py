import pytest
from unittest.mock import patch, MagicMock
from plexsearch.core import clear_new_area, get_terminal_size

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
    string_io, log_io = mock_terminal
    with patch('plexsearch.core.get_terminal_size', return_value=(10, 80)):
        clear_new_area()
        output = string_io.getvalue()
        
        # Should see:
        # 1. Debug message about clearing
        # 2. Newlines to push content up
        assert output.count('\n') >= 20
        assert "\n" * 10 in output  # Check for newlines

def test_interactive_mode_clearing(mock_terminal):
    """Test terminal clearing in interactive mode"""
    string_io, log_io = mock_terminal
    with patch('builtins.input', side_effect=['test query', 'exit']), \
         patch('plexsearch.core.perform_search', return_value=['test response']), \
         patch('plexsearch.core.get_terminal_size', return_value=(10, 80)), \
         patch('sys.argv', ['plexsearch']):
        
        from plexsearch.core import main
        main()
        
        output = string_io.getvalue()
        # Verify clearing happens between queries
        assert output.count('\n') >= 20
        assert "\n" * 10 in output

def test_no_stream_mode_clearing(mock_terminal):
    """Test terminal clearing in no-stream mode"""
    string_io, log_io = mock_terminal
    with patch('sys.argv', ['plexsearch', '--no-stream', 'test query']), \
         patch('plexsearch.core.perform_search', return_value=['test response']), \
         patch('plexsearch.core.get_terminal_size', return_value=(10, 80)), \
         patch('plexsearch.core.UpdateChecker') as mock_checker:
        
        mock_checker.return_value.check_and_notify.return_value = None
        from plexsearch.core import main
        main()
        
        output = string_io.getvalue()
        # Verify clearing happens before showing results
        assert output.count('\n') >= 20
        assert "\n" * 10 in output
