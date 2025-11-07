# Document Generator

AI-powered CLI tool that generates draft documents based on your writing style, topic insights, and preferences using Claude AI.

## Features

- **Interactive CLI**: Easy-to-use command-line interface with step-by-step prompts
- **Writing Style Input**: Provide your writing style via file or direct text
- **Topic & Insights**: Input topics, insights, and quotes from files or text
- **Customizable Output**: Specify document type, target audience, and length
- **Multiple Input Methods**: Support for local files and text input
- **Professional Generation**: Powered by Claude AI for high-quality content
- **Flexible Output**: Save to any local directory

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd ~/Development/Scripts/DocumentGenerator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**:
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

   Get your API key from [Anthropic Console](https://console.anthropic.com/)

## Usage

### Basic Usage

Run the interactive CLI:

```bash
python document_generator.py
```

or make it executable:

```bash
chmod +x document_generator.py
./document_generator.py
```

### Interactive Prompts

The application will guide you through the following steps:

#### 1. Writing Style & Voice
Enter your writing style/voice information:
- Provide a file path (e.g., `~/Documents/writing_style.txt`)
- Paste text directly
- Leave empty for default professional style

Example file content:
```
I write in a conversational yet authoritative tone. I use short paragraphs,
active voice, and concrete examples. I avoid jargon unless writing for
technical audiences. I like to start with a compelling hook and end with
a clear call-to-action.
```

#### 2. Topic, Insights & Quotes
Enter your topic information:
- Provide a file path with research, insights, quotes
- Paste content directly

Example:
```
Topic: The Future of Remote Work

Key Insights:
- 75% of employees want flexible work options
- Productivity increased 13% for remote workers
- Companies saving $11,000/year per remote employee

Quotes:
"Remote work isn't a perk anymore, it's a necessity" - Jane Smith, CEO

Key Points:
- Technology enabling collaboration
- Work-life balance improvements
- Environmental benefits
```

#### 3. Target Audience
Specify who will read this document:
- `business leaders`
- `technical professionals`
- `general public`
- `executives`
- `developers`

#### 4. Output Type
Choose the type of document:
- `blog post`
- `whitepaper`
- `marketing slick`
- `article`
- `report`
- `case study`
- `newsletter`

#### 5. Document Size
Specify the desired length:
- `1 page`
- `3 pages`
- `10 pages`
- `500 words`
- `2000 words`

#### 6. Output Location
Choose where to save:
- Local directory: `~/Documents/`
- Current directory: (press Enter)
- Specific path: `/Users/username/Projects/output/`

### Example Session

```bash
$ python document_generator.py

============================================================
DOCUMENT GENERATOR
Powered by Claude AI
============================================================

============================================================
WRITING STYLE & VOICE
============================================================
Enter the writing style/voice information.
Options:
  1. Enter a file path (local)
  2. Enter a Google Drive link
  3. Type/paste the style description directly

Your choice (path/link/text): ~/Documents/my_style.txt
✓ Successfully read 342 characters from my_style.txt

============================================================
TOPIC, INSIGHTS & QUOTES
============================================================
Enter the topic information (insights, quotes, key points).
Options:
  1. Enter a file path (local)
  2. Enter a Google Drive link
  3. Type/paste the topic information directly

Your choice (path/link/text): ~/Documents/remote_work_research.txt
✓ Successfully read 1523 characters from remote_work_research.txt

============================================================
TARGET AUDIENCE
============================================================
Who is the target audience for this document?
Examples: business leaders, technical professionals, general public, executives

Target audience: business leaders

============================================================
OUTPUT TYPE
============================================================
What type of document should be generated?
Examples: blog post, whitepaper, marketing slick, article, report, case study

Output type: whitepaper

============================================================
DOCUMENT SIZE
============================================================
How long should the document be?
Examples: 1 page, 3 pages, 10 pages, 500 words, 2000 words

Document size: 5 pages

============================================================
OUTPUT LOCATION
============================================================
Where should the document be saved?
Options:
  1. Enter a local directory path (e.g., ~/Documents/)
  2. Enter a Google Drive folder link
  3. Press Enter for current directory

Output location: ~/Documents/output/

============================================================
SUMMARY
============================================================
Output Type: whitepaper
Audience: business leaders
Size: 5 pages
Style Length: 342 characters
Topic Length: 1523 characters
Output Location: ~/Documents/output/

Proceed with document generation? (yes/no): yes

============================================================
GENERATING DOCUMENT...
============================================================
Sending request to Claude AI...
✓ Generated 8543 characters

============================================================
SAVING DOCUMENT...
============================================================
✓ Document saved successfully!
  Location: /Users/username/Documents/output/generated_whitepaper.md
  Size: 8543 characters

============================================================
✓ COMPLETE!
============================================================
```

## File Formats

### Input Files
- **Text files** (`.txt`, `.md`): Plain text content
- Any UTF-8 encoded text file

### Output Files
- **Markdown** (`.md`): Default output format
- Can be converted to other formats using tools like Pandoc

## Advanced Features

### Converting Output to Other Formats

Use Pandoc to convert the generated markdown to other formats:

**Convert to Word**:
```bash
pandoc generated_whitepaper.md -o output.docx
```

**Convert to PDF**:
```bash
pandoc generated_whitepaper.md -o output.pdf
```

**Convert to HTML**:
```bash
pandoc generated_whitepaper.md -o output.html
```

## Tips for Best Results

1. **Writing Style**: Be specific about tone, structure, and voice preferences
2. **Topic Content**: Include concrete data, quotes, and key points
3. **Audience**: Clearly define who will read this (affects language and depth)
4. **Document Type**: Different types have different structures (blog vs whitepaper)
5. **Size**: Be specific about length requirements

## Troubleshooting

### API Key Issues
```
Error: ANTHROPIC_API_KEY not found in environment variables.
```
**Solution**: Create a `.env` file with your API key or set the environment variable:
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

### File Not Found
```
Error: File not found: ~/Documents/style.txt
```
**Solution**: Check the file path and ensure the file exists. Use absolute paths if needed.

### Permission Issues
```
Error saving document: Permission denied
```
**Solution**: Ensure you have write permissions to the output directory.

## Future Enhancements

- [ ] Google Drive integration for reading/writing files
- [ ] Direct output to Word (.docx) and PDF formats
- [ ] Template library for different document types
- [ ] Batch processing multiple topics
- [ ] Style analysis from existing documents
- [ ] Version history and revisions

## Requirements

- Python 3.8+
- Anthropic API key
- Internet connection for API calls

## Project Structure

```
DocumentGenerator/
├── document_generator.py    # Main CLI application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variable template
├── .env                     # Your API key (not in git)
└── README.md               # This file
```

## Contributing

This is a personal utility script. Feel free to fork and customize for your needs.

## License

Personal use only.

## Support

For issues with:
- **Claude API**: See [Anthropic Documentation](https://docs.anthropic.com/)
- **This tool**: Check the troubleshooting section above

## Version History

- **v1.0.0** (2025-01-07)
  - Initial release
  - Interactive CLI interface
  - Local file input/output
  - Claude AI integration
  - Multiple document types support
