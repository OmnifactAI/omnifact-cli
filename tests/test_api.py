# tests/test_api.py

import pytest
import requests
from unittest.mock import patch, Mock
from omnifact_cli.api import OmnifactAPI

@pytest.fixture
def api():
    return OmnifactAPI("test_api_key")

def test_get_documents(api):
    with patch('requests.Session.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {"id": "doc1", "name": "Document 1"},
                {"id": "doc2", "name": "Document 2"}
            ],
            "total": 2,
            "limit": 20,
            "offset": 0
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = api.get_documents("space1")

        assert len(result["items"]) == 2
        assert result["items"][0]["name"] == "Document 1"
        mock_get.assert_called_once_with(
            "https://connect.omnifact.ai/v1/documents",
            params={"spaceId": "space1", "offset": 0, "limit": 20}
        )

def test_upload_document(api):
    with patch('requests.Session.post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"id": "new_doc", "name": "test.pdf"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with patch('builtins.open', Mock()):
            result = api.upload_document("space1", "test.pdf", name="Test Document")

        assert result["id"] == "new_doc"
        assert result["name"] == "test.pdf"
        mock_post.assert_called_once()

def test_upload_document_with_encoding(api):
    with patch('requests.Session.post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"id": "new_doc", "name": "test.txt"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with patch('builtins.open', Mock()):
            result = api.upload_document("space1", "test.txt", name="Test Document", encoding="windows-1252")

        assert result["id"] == "new_doc"
        assert result["name"] == "test.txt"

        # Verify the encoding header was set
        call_args = mock_post.call_args
        assert call_args[1]['headers']['Content-Transfer-Encoding'] == "windows-1252"
        mock_post.assert_called_once()

def test_upload_document_from_memory(api):
    with patch('requests.Session.post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"id": "new_doc", "name": "test.txt"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        file_data = b"Test file content"
        result = api.upload_document_from_memory(
            "space1",
            file_data,
            "test.txt",
            content_type="text/plain",
            name="Test Document",
            metadata={"key": "value"}
        )

        assert result["id"] == "new_doc"
        assert result["name"] == "test.txt"
        mock_post.assert_called_once()

        # Verify the call was made with correct parameters
        call_args = mock_post.call_args
        assert call_args[1]['params'] == {"spaceId": "space1"}
        assert 'file' in call_args[1]['files']
        assert call_args[1]['data']['name'] == "Test Document"

def test_get_document(api):
    with patch('requests.Session.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {"id": "doc1", "name": "Document 1", "status": "ready"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = api.get_document("doc1")

        assert result["id"] == "doc1"
        assert result["name"] == "Document 1"
        assert result["status"] == "ready"
        mock_get.assert_called_once_with("https://connect.omnifact.ai/v1/documents/doc1")

def test_delete_document(api):
    with patch('requests.Session.delete') as mock_delete:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response

        result = api.delete_document("doc1")

        assert result is None
        mock_delete.assert_called_once_with("https://connect.omnifact.ai/v1/documents/doc1")

def test_update_document(api):
    with patch('requests.Session.patch') as mock_patch:
        mock_response = Mock()
        mock_response.json.return_value = {"id": "doc1", "name": "renamed-document.pdf", "status": "ready"}
        mock_response.raise_for_status.return_value = None
        mock_patch.return_value = mock_response

        result = api.update_document("doc1", "renamed-document.pdf")

        assert result["id"] == "doc1"
        assert result["name"] == "renamed-document.pdf"
        mock_patch.assert_called_once_with(
            "https://connect.omnifact.ai/v1/documents/doc1",
            json={"name": "renamed-document.pdf"}
        )

def test_get_supported_file_types(api):
    with patch('requests.Session.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = [
            {"mimeType": "application/pdf", "extensions": ["pdf"]},
            {"mimeType": "text/plain", "extensions": ["txt"]}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = api.get_supported_file_types()

        assert len(result) == 2
        assert result[0]["mimeType"] == "application/pdf"
        assert result[1]["mimeType"] == "text/plain"
        mock_get.assert_called_once_with("https://connect.omnifact.ai/v1/documents/supported-file-types")

def test_upload_document_http_error(api):
    """Test upload_document handles HTTP errors properly."""
    with patch('requests.Session.post') as mock_post:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")
        mock_response.text = '{"error": "Invalid file"}'
        mock_post.return_value = mock_response

        with patch('builtins.open', Mock()):
            with pytest.raises(requests.exceptions.HTTPError):
                api.upload_document("space1", "test.pdf")

def test_upload_document_from_memory_http_error(api):
    """Test upload_document_from_memory handles HTTP errors properly."""
    with patch('requests.Session.post') as mock_post:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")
        mock_response.text = '{"error": "Invalid file"}'
        mock_post.return_value = mock_response

        file_data = b"Test file content"
        with pytest.raises(requests.exceptions.HTTPError):
            api.upload_document_from_memory("space1", file_data, "test.txt")

def test_update_document_http_error(api):
    """Test update_document handles HTTP errors properly."""
    with patch('requests.Session.patch') as mock_patch:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_response.text = '{"error": "Document not found"}'
        mock_patch.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            api.update_document("doc1", "new-name.pdf")