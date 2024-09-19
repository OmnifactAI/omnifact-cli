# tests/test_cli.py

import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock
from omnifact_cli.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

@patch('omnifact_cli.cli.get_api_key')
def test_list_documents(mock_get_api_key, runner):
    mock_get_api_key.return_value = "test_api_key"
    
    with patch('omnifact_cli.api.OmnifactAPI.get_documents') as mock_get_documents:
        mock_get_documents.return_value = {
            "items": [
                {"id": "doc1", "name": "Document 1"},
                {"id": "doc2", "name": "Document 2"}
            ],
            "total": 2,
            "limit": 20,
            "offset": 0
        }

        result = runner.invoke(cli, ['list-documents', '--space-id', 'space1'])

        assert result.exit_code == 0
        assert "ID: doc1, Name: Document 1" in result.output
        assert "ID: doc2, Name: Document 2" in result.output

@patch('omnifact_cli.cli.get_api_key')
def test_upload_document(mock_get_api_key, runner):
    mock_get_api_key.return_value = "test_api_key"
    
    with patch('omnifact_cli.api.OmnifactAPI.upload_document') as mock_upload_document:
        mock_upload_document.return_value = {"id": "new_doc", "name": "test.pdf"}

        with runner.isolated_filesystem():
            with open('test.pdf', 'wb') as f:
                f.write(b'Test PDF content')

            result = runner.invoke(cli, ['upload-document', '--space-id', 'space1', '--file', 'test.pdf'])

        assert result.exit_code == 0
        assert "Document uploaded successfully. ID: new_doc" in result.output

@patch('omnifact_cli.cli.get_api_key')
def test_get_document(mock_get_api_key, runner):
    mock_get_api_key.return_value = "test_api_key"
    
    with patch('omnifact_cli.api.OmnifactAPI.get_document') as mock_get_document:
        mock_get_document.return_value = {"id": "doc1", "name": "Document 1", "status": "ready"}

        result = runner.invoke(cli, ['get-document', 'doc1'])

        assert result.exit_code == 0
        assert "ID: doc1" in result.output
        assert "Name: Document 1" in result.output
        assert "Status: ready" in result.output

@patch('omnifact_cli.cli.get_api_key')
def test_delete_document(mock_get_api_key, runner):
    mock_get_api_key.return_value = "test_api_key"
    
    with patch('omnifact_cli.api.OmnifactAPI.delete_document') as mock_delete_document:
        mock_delete_document.return_value = None

        result = runner.invoke(cli, ['delete-document', 'doc1'])

        assert result.exit_code == 0
        assert "Document doc1 deleted successfully." in result.output