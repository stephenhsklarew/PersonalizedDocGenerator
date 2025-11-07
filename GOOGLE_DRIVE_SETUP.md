# Google Drive & Docs Integration Setup

This guide will help you set up Google Drive and Google Docs integration for the PersonalDocGenerator.

## Overview

With Google Drive integration, you can:
- Read writing style and topic content from Google Docs
- Read files from Google Drive
- Save generated documents directly to Google Docs
- Upload generated files to specific Google Drive folders

## Prerequisites

- A Google Account
- Access to Google Cloud Console
- Python with google-api-python-client installed (included in requirements.txt)

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "PersonalDocGenerator")
4. Click "Create"

### 2. Enable Required APIs

1. In your project, go to "APIs & Services" → "Library"
2. Search for and enable these APIs:
   - **Google Drive API**
   - **Google Docs API**

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" (unless you have a Google Workspace)
   - Fill in the required fields:
     - App name: PersonalDocGenerator
     - User support email: your email
     - Developer contact: your email
   - Click "Save and Continue"
   - Skip "Scopes" for now
   - Add yourself as a test user
   - Click "Save and Continue"

4. Back to "Create OAuth client ID":
   - Application type: **Desktop app**
   - Name: PersonalDocGenerator
   - Click "Create"

5. Download the credentials:
   - Click the download button (⬇) next to your new OAuth client
   - Save as `credentials.json`

### 4. Add credentials.json to Your Project

1. Move the downloaded `credentials.json` to your PersonalDocGenerator directory:
   ```bash
   mv ~/Downloads/credentials.json ~/Development/Scripts/PersonalDocGenerator/
   ```

2. Verify the file is in the correct location:
   ```bash
   ls ~/Development/Scripts/PersonalDocGenerator/credentials.json
   ```

### 5. First-Time Authentication

The first time you use Google Drive features, you'll need to authenticate:

1. Run the document generator (it will detect credentials.json)
2. A browser window will open asking you to sign in
3. Sign in with your Google Account
4. Grant the requested permissions:
   - View and manage Google Drive files
   - View and manage Google Docs

5. After authorization, a `token.pickle` file will be created
6. Future runs will use this token automatically

## Usage Examples

### Reading from Google Docs

When prompted for writing style or topic, paste a Google Docs URL:

```
Enter file path, link, or text: https://docs.google.com/document/d/1abc123xyz/edit
```

### Reading from Google Drive

```
Enter file path, link, or text: https://drive.google.com/file/d/1abc123xyz/view
```

### Saving to Google Docs

When prompted for output location, enter "docs":

```
Enter directory path or press Enter: docs
```

The tool will create a new Google Doc and provide the URL.

### Uploading to Google Drive Folder

Paste a Google Drive folder URL:

```
Enter directory path or press Enter: https://drive.google.com/drive/folders/1abc123xyz
```

### Command-Line Mode

```bash
# Read from Google Docs, save to Google Docs
python3 document_generator.py \
  --topic "https://docs.google.com/document/d/YOUR_DOC_ID/edit" \
  --style "https://docs.google.com/document/d/YOUR_STYLE_DOC_ID/edit" \
  --output "docs" \
  --audience "business leaders" \
  --type "whitepaper"

# Read from local, save to Drive folder
python3 document_generator.py \
  --topic "examples/sample_topic.txt" \
  --output "https://drive.google.com/drive/folders/YOUR_FOLDER_ID" \
  --type "report"
```

## Troubleshooting

### "credentials.json not found"

**Solution**: Make sure credentials.json is in the PersonalDocGenerator directory.

### "Access denied" or "Invalid credentials"

**Solution**:
1. Delete `token.pickle`
2. Run the tool again to re-authenticate
3. Make sure you're using the Google Account that was added as a test user

### "API not enabled"

**Solution**: Go back to Google Cloud Console and verify both Google Drive API and Google Docs API are enabled.

### "Quota exceeded"

**Solution**: Google APIs have usage limits. Wait a few minutes or check your quota in Google Cloud Console.

## Security Notes

- `credentials.json` contains your OAuth client credentials (not your password)
- `token.pickle` contains your authentication token
- Both files are listed in `.gitignore` and should NEVER be committed to git
- Keep these files secure and don't share them
- If compromised, revoke access in [Google Account Security](https://myaccount.google.com/security)

## Optional: Increase Quota

For heavy usage:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" → "Quotas"
3. Review and request quota increases if needed

## Disabling Google Drive Integration

If you don't need Google Drive:

1. Simply don't create credentials.json
2. The tool will work fine with local files only
3. You'll see "Google Drive integration not configured (optional)" at startup

## Support

For Google API issues:
- [Google Drive API Documentation](https://developers.google.com/drive)
- [Google Docs API Documentation](https://developers.google.com/docs)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
