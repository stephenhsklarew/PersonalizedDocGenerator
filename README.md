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

The tool supports two modes: **Interactive Mode** and **Command-Line Mode**.

### Interactive Mode

Run the interactive CLI for step-by-step guidance:

```bash
python3 document_generator.py
```

or make it executable:

```bash
chmod +x document_generator.py
./document_generator.py
```

### Command-Line Mode

Use command-line arguments for automation and scripting:

```bash
python3 document_generator.py \
  --topic "examples/sample_topic.txt" \
  --style "examples/sample_writing_style.txt" \
  --audience "business leaders" \
  --type "whitepaper" \
  --size "3 pages" \
  --output "./output"
```

**Available Arguments:**
- `-t, --topic` - Topic content (file path or direct text) - **Required for CLI mode**
- `-s, --style` - Writing style (file path or direct text) - Optional
- `-a, --audience` - Target audience (e.g., 'business leaders')
- `--type` - Output type (e.g., 'blog post', 'whitepaper')
- `--size` - Document size (e.g., '3 pages', '1000 words')
- `-o, --output` - Output directory

**Examples:**

With files:
```bash
python3 document_generator.py \
  --topic examples/sample_topic.txt \
  --style examples/sample_writing_style.txt \
  --audience "healthcare executives" \
  --type "executive summary" \
  --size "2 pages"
```

With direct text:
```bash
python3 document_generator.py \
  --topic "Write about the benefits of remote work for small businesses" \
  --audience "small business owners" \
  --type "blog post" \
  --size "500 words"
```

View help:
```bash
python3 document_generator.py --help
```

### Interactive Mode Prompts

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

## Testing

Two test scripts are provided to validate your installation:

### Bash Test Script

Run the comprehensive bash test suite:

```bash
./test_generator.sh
```

This script will:
- ✓ Check for API key configuration
- ✓ Verify Python dependencies
- ✓ Test help command
- ✓ Generate documents with sample files
- ✓ Generate documents with direct text input
- ✓ Verify example files exist
- ✓ Display test summary

### Python Test Script

Run the Python-based test suite:

```bash
python3 test_generator.py
```

This script will:
- ✓ Check environment setup
- ✓ Verify example files
- ✓ Test module import
- ✓ Test file reading functionality
- ✓ Test document generation
- ✓ Display detailed test results

**Quick Test:**

To quickly test the command-line mode:

```bash
python3 document_generator.py \
  --topic "Write a brief overview of cloud computing benefits" \
  --audience "business executives" \
  --type "brief" \
  --size "1 page"
```

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
PersonalDocGenerator/
├── document_generator.py         # Main CLI application
├── test_generator.sh            # Bash test script
├── test_generator.py            # Python test script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── .env                         # Your API key (not in git)
├── .gitignore                   # Git ignore rules
├── README.md                    # Full documentation
├── QUICKSTART.md                # Quick start guide
└── examples/
    ├── sample_writing_style.txt # Example writing style
    └── sample_topic.txt         # Example topic content
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

- **v1.1.0** (2025-01-07)
  - Added command-line argument support for automation
  - Added comprehensive test scripts (Bash and Python)
  - Added example files for quick testing
  - Enhanced documentation with CLI usage examples
  - Support for both interactive and non-interactive modes

- **v1.0.0** (2025-01-07)
  - Initial release
  - Interactive CLI interface
  - Local file input/output
  - Claude AI integration
  - Multiple document types support
