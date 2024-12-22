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
        with patch('plexsearch.update_checker.get_latest_version') as mock_get, \
             patch('time.time', return_value=time.time() + 3600/2):
            mock_get.return_value = "1.1.0"
            assert checker.check_and_notify(interval_hours=1) is None

    def test_check_and_notify_reminder_available(self, checker):
        """Test reminder when reminder interval has passed."""
        state = {"last_check": 0, "last_reminder": 0}
        checker.save_state(state)
        with patch('plexsearch.update_checker.get_latest_version') as mock_get, \
             patch('time.time', return_value=time.time() + 3600*2):
            mock_get.return_value = "1.1.0"
            assert checker.check_and_notify(interval_hours=1) == "1.1.0"

    def test_update_package_success(self, checker):
        """Test successful package update."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout="Successfully installed plexsearch-0.1.6",
                stderr="",
                text=True,
                returncode=0
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
                stdout="Successfully installed plexsearch-0.1.6"
            )
            assert checker.update_package() is True

    def test_update_package_no_message_no_change(self, checker):
        """Test successful update with no message and no change."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Successfully installed plexsearch-0.1.6",
                stderr=""
            )
            assert checker.update_package() is True

    def test_update_package_with_stderr(self, checker):
        """Test successful update with stderr."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Successfully installed plexsearch-0.1.6",
                stderr="Some stderr output"
            )
            assert checker.update_package() is True

    def test_check_and_notify_exact_interval(self):
        checker = UpdateChecker("plexsearch", "1.0.0")
        with patch('time.time', return_value=1000):
            with patch('plexsearch.update_checker.get_latest_version', return_value="1.1.0"), \
                 patch('plexsearch.update_checker.check_for_update', return_value=True):
                state = {"last_check": 0, "last_reminder": 0}
                with patch.object(checker, 'load_state', return_value=state), \
                     patch.object(checker, 'save_state') as mock_save_state:
                    latest_version = checker.check_and_notify(interval_hours=0.27778)  # approx 16.6667 minutes
                    assert latest_version == "1.1.0"
                    mock_save_state.assert_called_once()

    def test_update_package_with_non_zero_returncode(self, checker):
        """Test failed package update with non-zero return code."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=2,
                stdout="Some output",
                stderr="Some error"
            )
            assert checker.update_package() is False
def test_check_and_notify_exact_interval():
    checker = UpdateChecker("plexsearch", "1.0.0")
    with patch('time.time', return_value=1000.1):
        with patch('plexsearch.update_checker.get_latest_version', return_value="1.1.0"):
            state = {"last_check": 0, "last_reminder": 0}
            with patch.object(checker, 'load_state', return_value=state), \
                 patch.object(checker, 'save_state') as mock_save_state:
                latest_version = checker.check_and_notify(interval_hours=0.27778)  # approx 16.6667 hours
                assert latest_version == "1.1.0"
                mock_save_state.assert_called_once()
