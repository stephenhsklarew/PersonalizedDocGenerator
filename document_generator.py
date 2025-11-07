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
        """Read content from a local file."""
        try:
            file_path = Path(path).expanduser()
            if not file_path.exists():
                print(f"Error: File not found: {path}")
                return ""

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
        print("Available AI models:")

        # Display models by provider
        models_list = AIModelManager.get_model_display_list()
        for line in models_list:
            print(line)

        print()
        print("Default: claude-3-5-sonnet")
        print()

        model_key = input("Enter model key (or press Enter for default): ").strip()

        if not model_key:
            return "claude-3-5-sonnet"

        # Validate model key
        if model_key not in AIModelManager.MODELS:
            print(f"⚠ Unknown model: {model_key}")
            print("Using default: claude-3-5-sonnet")
            return "claude-3-5-sonnet"

        return model_key

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
        print("  • Directory path: ~/Documents/output")
        print("  • Google Drive link: https://drive.google.com/drive/folders/...")
        print("  • Press Enter for current directory")
        print()

        location = input("Enter directory path or press Enter: ").strip()
        if not location:
            location = "."
            print(f"Using current directory: {os.path.abspath(location)}")

        return location

    def generate_document(self) -> str:
        """Generate the document using selected AI model."""
        print("\n" + "="*60)
        print("GENERATING DOCUMENT...")
        print("="*60)

        # Build the prompt
        prompt = f"""You are a professional content writer tasked with creating a {self.output_type}.

WRITING STYLE & VOICE:
{self.style_content}

TARGET AUDIENCE:
{self.audience}

TOPIC, INSIGHTS & QUOTES:
{self.topic_content}

DOCUMENT REQUIREMENTS:
- Type: {self.output_type}
- Length: {self.size}
- Audience: {self.audience}

Please generate a complete, well-structured {self.output_type} that:
1. Matches the provided writing style and voice
2. Is tailored to the target audience ({self.audience})
3. Incorporates the topic, insights, and quotes provided
4. Meets the length requirement ({self.size})
5. Is professionally formatted and ready for publication

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

    def save_document(self, content: str) -> None:
        """Save the generated document to the specified location."""
        print("\n" + "="*60)
        print("SAVING DOCUMENT...")
        print("="*60)

        # Check if it's a Google Drive location
        if "drive.google.com" in self.output_location or "docs.google.com" in self.output_location:
            if self.google_drive:
                output_type_clean = self.output_type.replace(" ", "_").lower()
                title = f"Generated {self.output_type.title()}"
                filename = f"generated_{output_type_clean}.md"

                # Check if it's a folder URL (for uploading files) or docs URL (for creating Google Docs)
                if "docs.google.com" in self.output_location or "/folders/" not in self.output_location:
                    # Create as Google Doc
                    url = self.google_drive.create_doc(title, content)
                    if url:
                        print(f"✓ Document saved as Google Doc!")
                        print(f"  URL: {url}")
                        print(f"  Size: {len(content)} characters")
                        return
                else:
                    # Upload to Drive folder
                    url = self.google_drive.upload_to_folder(self.output_location, filename, content)
                    if url:
                        print(f"✓ Document uploaded to Google Drive!")
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

        # Generate filename based on output type
        output_type_clean = self.output_type.replace(" ", "_").lower()
        filename = f"generated_{output_type_clean}.md"
        full_path = output_path / filename

        # Save the file
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ Document saved successfully!")
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
        print(f"Output Type: {self.output_type}")
        print(f"Audience: {self.audience}")
        print(f"Size: {self.size}")
        print(f"Style Length: {len(self.style_content)} characters")
        print(f"Topic Length: {len(self.topic_content)} characters")
        print(f"Output Location: {self.output_location}")

        # Generate and save
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

        # Generate and save
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
