"""Tests for the update checker functionality."""
import os
import json
import time
import subprocess
from unittest.mock import patch, MagicMock
import pytest
from plexsearch.update_checker import (
    get_latest_version,
    check_for_update,
    UpdateChecker
)

def test_get_latest_version():
    """Test getting latest version from PyPI."""
    with patch('feedparser.parse') as mock_parse:
        mock_parse.return_value = MagicMock(
            entries=[MagicMock(title="plexsearch: 1.2.0")]
        )
        assert get_latest_version("plexsearch") == "1.2.0"

def test_get_latest_version_no_releases():
    """Test handling no releases."""
    with patch('feedparser.parse') as mock_parse:
        mock_parse.return_value = MagicMock(entries=[])
        assert get_latest_version("plexsearch") == "0.0.0"

def test_check_for_update():
    """Test version comparison."""
    assert check_for_update("1.0.0", "1.1.0") is True
    assert check_for_update("1.1.0", "1.0.0") is False
    assert check_for_update("1.0.0", "1.0.0") is False
    assert check_for_update("1.0.0", "invalid") is False

class TestUpdateChecker:
    """Tests for the UpdateChecker class."""
    
    @pytest.fixture
    def checker(self, tmp_path):
        """Create an UpdateChecker instance for testing."""
        checker = UpdateChecker("plexsearch", "1.0.0")
        checker.state_dir = str(tmp_path)
        checker.state_file = str(tmp_path / "update_state.json")
        return checker
        
    def test_load_state_new_file(self, checker):
        """Test loading state with no existing file."""
        state = checker.load_state()
        assert state == {"last_check": 0, "last_reminder": 0}
        
    def test_save_and_load_state(self, checker):
        """Test saving and loading state."""
        state = {"last_check": 123, "last_reminder": 456}
        checker.save_state(state)
        loaded = checker.load_state()
        assert loaded == state
        
    def test_check_and_notify_too_soon(self, checker):
        """Test checking too soon after last check."""
        state = {"last_check": time.time(), "last_reminder": 0}
        checker.save_state(state)
        assert checker.check_and_notify(interval_hours=24) is None

    def test_check_and_notify_update_available(self, checker):
        """Test checking when update is available."""
        state = {"last_check": 0, "last_reminder": 0}
        checker.save_state(state)

        with patch('plexsearch.update_checker.get_latest_version') as mock_get:
            mock_get.return_value = "1.1.0"
            assert checker.check_and_notify() == "1.1.0"

    def test_check_and_notify_no_update(self, checker):
        """Test checking when no update is available."""
        state = {"last_check": 0, "last_reminder": 0}
        checker.save_state(state)

        with patch('plexsearch.update_checker.get_latest_version') as mock_get:
            mock_get.return_value = "1.0.0"
            assert checker.check_and_notify() is None

    def test_check_and_notify_reminder_too_soon(self, checker):
        """Test reminder too soon after last reminder."""
        state = {"last_check": 0, "last_reminder": time.time()}
        checker.save_state(state)

        with patch('plexsearch.update_checker.get_latest_version') as mock_get:
            mock_get.return_value = "1.1.0"
            assert checker.check_and_notify(interval_hours=24, reminder_interval_hours=1) is None

    def test_check_and_notify_reminder_available(self, checker):
        """Test reminder when reminder interval has passed."""
        state = {"last_check": 0, "last_reminder": 0}
        checker.save_state(state)

        with patch('plexsearch.update_checker.get_latest_version') as mock_get:
            mock_get.return_value = "1.1.0"
            assert checker.check_and_notify(interval_hours=24, reminder_interval_hours=1) == "1.1.0"

    def test_update_package_success(self, checker):
        """Test successful package update."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Successfully installed plexsearch-0.1.6",
                stderr="",
                text=True
            )
            assert checker.update_package() is True

    def test_update_package_failure(self, checker):
        """Test failed package update."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, [], stderr="Test error")
            assert checker.update_package() is False

    def test_update_package_success_message(self, checker):
        """Test successful update with message."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Successfully installed plexsearch-0.1.6"
            )
            assert checker.update_package() is True

    def test_update_package_no_message(self, checker):
        """Test successful update with no message."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=""
            )
            assert checker.update_package() is True

    def test_update_continues_execution(self, checker, capsys):
        """Test that program continues after update."""
        from plexsearch.core import main

        with patch('sys.argv', ['plexsearch', 'test query']), \
             patch('plexsearch.core.perform_search') as mock_search, \
             patch('builtins.input', return_value='y'), \
             patch.object(UpdateChecker, 'check_and_notify', return_value='0.2.0'), \
             patch.object(UpdateChecker, 'update_package', return_value=True):

            mock_search.return_value = iter(['test response'])
            main()

            captured = capsys.readouterr()
            assert 'Successfully updated' in captured.out
            mock_search.assert_called_once()

            captured = capsys.readouterr()
            assert 'test response' in captured.out
