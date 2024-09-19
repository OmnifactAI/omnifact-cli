# tests/test_api.py

import pytest
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