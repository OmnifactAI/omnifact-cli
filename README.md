# Omnifact CLI

Omnifact CLI is a command-line interface tool for managing documents in the Omnifact platform.

The Omnifact API Spec can be found [here](https://connect.omnifact.ai/docs). For more information on Omnifact, please visit [omnifact.ai](https://omnifact.ai).

## Installation

To install Omnifact CLI, follow these steps:

1. Clone the repository:

```
git clone https://github.com/OmnifactAI/omnifact-cli.git
cd omnifact-cli
```

2. Create and activate a virtual environment:

```
python3 -m venv venv
source venv/bin/activate # On Windows, use venv\Scripts\activate
```

3. Install the package in editable mode:

```
pip install -e .
```

## Configuration

Before using the Omnifact CLI, you need to set your API key:

```
omnifact-cli config set-api-key YOUR_API_KEY
```

Optionally, set your Connect URL:

```
omnifact-cli config set-connect-url YOUR_CONNECT_URL
```

You can also use environment variables to set the API key and Connect URL. This is useful for scripts or CI/CD pipelines, when using the CLI in a non-interactive way or when you want to avoid storing the API key in the configuration file.

```bash
OMNIFACT_API_KEY=your_api_key OMNIFACT_CONNECT_URL=https://your-connect-url.com omnifact-cli list-documents --space-id YOUR_SPACE_ID
```

## Usage

Here are some example commands:

1. List documents in a space:

```
omnifact-cli list-documents --space-id YOUR_SPACE_ID
```

2. Upload a document:

```
omnifact-cli upload-document --space-id YOUR_SPACE_ID --file /path/to/your/document.pdf
# Optionally, you can set the name of the document and the metadata
omnifact-cli upload-document --space-id YOUR_SPACE_ID --file /path/to/your/document.pdf --name "Document Name" --metadata '{"url": "https://example.com/docs/document.pdf"}'
```

3. Get document details:

```
omnifact-cli get-document DOCUMENT_ID
```

4. Delete a document:

```
omnifact-cli delete-document DOCUMENT_ID
```

For more information on available commands, use:

```
omnifact-cli --help
```

## Development

To set up the development environment:

1. Install development dependencies:

```
pip install -r requirements.txt
```

2. Run tests:

```
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository.
