# omnifact_cli/cli.py

import sys
import click
from .api import OmnifactAPI
from .config import get_api_key, set_api_key, set_connect_url, get_connect_url

@click.group()
@click.pass_context
def cli(ctx):
    """Omnifact CLI for managing documents."""
    api_key = get_api_key()
    connect_url = get_connect_url()
    if ctx.invoked_subcommand not in ['config', 'help']:
        if not api_key:
            click.echo("Error: API key not set. Use 'omnifact-cli config set-api-key' to set it.", err=True)
            sys.exit(1)
        ctx.obj = OmnifactAPI(api_key, connect_url)

@cli.group()
def config():
    """Manage Omnifact CLI configuration."""
    pass

@config.command('set-api-key')
@click.argument('api_key')
def set_api_key_command(api_key):
    """Set the API key for Omnifact CLI."""
    set_api_key(api_key)
    click.echo("API key set successfully.")

@config.command('get-api-key')
def get_api_key_command():
    """Get the current API key."""
    api_key = get_api_key()
    if api_key:
        click.echo(f"Current API key: {api_key}")
    else:
        click.echo("API key is not set.")

@config.command('set-connect-url')
@click.argument('connect_url')
def set_connect_url_command(connect_url):
    """Set the Connect URL for Omnifact CLI."""
    set_connect_url(connect_url)
    click.echo("Connect URL set successfully.")

@config.command('get-connect-url')
def get_connect_url_command():
    """Get the current Connect URL."""
    connect_url = get_connect_url()
    click.echo(f"Current Connect URL: {connect_url}")

@cli.command()
@click.option('--space-id', required=True, help='ID of the space to list documents from.')
@click.pass_obj
def list_documents(api, space_id):
    """List all documents in a space."""
    try:
        all_documents = []
        offset = 0
        limit = 100

        # Fetch all documents in batches of 100
        while True:
            documents = api.get_documents(space_id, offset=offset, limit=limit)
            all_documents.extend(documents['items'])
            
            if len(documents['items']) < limit:
                break
            
            offset += limit
        for doc in all_documents:
            click.echo(f"ID: {doc['id']}, Name: {doc['name']}")
    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.option('--space-id', required=True, help='ID of the space to upload the document to.')
@click.option('--file', required=True, type=click.Path(exists=True), help='Path to the file to upload.')
@click.option('--name', help='Name to give the document (optional).')
@click.option('--metadata', help='Metadata for the document in JSON format (optional).')
@click.option('--encoding', help='File encoding (e.g., utf-8, windows-1252, ISO-8859-1). If not specified, encoding will be auto-detected.')
@click.pass_obj
def upload_document(api, space_id, file, name, metadata, encoding):
    """Upload a document to a space."""
    try:
        if metadata:
            try:
                import json
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                click.echo("Error: Invalid JSON format for metadata", err=True)
                return
        result = api.upload_document(space_id, file, name, metadata, encoding)
        click.echo(f"Document uploaded successfully. ID: {result['id']}")
    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.argument('document_id')
@click.pass_obj
def get_document(api, document_id):
    """Get details of a specific document."""
    try:
        document = api.get_document(document_id)
        click.echo(f"ID: {document['id']}")
        click.echo(f"Name: {document['name']}")
        click.echo(f"Status: {document['status']}")
        if 'metadata' in document:
            import json
            click.echo(f"Metadata: {json.dumps(document['metadata'], indent=2)}")
    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.argument('document_id')
@click.pass_obj
def delete_document(api, document_id):
    """Delete a specific document."""
    try:
        api.delete_document(document_id)
        click.echo(f"Document {document_id} deleted successfully.")
    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.argument('document_id')
@click.option('--name', required=True, help='New name for the document.')
@click.pass_obj
def rename_document(api, document_id, name):
    """Rename a specific document."""
    try:
        document = api.update_document(document_id, name)
        click.echo(f"Document renamed successfully to: {document['name']}")
    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.pass_obj
def list_supported_types(api):
    """List supported file types for document upload."""
    try:
        file_types = api.get_supported_file_types()
        click.echo("Supported file types:")
        for file_type in file_types:
            extensions = ", ".join(file_type['extensions'])
            click.echo(f"  {file_type['mimeType']}: {extensions}")
    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.option('--space-id', required=True, help='ID of the space to purge documents from.')
@click.pass_obj
def purge(api, space_id):
    """Purge all documents from a space."""
    try:
        all_documents = []
        offset = 0
        limit = 100

        # Fetch all documents in batches of 100
        while True:
            documents = api.get_documents(space_id, offset=offset, limit=limit)
            all_documents.extend(documents['items'])
            
            if len(documents['items']) < limit:
                break
            
            offset += limit

        if not all_documents:
            click.echo("No documents found in the specified space.")
            return

        # Display the documents to be deleted
        click.echo("The following documents will be deleted:")
        for doc in all_documents:
            click.echo(f"ID: {doc['id']}, Name: {doc['name']}")
        
        # Ask for confirmation
        if click.confirm("Are you sure you want to delete all these documents?"):
            # Delete each document
            for doc in all_documents:
                api.delete_document(doc['id'])
                click.echo(f"Deleted document: {doc['id']}")
            
            click.echo("All documents have been purged from the space.")
        else:
            click.echo("Operation cancelled.")
    except Exception as e:
        raise click.ClickException(str(e))

def _process_stream_response(response):
    """Process a streaming SSE response and yield content chunks.

    The SSE format is:
        event: <event_type>
        id: <id>
        <json_data>
        (blank line)

    Where json_data for assistant_write events is: {"messageId": "...", "content": "..."}
    """
    import json
    current_event = None

    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')

            # Parse SSE event type
            if line_str.startswith('event: '):
                current_event = line_str[7:].strip()
                continue

            # Skip id lines
            if line_str.startswith('id: '):
                continue

            # Skip data: prefix if present
            if line_str.startswith('data: '):
                line_str = line_str[6:]

            # Only process content from assistant_write events
            if current_event == 'assistant_write' and line_str:
                try:
                    data = json.loads(line_str)
                    if 'content' in data:
                        yield data['content']
                except json.JSONDecodeError:
                    # If not JSON, yield raw content
                    yield line_str

            # Stop on done event
            if current_event == 'done':
                break


@cli.command()
@click.option('--endpoint-id', required=True, help='ID of the chat endpoint.')
@click.option('--interactive', '-i', is_flag=True, help='Start an interactive chat session.')
@click.argument('message', required=False)
@click.pass_obj
def chat(api, endpoint_id, interactive, message):
    """Chat with an AI assistant.

    In single-question mode, provide a MESSAGE argument:
        omnifact-cli chat --endpoint-id <id> "Your question here"

    In interactive mode, use the -i flag:
        omnifact-cli chat --endpoint-id <id> -i
    """
    try:
        if interactive:
            _run_interactive_chat(api, endpoint_id)
        else:
            if not message:
                raise click.ClickException("Message is required in non-interactive mode. Use -i for interactive mode.")
            _run_single_chat(api, endpoint_id, message)
    except KeyboardInterrupt:
        click.echo("\nChat ended.")
    except Exception as e:
        raise click.ClickException(str(e))


def _run_single_chat(api, endpoint_id, message):
    """Send a single message and print the response."""
    response = api.chat(endpoint_id, message, stream=True)
    for chunk in _process_stream_response(response):
        click.echo(chunk, nl=False)
    click.echo()  # Final newline


def _run_interactive_chat(api, endpoint_id):
    """Run an interactive chat session with conversation history."""
    click.echo("Interactive chat started. Type 'exit' or 'quit' to end the session.")
    click.echo("-" * 50)

    history = []

    while True:
        try:
            user_input = click.prompt("You", prompt_suffix=": ")
        except click.exceptions.Abort:
            break

        if user_input.lower() in ('exit', 'quit'):
            click.echo("Goodbye!")
            break

        if not user_input.strip():
            continue

        # Send message with history
        click.echo("Assistant: ", nl=False)
        response = api.chat(endpoint_id, user_input, history=history, stream=True)

        # Collect the full response for history
        full_response = []
        for chunk in _process_stream_response(response):
            click.echo(chunk, nl=False)
            full_response.append(chunk)
        click.echo()  # Newline after response

        # Add to history
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": "".join(full_response)})


if __name__ == '__main__':
    cli()