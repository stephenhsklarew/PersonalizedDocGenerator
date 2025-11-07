#!/usr/bin/env python3
"""
Test script for PersonalDocGenerator
Validates installation and tests document generation
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60)

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}{text}{Colors.NC}")

def check_environment():
    """Check if environment is properly set up"""
    print_header("Test 1: Environment Check")

    # Check if we're in the right directory
    if not Path("document_generator.py").exists():
        print_error("document_generator.py not found")
        print("Please run this script from the PersonalDocGenerator directory")
        return False

    print_success("Found document_generator.py")

    # Check for .env file
    if Path(".env").exists():
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            print_success(f"API key found (starts with: {api_key[:15]}...)")
        else:
            print_warning("API key not found in .env file")
            return False
    else:
        print_warning(".env file not found")
        return False

    # Check dependencies
    try:
        import anthropic
        from dotenv import load_dotenv
        print_success("All Python dependencies installed")
    except ImportError as e:
        print_error(f"Missing dependency: {e}")
        print("Run: pip3 install -r requirements.txt")
        return False

    return True

def check_examples():
    """Check if example files exist"""
    print_header("Test 2: Example Files")

    style_file = Path("examples/sample_writing_style.txt")
    topic_file = Path("examples/sample_topic.txt")

    if style_file.exists():
        size = style_file.stat().st_size
        print_success(f"sample_writing_style.txt exists ({size} bytes)")
    else:
        print_error("sample_writing_style.txt not found")
        return False

    if topic_file.exists():
        size = topic_file.stat().st_size
        print_success(f"sample_topic.txt exists ({size} bytes)")
    else:
        print_error("sample_topic.txt not found")
        return False

    return True

def test_import():
    """Test importing the document generator"""
    print_header("Test 3: Module Import")

    try:
        sys.path.insert(0, str(Path.cwd()))
        import document_generator
        print_success("Successfully imported document_generator module")

        # Test instantiation
        generator = document_generator.DocumentGenerator()
        print_success("Successfully created DocumentGenerator instance")
        return True
    except Exception as e:
        print_error(f"Failed to import: {e}")
        return False

def test_file_reading():
    """Test file reading functionality"""
    print_header("Test 4: File Reading")

    try:
        sys.path.insert(0, str(Path.cwd()))
        import document_generator

        generator = document_generator.DocumentGenerator()

        # Test reading style file
        style_content = generator.read_file("examples/sample_writing_style.txt")
        if style_content:
            print_success(f"Read style file ({len(style_content)} characters)")
        else:
            print_error("Failed to read style file")
            return False

        # Test reading topic file
        topic_content = generator.read_file("examples/sample_topic.txt")
        if topic_content:
            print_success(f"Read topic file ({len(topic_content)} characters)")
        else:
            print_error("Failed to read topic file")
            return False

        return True
    except Exception as e:
        print_error(f"File reading test failed: {e}")
        return False

def test_generation():
    """Test document generation with sample inputs"""
    print_header("Test 5: Document Generation")

    try:
        sys.path.insert(0, str(Path.cwd()))
        import document_generator

        generator = document_generator.DocumentGenerator()

        # Set up test parameters
        generator.style_content = generator.read_file("examples/sample_writing_style.txt")
        generator.topic_content = "Write a brief 2-paragraph overview of artificial intelligence and its impact on business."
        generator.audience = "business executives"
        generator.output_type = "brief"
        generator.size = "2 paragraphs"
        generator.output_location = "./test_output"

        # Create output directory
        Path("./test_output").mkdir(exist_ok=True)

        print_info("Generating test document...")
        print_info("This may take 10-30 seconds...")

        # Generate document
        content = generator.generate_document()

        if content and len(content) > 100:
            print_success(f"Generated document ({len(content)} characters)")

            # Save document
            generator.save_document(content)

            # Show preview
            print("\nDocument Preview (first 200 characters):")
            print("-" * 60)
            print(content[:200] + "...")
            print("-" * 60)

            return True
        else:
            print_error("Generated content is too short or empty")
            return False

    except Exception as e:
        print_error(f"Document generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print_header("PersonalDocGenerator Test Suite")
    print("Testing installation and functionality...\n")

    results = []

    # Run tests
    results.append(("Environment Check", check_environment()))
    results.append(("Example Files", check_examples()))
    results.append(("Module Import", test_import()))
    results.append(("File Reading", test_file_reading()))
    results.append(("Document Generation", test_generation()))

    # Print summary
    print_header("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.NC}" if result else f"{Colors.RED}FAIL{Colors.NC}"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print_success("\nAll tests passed! 🎉")
        print("\nYou can now use the document generator:")
        print_info("  python3 document_generator.py --help")
    else:
        print_warning(f"\n{total - passed} test(s) failed")
        print("\nCommon issues:")
        print("1. API Key: Make sure ANTHROPIC_API_KEY is set in .env")
        print("2. Dependencies: Run 'pip3 install -r requirements.txt'")
        print("3. Files: Ensure example files exist in examples/ directory")

    # Show output files if generated
    if Path("test_output").exists():
        output_files = list(Path("test_output").glob("generated_*.md"))
        if output_files:
            print("\nGenerated test files:")
            for file in output_files:
                size = file.stat().st_size
                print(f"  {Colors.BLUE}{file}{Colors.NC} ({size} bytes)")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
