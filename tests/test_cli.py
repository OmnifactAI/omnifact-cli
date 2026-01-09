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
        # Simulate pagination: first call returns 2 items, second call returns 0 (done)
        mock_get_documents.side_effect = [
            {
                "items": [
                    {"id": "doc1", "name": "Document 1"},
                    {"id": "doc2", "name": "Document 2"}
                ],
                "total": 2,
                "limit": 100,
                "offset": 0
            },
            {
                "items": [],
                "total": 2,
                "limit": 100,
                "offset": 100
            }
        ]

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
def test_upload_document_with_encoding(mock_get_api_key, runner):
    mock_get_api_key.return_value = "test_api_key"

    with patch('omnifact_cli.api.OmnifactAPI.upload_document') as mock_upload_document:
        mock_upload_document.return_value = {"id": "new_doc", "name": "test.txt"}

        with runner.isolated_filesystem():
            with open('test.txt', 'wb') as f:
                f.write(b'Test text content')

            result = runner.invoke(cli, ['upload-document', '--space-id', 'space1', '--file', 'test.txt', '--encoding', 'windows-1252'])

        assert result.exit_code == 0
        assert "Document uploaded successfully. ID: new_doc" in result.output
        # Verify the encoding parameter was passed to the API method
        mock_upload_document.assert_called_once_with('space1', 'test.txt', None, None, 'windows-1252')

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

@patch('omnifact_cli.cli.get_api_key')
def test_rename_document(mock_get_api_key, runner):
    mock_get_api_key.return_value = "test_api_key"

    with patch('omnifact_cli.api.OmnifactAPI.update_document') as mock_update_document:
        mock_update_document.return_value = {"id": "doc1", "name": "new-name.pdf", "status": "ready"}

        result = runner.invoke(cli, ['rename-document', 'doc1', '--name', 'new-name.pdf'])

        assert result.exit_code == 0
        assert "Document renamed successfully to: new-name.pdf" in result.output
        mock_update_document.assert_called_once_with('doc1', 'new-name.pdf')

@patch('omnifact_cli.cli.get_api_key')
def test_list_supported_types(mock_get_api_key, runner):
    mock_get_api_key.return_value = "test_api_key"

    with patch('omnifact_cli.api.OmnifactAPI.get_supported_file_types') as mock_get_types:
        mock_get_types.return_value = [
            {"mimeType": "application/pdf", "extensions": ["pdf"]},
            {"mimeType": "text/plain", "extensions": ["txt", "text"]}
        ]

        result = runner.invoke(cli, ['list-supported-types'])

        assert result.exit_code == 0
        assert "Supported file types:" in result.output
        assert "application/pdf: pdf" in result.output
        assert "text/plain: txt, text" in result.output

@patch('omnifact_cli.cli.get_api_key')
def test_purge_with_confirmation(mock_get_api_key, runner):
    mock_get_api_key.return_value = "test_api_key"

    with patch('omnifact_cli.api.OmnifactAPI.get_documents') as mock_get_documents:
        with patch('omnifact_cli.api.OmnifactAPI.delete_document') as mock_delete_document:
            # Simulate pagination: first call returns 2 items, second call returns empty
            mock_get_documents.side_effect = [
                {
                    "items": [
                        {"id": "doc1", "name": "Document 1"},
                        {"id": "doc2", "name": "Document 2"}
                    ],
                    "total": 2,
                    "limit": 100,
                    "offset": 0
                },
                {
                    "items": [],
                    "total": 2,
                    "limit": 100,
                    "offset": 100
                }
            ]
            mock_delete_document.return_value = None

            # Simulate user confirming the deletion
            result = runner.invoke(cli, ['purge', '--space-id', 'space1'], input='y\n')

            assert result.exit_code == 0
            assert "ID: doc1, Name: Document 1" in result.output
            assert "ID: doc2, Name: Document 2" in result.output
            assert "Deleted document: doc1" in result.output
            assert "Deleted document: doc2" in result.output
            assert "All documents have been purged from the space." in result.output
            assert mock_delete_document.call_count == 2

@patch('omnifact_cli.cli.get_api_key')
def test_purge_cancelled(mock_get_api_key, runner):
    mock_get_api_key.return_value = "test_api_key"

    with patch('omnifact_cli.api.OmnifactAPI.get_documents') as mock_get_documents:
        with patch('omnifact_cli.api.OmnifactAPI.delete_document') as mock_delete_document:
            # Simulate pagination
            mock_get_documents.side_effect = [
                {
                    "items": [
                        {"id": "doc1", "name": "Document 1"}
                    ],
                    "total": 1,
                    "limit": 100,
                    "offset": 0
                },
                {
                    "items": [],
                    "total": 1,
                    "limit": 100,
                    "offset": 100
                }
            ]

            # Simulate user cancelling the deletion
            result = runner.invoke(cli, ['purge', '--space-id', 'space1'], input='n\n')

            assert result.exit_code == 0
            assert "Operation cancelled." in result.output
            mock_delete_document.assert_not_called()

@patch('omnifact_cli.cli.get_api_key')
def test_purge_no_documents(mock_get_api_key, runner):
    mock_get_api_key.return_value = "test_api_key"

    with patch('omnifact_cli.api.OmnifactAPI.get_documents') as mock_get_documents:
        # Simulate no documents in space
        mock_get_documents.return_value = {
            "items": [],
            "total": 0,
            "limit": 100,
            "offset": 0
        }

        result = runner.invoke(cli, ['purge', '--space-id', 'space1'])

        assert result.exit_code == 0
        assert "No documents found in the specified space." in result.output


@patch('omnifact_cli.cli.get_api_key')
def test_chat_single_question(mock_get_api_key, runner):
    """Test chat command in single-question mode."""
    mock_get_api_key.return_value = "test_api_key"

    with patch('omnifact_cli.api.OmnifactAPI.chat') as mock_chat:
        mock_response = Mock()
        # Simulate SSE streaming response
        mock_response.iter_lines.return_value = [
            b'event: assistant_write',
            b'id: 1',
            b'{"messageId": "msg1", "content": "Hello, "}',
            b'event: assistant_write',
            b'id: 2',
            b'{"messageId": "msg1", "content": "how can I help?"}',
            b'event: done',
            b'id: 3',
        ]
        mock_chat.return_value = mock_response

        result = runner.invoke(cli, ['chat', '--endpoint-id', 'endpoint1', 'Hi there'])

        assert result.exit_code == 0
        assert "Hello, how can I help?" in result.output
        mock_chat.assert_called_once_with('endpoint1', 'Hi there', stream=True)


@patch('omnifact_cli.cli.get_api_key')
def test_chat_missing_message(mock_get_api_key, runner):
    """Test chat command fails when message is missing in non-interactive mode."""
    mock_get_api_key.return_value = "test_api_key"

    result = runner.invoke(cli, ['chat', '--endpoint-id', 'endpoint1'])

    assert result.exit_code != 0
    assert "Message is required in non-interactive mode" in result.output


@patch('omnifact_cli.cli.get_api_key')
def test_chat_interactive_mode(mock_get_api_key, runner):
    """Test chat command in interactive mode."""
    mock_get_api_key.return_value = "test_api_key"

    with patch('omnifact_cli.api.OmnifactAPI.chat') as mock_chat:
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'event: assistant_write',
            b'id: 1',
            b'{"messageId": "msg1", "content": "Hello!"}',
            b'event: done',
            b'id: 2',
        ]
        mock_chat.return_value = mock_response

        # Simulate user input: one message then exit
        result = runner.invoke(cli, ['chat', '--endpoint-id', 'endpoint1', '-i'], input='Hello\nexit\n')

        assert result.exit_code == 0
        assert "Interactive chat started" in result.output
        assert "Hello!" in result.output
        assert "Goodbye!" in result.output


@patch('omnifact_cli.cli.get_api_key')
def test_chat_interactive_mode_with_history(mock_get_api_key, runner):
    """Test that interactive mode maintains conversation history."""
    mock_get_api_key.return_value = "test_api_key"

    # Track history at each call
    captured_histories = []

    with patch('omnifact_cli.api.OmnifactAPI.chat') as mock_chat:
        def create_mock_response(endpoint_id, message, history=None, stream=True):
            # Capture a copy of history at call time
            captured_histories.append(list(history) if history else [])
            mock_response = Mock()
            content = "First response" if len(captured_histories) == 1 else "Second response"
            mock_response.iter_lines.return_value = iter([
                b'event: assistant_write',
                b'id: 1',
                f'{{"messageId": "msg1", "content": "{content}"}}'.encode(),
                b'event: done',
                b'id: 2',
            ])
            return mock_response

        mock_chat.side_effect = create_mock_response

        # Send two messages then exit
        result = runner.invoke(cli, ['chat', '--endpoint-id', 'endpoint1', '-i'], input='First\nSecond\nexit\n')

        assert result.exit_code == 0
        assert mock_chat.call_count == 2

        # First call should have no history
        assert captured_histories[0] == []

        # Second call should have history from first exchange
        assert len(captured_histories[1]) == 2
        assert captured_histories[1][0] == {"role": "user", "content": "First"}
        assert captured_histories[1][1] == {"role": "assistant", "content": "First response"}