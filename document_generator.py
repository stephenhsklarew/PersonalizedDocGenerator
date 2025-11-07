#!/usr/bin/env python3
"""
Document Generator CLI
Generates draft documents based on writing style, topic, and preferences using Claude AI.
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Tuple
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DocumentGenerator:
    """Main class for document generation."""

    def __init__(self):
        """Initialize the document generator."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not found in environment variables.")
            print("Please set your API key in .env file or environment.")
            sys.exit(1)

        self.client = Anthropic(api_key=api_key)
        self.style_content = ""
        self.topic_content = ""
        self.audience = ""
        self.output_type = ""
        self.size = ""
        self.output_location = ""

    def read_file(self, path: str) -> str:
        """
        Read content from a file path or Google Drive link.

        Args:
            path: Local file path or Google Drive URL

        Returns:
            Content of the file as string
        """
        # Check if it's a Google Drive link
        if "drive.google.com" in path or "docs.google.com" in path:
            return self.read_google_drive(path)
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

    def read_google_drive(self, url: str) -> str:
        """
        Read content from Google Drive.
        Note: This requires Google Drive API setup and authentication.
        """
        print("⚠ Google Drive integration requires additional setup.")
        print("For now, please download the file and provide a local path.")
        print("Google Drive API integration can be added if needed.")
        return ""

    def get_style_input(self) -> str:
        """Get writing style input from user."""
        print("\n" + "="*60)
        print("WRITING STYLE & VOICE")
        print("="*60)
        print("Enter the writing style/voice information.")
        print("Options:")
        print("  1. Enter a file path (local)")
        print("  2. Enter a Google Drive link")
        print("  3. Type/paste the style description directly")
        print()

        choice = input("Your choice (path/link/text): ").strip()

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
        print("Enter the topic information (insights, quotes, key points).")
        print("Options:")
        print("  1. Enter a file path (local)")
        print("  2. Enter a Google Drive link")
        print("  3. Type/paste the topic information directly")
        print()

        choice = input("Your choice (path/link/text): ").strip()

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
        print("Options:")
        print("  1. Enter a local directory path (e.g., ~/Documents/)")
        print("  2. Enter a Google Drive folder link")
        print("  3. Press Enter for current directory")
        print()

        location = input("Output location: ").strip()
        if not location:
            location = "."
            print(f"Using current directory: {os.path.abspath(location)}")

        return location

    def generate_document(self) -> str:
        """Generate the document using Claude AI."""
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
            # Call Claude API
            print("Sending request to Claude AI...")
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = message.content[0].text
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
        if "drive.google.com" in self.output_location:
            print("⚠ Google Drive upload requires additional setup.")
            print("Saving to current directory instead.")
            self.output_location = "."

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

    def run(self) -> None:
        """Run the interactive CLI application."""
        print("\n" + "="*60)
        print("DOCUMENT GENERATOR")
        print("Powered by Claude AI")
        print("="*60)

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
    try:
        generator = DocumentGenerator()
        generator.run()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
