#!/usr/bin/env python3
"""
Document Generator CLI
Generates draft documents based on writing style, topic, and preferences using AI models.
Supports: Anthropic Claude, OpenAI GPT, Google Gemini
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import helper modules
try:
    from ai_models import AIModelManager
    from google_drive_helper import GoogleDriveHelper
except ImportError as e:
    print(f"Error importing helper modules: {e}")
    print("Make sure ai_models.py and google_drive_helper.py are in the same directory.")
    sys.exit(1)


class DocumentGenerator:
    """Main class for document generation."""

    def __init__(self, model_key: str = 'claude-3-5-sonnet'):
        """Initialize the document generator."""
        self.model_key = model_key
        self.ai_manager = None
        self.google_drive = None
        self.style_content = ""
        self.topic_content = ""
        self.audience = ""
        self.output_type = ""
        self.size = ""
        self.output_location = ""

        # Initialize AI model
        try:
            self.ai_manager = AIModelManager(model_key)
            print(f"✓ Initialized AI Model: {self.ai_manager.name}")
        except Exception as e:
            print(f"Error initializing AI model: {e}")
            sys.exit(1)

        # Try to initialize Google Drive (optional)
        try:
            self.google_drive = GoogleDriveHelper()
            print("✓ Google Drive integration available")
        except FileNotFoundError as e:
            print("ℹ Google Drive integration not configured (optional)")
            self.google_drive = None
        except Exception as e:
            print(f"ℹ Google Drive not available: {e}")
            self.google_drive = None

    def read_file(self, path: str) -> str:
        """
        Read content from a file path or Google Drive link.

        Args:
            path: Local file path or Google Drive URL

        Returns:
            Content of the file as string
        """
        # Check if it's a Google Drive or Google Docs link
        if "drive.google.com" in path or "docs.google.com" in path:
            if self.google_drive:
                # Determine if it's a Doc or Drive file
                if "docs.google.com" in path:
                    return self.google_drive.read_doc(path)
                else:
                    return self.google_drive.read_file(path)
            else:
                print("⚠ Google Drive integration not available.")
                print("Please set up credentials.json to use Google Drive/Docs.")
                return ""
        else:
            return self.read_local_file(path)

    def read_local_file(self, path: str) -> str:
        """Read content from a local file (supports .txt, .md, .docx, .pdf)."""
        try:
            file_path = Path(path).expanduser()
            if not file_path.exists():
                print(f"Error: File not found: {path}")
                return ""

            # Get file extension
            ext = file_path.suffix.lower()

            # Handle Word documents
            if ext in ['.docx', '.doc']:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                    print(f"✓ Successfully read {len(content)} characters from Word document {file_path.name}")
                    return content
                except Exception as e:
                    print(f"Error reading Word document: {e}")
                    print("Make sure python-docx is installed: pip install python-docx")
                    return ""

            # Handle PDF files
            elif ext == '.pdf':
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(file_path)
                    content = ''
                    for page in reader.pages:
                        content += page.extract_text() + '\n'
                    print(f"✓ Successfully read {len(content)} characters from PDF {file_path.name}")
                    return content
                except Exception as e:
                    print(f"Error reading PDF: {e}")
                    print("Make sure PyPDF2 is installed: pip install PyPDF2")
                    return ""

            # Handle text files (default)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✓ Successfully read {len(content)} characters from {file_path.name}")
                return content

        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return ""

    def get_model_input(self) -> str:
        """Get AI model selection from user."""
        print("\n" + "="*60)
        print("AI MODEL SELECTION")
        print("="*60)
        print("Available AI models:\n")

        # Build numbered list
        model_keys = list(AIModelManager.MODELS.keys())
        by_provider = AIModelManager.list_models_by_provider()

        index = 1
        key_to_number = {}

        for provider in ['anthropic', 'openai', 'gemini']:
            if provider in by_provider:
                provider_name = {
                    'anthropic': 'Anthropic Claude',
                    'openai': 'OpenAI GPT',
                    'gemini': 'Google Gemini'
                }[provider]

                print(f"{provider_name}:")
                for model in by_provider[provider]:
                    print(f"  {index}. {model['name']}")
                    key_to_number[str(index)] = model['key']
                    index += 1
                print()

        print(f"Default: 1 (Claude 3.5 Sonnet)")
        print()

        choice = input("Enter number or model key (or press Enter for default): ").strip()

        if not choice:
            return "claude-3-5-sonnet"

        # Check if it's a number
        if choice in key_to_number:
            selected_key = key_to_number[choice]
            print(f"✓ Selected: {AIModelManager.MODELS[selected_key]['name']}")
            return selected_key

        # Check if it's a direct key
        if choice in AIModelManager.MODELS:
            print(f"✓ Selected: {AIModelManager.MODELS[choice]['name']}")
            return choice

        # Invalid input
        print(f"\n⚠ Invalid selection: '{choice}'")
        print("Using default: Claude 3.5 Sonnet")
        return "claude-3-5-sonnet"

    def get_style_input(self) -> str:
        """Get writing style input from user."""
        print("\n" + "="*60)
        print("WRITING STYLE & VOICE")
        print("="*60)
        print("You can provide the writing style in three ways:")
        print("  • File path: examples/sample_writing_style.txt")
        print("  • Google Drive link: https://docs.google.com/document/d/...")
        print("  • Direct text: Type your style description here")
        print()
        print("Press Enter to use default professional style.")
        print()

        choice = input("Enter file path, link, or text: ").strip()

        if not choice:
            print("No input provided. Using default professional style.")
            return "Professional, clear, and engaging writing style."

        # Check if it's a path or URL
        if choice.startswith("http") or choice.startswith("~") or choice.startswith("/") or os.path.exists(choice):
            content = self.read_file(choice)
            if content:
                return content
            else:
                print("Failed to read file. Please enter style description directly:")
                return input("> ").strip()
        else:
            # It's direct text input
            return choice

    def get_topic_input(self) -> str:
        """Get topic, insights, and quotes from user."""
        print("\n" + "="*60)
        print("TOPIC, INSIGHTS & QUOTES")
        print("="*60)
        print("Provide your topic content (insights, quotes, key points):")
        print("  • File path: examples/sample_topic.txt")
        print("  • Google Drive link: https://docs.google.com/document/d/...")
        print("  • Direct text: Type your topic description here")
        print()
        print("This field is required.")
        print()

        choice = input("Enter file path, link, or text: ").strip()

        if not choice:
            print("Error: Topic information is required.")
            sys.exit(1)

        # Check if it's a path or URL
        if choice.startswith("http") or choice.startswith("~") or choice.startswith("/") or os.path.exists(choice):
            content = self.read_file(choice)
            if content:
                return content
            else:
                print("Failed to read file. Please enter topic information directly:")
                return input("> ").strip()
        else:
            # It's direct text input
            return choice

    def get_audience_input(self) -> str:
        """Get target audience from user."""
        print("\n" + "="*60)
        print("TARGET AUDIENCE")
        print("="*60)
        print("Who is the target audience for this document?")
        print("Examples: business leaders, technical professionals, general public, executives")
        print()

        audience = input("Target audience: ").strip()
        if not audience:
            audience = "general professional audience"
            print(f"Using default: {audience}")

        return audience

    def get_output_type_input(self) -> str:
        """Get desired output type from user."""
        print("\n" + "="*60)
        print("OUTPUT TYPE")
        print("="*60)
        print("What type of document should be generated?")
        print("Examples: blog post, whitepaper, marketing slick, article, report, case study")
        print()

        output_type = input("Output type: ").strip()
        if not output_type:
            output_type = "blog post"
            print(f"Using default: {output_type}")

        return output_type

    def get_size_input(self) -> str:
        """Get desired document size from user."""
        print("\n" + "="*60)
        print("DOCUMENT SIZE")
        print("="*60)
        print("How long should the document be?")
        print("Examples: 1 page, 3 pages, 10 pages, 500 words, 2000 words")
        print()

        size = input("Document size: ").strip()
        if not size:
            size = "2-3 pages"
            print(f"Using default: {size}")

        return size

    def get_output_location_input(self) -> str:
        """Get output location from user."""
        print("\n" + "="*60)
        print("OUTPUT LOCATION")
        print("="*60)
        print("Where should the document be saved?")
        print("  • Directory path: ~/Documents/output (saves as markdown .md file)")
        print("  • Google Drive link: https://drive.google.com/drive/folders/... (creates native Google Doc)")
        print("  • Type 'docs' to create in Google Docs root")
        print("  • Press Enter for current directory")
        print()

        location = input("Enter directory path or press Enter: ").strip()
        if not location:
            location = "."
            print(f"Using current directory: {os.path.abspath(location)}")
        elif location.lower() == 'docs':
            location = "docs.google.com"
            print("Will create as Google Doc")

        return location

    def generate_document(self) -> str:
        """Generate the document using selected AI model.

        Always generates in markdown format. For Google Docs output,
        markdown will be converted to native formatting automatically.
        """
        print("\n" + "="*60)
        print("GENERATING DOCUMENT...")
        print("="*60)

        # Always use markdown - will be converted to Google Docs format if needed
        format_instructions = """
FORMAT: Use Markdown formatting:
- Use # for the main title (only once at the beginning)
- Use ## for major section headings
- Use ### for subsection headings
- Use **bold** for emphasis (sparingly)
- Use *italic* for subtle emphasis (sparingly)
- Use bullet points with - or *
- Use numbered lists with 1., 2., 3.
"""

        # Build the prompt
        prompt = f"""You are a professional content writer tasked with creating a {self.output_type}.

WRITING STYLE & VOICE:
{self.style_content}

CRITICAL: Deeply analyze the writing style above. Pay close attention to:
- Sentence structure patterns and rhythm
- Word choice and vocabulary level
- Tone and personality quirks
- How ideas are introduced and developed
- Paragraph structure and flow
- Use of examples, metaphors, or analogies
- Any unique stylistic signatures

Mirror these patterns authentically in your writing.

TARGET AUDIENCE:
{self.audience}

TOPIC, INSIGHTS & QUOTES:
{self.topic_content}

DOCUMENT REQUIREMENTS:
- Type: {self.output_type}
- Length: {self.size}
- Audience: {self.audience}

{format_instructions}

ANTI-AI-PATTERN INSTRUCTIONS (CRITICAL):
Write like a human, not an AI. Specifically avoid these common AI patterns:

❌ AVOID:
- Generic openings ("In today's world...", "In an era of...", "As we navigate...")
- Excessive hedging language ("may," "might," "could potentially," "arguably")
- Formulaic transitions ("Moreover," "Furthermore," "Additionally," "In conclusion")
- Overly enthusiastic or promotional tone
- Lists of abstract concepts without concrete examples
- Perfectly balanced arguments (real writing has a point of view)
- Explaining what you're about to do ("Let's explore...", "We will examine...")
- Meta-commentary about the document itself

✓ INSTEAD:
- Start directly with substance or a specific observation
- Make clear, confident statements when appropriate
- Use natural transitions that flow from ideas
- Vary sentence structure organically (mix short and long)
- Include specific examples, anecdotes, or concrete details
- Write with authentic voice and clear perspective
- Let ideas connect naturally without announcing connections

Generate a complete, well-structured {self.output_type} that:
1. DEEPLY matches the provided writing style and voice (analyze it carefully first)
2. Is tailored to the target audience ({self.audience})
3. Incorporates the topic, insights, and quotes provided naturally
4. Meets the length requirement ({self.size})
5. Sounds like authentic human writing, not AI-generated content
6. Is professionally formatted and ready for publication

Generate the complete document now:"""

        try:
            # Call AI model
            print(f"Sending request to {self.ai_manager.name}...")
            content = self.ai_manager.generate(prompt)
            print(f"✓ Generated {len(content)} characters")
            return content

        except Exception as e:
            print(f"Error generating document: {e}")
            sys.exit(1)

    def extract_title_from_content(self, content: str) -> str:
        """Extract title from markdown content (first # heading).

        Returns cleaned title suitable for filename, or default if no title found.
        """
        import re

        lines = content.split('\n')
        for line in lines:
            # Look for markdown heading
            match = re.match(r'^#\s+(.+)$', line.strip())
            if match:
                title = match.group(1).strip()
                # Clean title for filename (remove special characters)
                title = re.sub(r'[^\w\s-]', '', title)  # Remove special chars except spaces and hyphens
                title = re.sub(r'\s+', ' ', title)  # Normalize spaces
                title = title.strip()
                return title[:80]  # Limit length to 80 chars

        # Fallback if no title found
        return f"Generated {self.output_type.title()}"

    def save_document(self, content: str) -> None:
        """Save the generated document to the specified location."""
        print("\n" + "="*60)
        print("SAVING DOCUMENT...")
        print("="*60)

        # Extract title from content for filename
        doc_title = self.extract_title_from_content(content)

        # Check if it's a Google Drive location
        if "drive.google.com" in self.output_location or "docs.google.com" in self.output_location:
            if self.google_drive:
                # Format: [Title]-Generated
                title = f"{doc_title}-Generated"

                # Extract folder ID if it's a folder URL
                folder_id = None
                if "/folders/" in self.output_location:
                    folder_id = self.google_drive.extract_file_id(self.output_location)

                # Always create as native Google Doc
                url = self.google_drive.create_doc(title, content, folder_id=folder_id)
                if url:
                    if folder_id:
                        print(f"✓ Document saved as Google Doc in folder!")
                    else:
                        print(f"✓ Document saved as Google Doc!")
                    print(f"  Title: {title}")
                    print(f"  URL: {url}")
                    print(f"  Size: {len(content)} characters")
                    return

                # If Google Drive save failed, fall back to local
                print("⚠ Google Drive save failed, saving locally instead...")
                self.output_location = "."
            else:
                print("⚠ Google Drive integration not available.")
                print("Saving to current directory instead.")
                self.output_location = "."

        # Save locally
        # Expand path and create directory if needed
        output_path = Path(self.output_location).expanduser()
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)

        # Format: [Title]-Generated.md
        filename = f"{doc_title}-Generated.md"
        full_path = output_path / filename

        # Save the file
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ Document saved successfully!")
            print(f"  Filename: {filename}")
            print(f"  Location: {full_path.absolute()}")
            print(f"  Size: {len(content)} characters")
        except Exception as e:
            print(f"Error saving document: {e}")
            sys.exit(1)

    def run_with_args(self, args: argparse.Namespace) -> None:
        """Run with command-line arguments (non-interactive mode)."""
        print("\n" + "="*60)
        print("DOCUMENT GENERATOR")
        print(f"Using: {self.ai_manager.name}")
        print("="*60)

        # Load style content
        if args.style:
            if os.path.exists(args.style) or args.style.startswith("~"):
                self.style_content = self.read_file(args.style)
                if not self.style_content:
                    print(f"Error: Could not read style file: {args.style}")
                    sys.exit(1)
            else:
                self.style_content = args.style
        else:
            self.style_content = "Professional, clear, and engaging writing style."

        # Load topic content
        if os.path.exists(args.topic) or args.topic.startswith("~"):
            self.topic_content = self.read_file(args.topic)
            if not self.topic_content:
                print(f"Error: Could not read topic file: {args.topic}")
                sys.exit(1)
        else:
            self.topic_content = args.topic

        # Set other parameters
        self.audience = args.audience or "general professional audience"
        self.output_type = args.type or "blog post"
        self.size = args.size or "2-3 pages"
        self.output_location = args.output or "."

        # Display summary
        print("\n" + "="*60)
        print("CONFIGURATION")
        print("="*60)
        print(f"AI Model: {self.ai_manager.name}")
        print(f"Output Type: {self.output_type}")
        print(f"Audience: {self.audience}")
        print(f"Size: {self.size}")
        print(f"Style Length: {len(self.style_content)} characters")
        print(f"Topic Length: {len(self.topic_content)} characters")
        print(f"Output Location: {self.output_location}")

        # Generate and save (always uses markdown, converted automatically for Google Docs)
        content = self.generate_document()
        self.save_document(content)

        print("\n" + "="*60)
        print("✓ COMPLETE!")
        print("="*60)

    def run(self) -> None:
        """Run the interactive CLI application."""
        print("\n" + "="*60)
        print("DOCUMENT GENERATOR")
        print("Powered by Multiple AI Models")
        print("="*60)

        # Get model selection (may reinitialize AI manager)
        new_model_key = self.get_model_input()
        if new_model_key != self.model_key:
            print(f"\nSwitching to {AIModelManager.MODELS[new_model_key]['name']}...")
            self.model_key = new_model_key
            try:
                self.ai_manager = AIModelManager(new_model_key)
                print(f"✓ Model switched successfully")
            except Exception as e:
                print(f"Error switching model: {e}")
                sys.exit(1)

        # Gather inputs
        self.style_content = self.get_style_input()
        self.topic_content = self.get_topic_input()
        self.audience = self.get_audience_input()
        self.output_type = self.get_output_type_input()
        self.size = self.get_size_input()
        self.output_location = self.get_output_location_input()

        # Display summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"AI Model: {self.ai_manager.name}")
        print(f"Output Type: {self.output_type}")
        print(f"Audience: {self.audience}")
        print(f"Size: {self.size}")
        print(f"Style Length: {len(self.style_content)} characters")
        print(f"Topic Length: {len(self.topic_content)} characters")
        print(f"Output Location: {self.output_location}")
        print()

        # Confirm before generating
        confirm = input("Proceed with document generation? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Cancelled.")
            sys.exit(0)

        # Generate and save (always uses markdown, converted automatically for Google Docs)
        content = self.generate_document()
        self.save_document(content)

        print("\n" + "="*60)
        print("✓ COMPLETE!")
        print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered document generator using multiple AI models (Claude, GPT, Gemini)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode (default):
    python3 document_generator.py

  Command-line mode with Claude:
    python3 document_generator.py \\
      --model claude-3-5-sonnet \\
      --topic "examples/sample_topic.txt" \\
      --style "examples/sample_writing_style.txt" \\
      --audience "business leaders" \\
      --type "whitepaper" \\
      --size "3 pages" \\
      --output "./output"

  Using GPT-4:
    python3 document_generator.py \\
      --model gpt-4o \\
      --topic "Write about AI in healthcare" \\
      --audience "healthcare executives" \\
      --type "blog post"

  Using Gemini:
    python3 document_generator.py \\
      --model gemini-1.5-pro \\
      --topic "Remote work trends" \\
      --type "article"
        """
    )

    parser.add_argument(
        "-m", "--model",
        default="claude-3-5-sonnet",
        help="AI model to use (default: claude-3-5-sonnet). Options: claude-3-5-sonnet, claude-3-5-haiku, claude-3-opus, gpt-4, gpt-4o, gpt-3.5-turbo, gemini-pro, gemini-1.5-pro, gemini-1.5-flash"
    )
    parser.add_argument(
        "-t", "--topic",
        help="Topic content (file path or direct text). Required for non-interactive mode."
    )
    parser.add_argument(
        "-s", "--style",
        help="Writing style (file path or direct text). Optional, uses default if not provided."
    )
    parser.add_argument(
        "-a", "--audience",
        help="Target audience (e.g., 'business leaders', 'technical professionals')"
    )
    parser.add_argument(
        "--type",
        help="Output type (e.g., 'blog post', 'whitepaper', 'article')"
    )
    parser.add_argument(
        "--size",
        help="Document size (e.g., '3 pages', '1000 words')"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output location (directory path or Google Drive URL)"
    )

    args = parser.parse_args()

    try:
        # Initialize with selected model
        generator = DocumentGenerator(model_key=args.model)

        # Check if any arguments were provided (non-interactive mode)
        if args.topic:
            generator.run_with_args(args)
        else:
            # No arguments, run in interactive mode
            generator.run()

    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
