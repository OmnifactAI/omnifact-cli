# tests/test_config.py

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from omnifact_cli.config import get_api_key, get_connect_url, set_api_key, set_connect_url, CONFIG_FILE

@pytest.fixture
def temp_config_file(monkeypatch):
    """Create a temporary config file for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_config = Path(temp_dir) / '.omnifact_cli.ini'
        monkeypatch.setattr('omnifact_cli.config.CONFIG_FILE', temp_config)
        yield temp_config

@pytest.fixture
def clean_env(monkeypatch):
    """Ensure environment variables are not set."""
    monkeypatch.delenv('OMNIFACT_API_KEY', raising=False)
    monkeypatch.delenv('OMNIFACT_CONNECT_URL', raising=False)

def test_get_api_key_from_env(clean_env, monkeypatch):
    """Test getting API key from environment variable."""
    monkeypatch.setenv('OMNIFACT_API_KEY', 'test-env-key')
    assert get_api_key() == 'test-env-key'

def test_get_api_key_from_config_file(clean_env, temp_config_file):
    """Test getting API key from config file."""
    # Write a config file
    temp_config_file.write_text('[DEFAULT]\napi_key = test-file-key\n')

    assert get_api_key() == 'test-file-key'

def test_get_api_key_no_config(clean_env, temp_config_file):
    """Test getting API key when no config exists."""
    # temp_config_file exists but is empty in fixture, but we don't write to it
    assert get_api_key() is None

def test_get_api_key_env_takes_precedence(clean_env, temp_config_file, monkeypatch):
    """Test that environment variable takes precedence over config file."""
    # Write a config file
    temp_config_file.write_text('[DEFAULT]\napi_key = test-file-key\n')

    # Set environment variable
    monkeypatch.setenv('OMNIFACT_API_KEY', 'test-env-key')

    assert get_api_key() == 'test-env-key'

def test_get_connect_url_from_env(clean_env, monkeypatch):
    """Test getting connect URL from environment variable."""
    monkeypatch.setenv('OMNIFACT_CONNECT_URL', 'https://custom.url.com')
    assert get_connect_url() == 'https://custom.url.com'

def test_get_connect_url_from_config_file(clean_env, temp_config_file):
    """Test getting connect URL from config file."""
    # Write a config file
    temp_config_file.write_text('[DEFAULT]\nconnect_url = https://config.url.com\n')

    assert get_connect_url() == 'https://config.url.com'

def test_get_connect_url_default(clean_env, temp_config_file):
    """Test getting default connect URL when no config exists."""
    assert get_connect_url() == 'https://connect.omnifact.ai'

def test_get_connect_url_env_takes_precedence(clean_env, temp_config_file, monkeypatch):
    """Test that environment variable takes precedence over config file."""
    # Write a config file
    temp_config_file.write_text('[DEFAULT]\nconnect_url = https://config.url.com\n')

    # Set environment variable
    monkeypatch.setenv('OMNIFACT_CONNECT_URL', 'https://env.url.com')

    assert get_connect_url() == 'https://env.url.com'

def test_set_api_key_new_file(clean_env, temp_config_file):
    """Test setting API key in a new config file."""
    set_api_key('new-api-key')

    # Verify the key was written
    assert temp_config_file.exists()
    assert get_api_key() == 'new-api-key'

def test_set_api_key_existing_file(clean_env, temp_config_file):
    """Test setting API key in an existing config file."""
    # Create initial config
    temp_config_file.write_text('[DEFAULT]\napi_key = old-key\n')

    # Update the key
    set_api_key('updated-key')

    # Verify the key was updated
    assert get_api_key() == 'updated-key'

def test_set_connect_url_new_file(clean_env, temp_config_file):
    """Test setting connect URL in a new config file."""
    set_connect_url('https://new.url.com')

    # Verify the URL was written
    assert temp_config_file.exists()
    assert get_connect_url() == 'https://new.url.com'

def test_set_connect_url_existing_file(clean_env, temp_config_file):
    """Test setting connect URL in an existing config file."""
    # Create initial config
    temp_config_file.write_text('[DEFAULT]\nconnect_url = https://old.url.com\n')

    # Update the URL
    set_connect_url('https://updated.url.com')

    # Verify the URL was updated
    assert get_connect_url() == 'https://updated.url.com'

def test_set_api_key_preserves_connect_url(clean_env, temp_config_file):
    """Test that setting API key preserves existing connect URL."""
    # Set both values initially
    temp_config_file.write_text('[DEFAULT]\napi_key = initial-key\nconnect_url = https://initial.url.com\n')

    # Update only the API key
    set_api_key('new-key')

    # Verify both values
    assert get_api_key() == 'new-key'
    assert get_connect_url() == 'https://initial.url.com'

def test_set_connect_url_preserves_api_key(clean_env, temp_config_file):
    """Test that setting connect URL preserves existing API key."""
    # Set both values initially
    temp_config_file.write_text('[DEFAULT]\napi_key = initial-key\nconnect_url = https://initial.url.com\n')

    # Update only the connect URL
    set_connect_url('https://new.url.com')

    # Verify both values
    assert get_api_key() == 'initial-key'
    assert get_connect_url() == 'https://new.url.com'
