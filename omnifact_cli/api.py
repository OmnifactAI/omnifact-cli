# omnifact_cli/api.py

import requests
import json

class OmnifactAPI:
    def __init__(self, api_key, base_url="https://connect.omnifact.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": self.api_key})

    def get_documents(self, space_id, offset=0, limit=20):
        url = f"{self.base_url}/v1/documents"
        params = {"spaceId": space_id, "offset": offset, "limit": limit}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def upload_document(self, space_id, file_path, name=None, metadata=None):
        url = f"{self.base_url}/v1/documents"
        params = {"spaceId": space_id}
        files = {"file": open(file_path, "rb")}
        data = {}
        if name:
            data["name"] = name
        if metadata:
            data["metadata"] = json.dumps(metadata)  # Convert metadata to JSON string
        print(data)
        response = self.session.post(url, params=params, files=files, data=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Server response: {response.text}")
            raise
        return response.json()

    def get_document(self, document_id):
        url = f"{self.base_url}/v1/documents/{document_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def delete_document(self, document_id):
        url = f"{self.base_url}/v1/documents/{document_id}"
        response = self.session.delete(url)
        response.raise_for_status()
        return None