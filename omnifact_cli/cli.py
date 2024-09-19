# omnifact_cli/cli.py

import click
from .api import OmnifactAPI
from .config import get_api_key, set_api_key, set_connect_url, get_connect_url

@click.group()
@click.pass_context
def cli(ctx):
    """Omnifact CLI for managing documents."""
    api_key = get_api_key()
    connect_url = get_connect_url()
    if not api_key:
        click.echo("API key not set. Use 'omnifact-cli config set-api-key' to set it.")
    else:
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
@click.option('--offset', default=0, help='Number of items to skip.')
@click.option('--limit', default=20, help='Maximum number of items to return.')
@click.pass_obj
def list_documents(api, space_id, offset, limit):
    """List documents in a space."""
    try:
        documents = api.get_documents(space_id, offset, limit)
        for doc in documents['items']:
            click.echo(f"ID: {doc['id']}, Name: {doc['name']}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.option('--space-id', required=True, help='ID of the space to upload the document to.')
@click.option('--file', required=True, type=click.Path(exists=True), help='Path to the file to upload.')
@click.option('--name', help='Name to give the document (optional).')
@click.pass_obj
def upload_document(api, space_id, file, name):
    """Upload a document to a space."""
    try:
        result = api.upload_document(space_id, file, name)
        click.echo(f"Document uploaded successfully. ID: {result['id']}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

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
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.argument('document_id')
@click.pass_obj
def delete_document(api, document_id):
    """Delete a specific document."""
    try:
        api.delete_document(document_id)
        click.echo(f"Document {document_id} deleted successfully.")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == '__main__':
    cli()