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

        Strips markdown syntax and applies appropriate Google Docs styles:
        - # Header -> TITLE
        - ## Header -> HEADING_1
        - ### Header -> HEADING_2
        - #### Header -> HEADING_3
        - **bold** and *italic* -> removed (plain text)
        - Regular paragraphs -> Normal Text
        """
        import re

        requests = []
        lines = content.split('\n')

        # First pass: strip markdown and track formatting
        cleaned_lines = []
        line_styles = []

        for i, line in enumerate(lines):
            original_line = line
            stripped = line.strip()

            # Detect markdown headers
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                cleaned_lines.append(text)

                # Map markdown levels to Google Docs styles
                if i == 0 or level == 1:
                    line_styles.append('TITLE')
                elif level == 2:
                    line_styles.append('HEADING_1')
                elif level == 3:
                    line_styles.append('HEADING_2')
                else:
                    line_styles.append('HEADING_3')
            else:
                # Remove markdown bold/italic
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped)  # **bold**
                text = re.sub(r'\*(.+?)\*', r'\1', text)  # *italic*
                text = re.sub(r'__(.+?)__', r'\1', text)  # __bold__
                text = re.sub(r'_(.+?)_', r'\1', text)  # _italic_

                cleaned_lines.append(text)
                line_styles.append('NORMAL')

        # Join cleaned content
        cleaned_content = '\n'.join(cleaned_lines)

        # Insert all text first
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': cleaned_content
            }
        })

        # Now apply formatting based on detected styles
        current_index = 1

        for i, (line, style) in enumerate(zip(cleaned_lines, line_styles)):
            if not line:  # Skip empty lines
                current_index += 1  # Just the newline
                continue

            start_index = current_index
            end_index = current_index + len(line)

            # Apply style based on what was detected
            if style == 'TITLE':
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
            elif style == 'HEADING_1':
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
            elif style == 'HEADING_2':
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
            elif style == 'HEADING_3':
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': start_index,
                            'endIndex': end_index
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_3',
                            'spaceAbove': {'magnitude': 8, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 4, 'unit': 'PT'}
                        },
                        'fields': 'namedStyleType,spaceAbove,spaceBelow'
                    }
                })

            # Move to next line (length of line + newline)
            current_index = end_index + 1

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
