"""
Google Drive and Google Docs integration helper
"""

import os
import re
import pickle
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes for Google Drive and Docs
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/documents'
]


class GoogleDriveHelper:
    """Helper class for Google Drive and Docs operations"""

    def __init__(self):
        """Initialize Google Drive helper"""
        self.creds = None
        self.drive_service = None
        self.docs_service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive and Docs APIs"""
        token_path = Path('token.pickle')
        creds_path = Path('credentials.json')

        # Load existing credentials
        if token_path.exists():
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # Refresh or get new credentials
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    self.creds = None

            if not self.creds:
                if not creds_path.exists():
                    raise FileNotFoundError(
                        "credentials.json not found. Please download it from "
                        "https://console.cloud.google.com/ and place it in this directory."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(creds_path), SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save credentials
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        # Build services
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.docs_service = build('docs', 'v1', credentials=self.creds)

    def extract_file_id(self, url: str) -> Optional[str]:
        """Extract file ID from Google Drive/Docs URL"""
        # Handle various Google URL formats
        patterns = [
            r'/d/([a-zA-Z0-9-_]+)',  # /d/FILE_ID
            r'id=([a-zA-Z0-9-_]+)',   # id=FILE_ID
            r'/folders/([a-zA-Z0-9-_]+)',  # /folders/FOLDER_ID
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def read_doc(self, url: str) -> str:
        """Read content from a Google Doc"""
        try:
            file_id = self.extract_file_id(url)
            if not file_id:
                return ""

            # Get document
            document = self.docs_service.documents().get(documentId=file_id).execute()

            # Extract text content
            content = []
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for text_run in element['paragraph'].get('elements', []):
                        if 'textRun' in text_run:
                            content.append(text_run['textRun']['content'])

            text = ''.join(content)
            print(f"✓ Successfully read {len(text)} characters from Google Doc")
            return text

        except HttpError as error:
            print(f"Error reading Google Doc: {error}")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""

    def read_file(self, url: str) -> str:
        """Read content from a Google Drive file (text or doc)"""
        try:
            file_id = self.extract_file_id(url)
            if not file_id:
                return ""

            # Get file metadata
            file_metadata = self.drive_service.files().get(
                fileId=file_id,
                fields='name,mimeType'
            ).execute()

            mime_type = file_metadata.get('mimeType', '')

            # If it's a Google Doc, use Docs API
            if mime_type == 'application/vnd.google-apps.document':
                return self.read_doc(url)

            # Otherwise, export as plain text
            request = self.drive_service.files().export_media(
                fileId=file_id,
                mimeType='text/plain'
            )
            content = request.execute().decode('utf-8')

            print(f"✓ Successfully read {len(content)} characters from Google Drive")
            return content

        except HttpError as error:
            print(f"Error reading Google Drive file: {error}")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""

    def create_doc(self, title: str, content: str, folder_id: Optional[str] = None) -> Optional[str]:
        """Create a new Google Doc with content and formatting

        Args:
            title: Title of the document
            content: Content to insert
            folder_id: Optional folder ID to place the document in
        """
        try:
            # Create document
            document = self.docs_service.documents().create(
                body={'title': title}
            ).execute()

            doc_id = document.get('documentId')

            # Parse content and build formatted requests
            requests = self._build_formatted_requests(content)

            # Apply all formatting in one batch
            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': requests}
                ).execute()

            # If folder_id specified, move the doc to that folder
            if folder_id:
                # Get the current parents
                file = self.drive_service.files().get(
                    fileId=doc_id,
                    fields='parents'
                ).execute()

                previous_parents = ",".join(file.get('parents', []))

                # Move the file to the new folder
                self.drive_service.files().update(
                    fileId=doc_id,
                    addParents=folder_id,
                    removeParents=previous_parents,
                    fields='id, parents'
                ).execute()

            url = f"https://docs.google.com/document/d/{doc_id}/edit"
            print(f"✓ Created Google Doc: {url}")
            return url

        except HttpError as error:
            print(f"Error creating Google Doc: {error}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _build_formatted_requests(self, content: str) -> list:
        """Build Google Docs API requests with formatting applied

        Analyzes content structure and applies appropriate styles:
        - First line as Title (if short)
        - Short lines (< 60 chars) as Headings
        - Regular paragraphs as Normal Text
        """
        requests = []
        lines = content.split('\n')

        # Track current position in document
        current_index = 1

        # Insert all text first
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        })

        # Now apply formatting (in reverse order to maintain indices)
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            line_length = len(line_stripped)

            # Skip empty lines
            if not line_stripped:
                current_index += len(line) + 1  # +1 for newline
                continue

            # Calculate start and end indices for this line
            start_index = current_index
            end_index = current_index + len(line)

            # Determine if this should be a heading
            is_first_line = (i == 0)
            is_heading = (
                line_length < 80 and
                line_length > 0 and
                not line_stripped.endswith('.') and
                not line_stripped.endswith(',') and
                (line_stripped[0].isupper() if line_stripped else False)
            )

            # Apply appropriate style
            if is_first_line and line_length < 100:
                # First line as Title
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': start_index,
                            'endIndex': end_index
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'TITLE',
                            'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 12, 'unit': 'PT'}
                        },
                        'fields': 'namedStyleType,spaceAbove,spaceBelow'
                    }
                })
            elif is_heading and line_length < 60:
                # Short lines as Heading 1
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': start_index,
                            'endIndex': end_index
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_1',
                            'spaceAbove': {'magnitude': 12, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 6, 'unit': 'PT'}
                        },
                        'fields': 'namedStyleType,spaceAbove,spaceBelow'
                    }
                })
            elif is_heading and line_length < 80:
                # Medium short lines as Heading 2
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': start_index,
                            'endIndex': end_index
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_2',
                            'spaceAbove': {'magnitude': 10, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 4, 'unit': 'PT'}
                        },
                        'fields': 'namedStyleType,spaceAbove,spaceBelow'
                    }
                })

            # Move to next line
            current_index = end_index + 1  # +1 for newline

        return requests

    def upload_to_folder(self, folder_url: str, filename: str, content: str) -> Optional[str]:
        """Upload a file to a Google Drive folder"""
        try:
            folder_id = self.extract_file_id(folder_url)
            if not folder_id:
                print("Could not extract folder ID from URL")
                return None

            # Create file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }

            # Create file
            from googleapiclient.http import MediaInMemoryUpload
            media = MediaInMemoryUpload(
                content.encode('utf-8'),
                mimetype='text/plain',
                resumable=True
            )

            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()

            url = file.get('webViewLink')
            print(f"✓ Uploaded to Google Drive: {url}")
            return url

        except HttpError as error:
            print(f"Error uploading to Google Drive: {error}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
