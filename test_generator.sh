#!/bin/bash
# Test script for PersonalDocGenerator
# Tests the document generator with sample inputs

set -e  # Exit on error

echo "=========================================="
echo "PersonalDocGenerator Test Suite"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "document_generator.py" ]; then
    echo -e "${RED}Error: document_generator.py not found${NC}"
    echo "Please run this script from the PersonalDocGenerator directory"
    exit 1
fi

# Check for API key
if [ -f ".env" ]; then
    source .env
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo -e "${YELLOW}Warning: ANTHROPIC_API_KEY not set in .env file${NC}"
        echo "The script will continue but API calls will fail"
        echo ""
    else
        echo -e "${GREEN}✓ API key found${NC}"
    fi
else
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo ""
fi

# Check Python dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
python3 -c "import anthropic, dotenv" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}✗ Missing dependencies. Run: pip3 install -r requirements.txt${NC}"
    exit 1
fi
echo ""

# Test 1: Help command
echo "=========================================="
echo "Test 1: Help Command"
echo "=========================================="
python3 document_generator.py --help | head -20
echo ""
echo -e "${GREEN}✓ Test 1 passed${NC}"
echo ""

# Test 2: Command-line mode with files
echo "=========================================="
echo "Test 2: Generate with Sample Files"
echo "=========================================="
echo "Testing command-line mode with example files..."
echo ""

OUTPUT_DIR="./test_output"
mkdir -p "$OUTPUT_DIR"

python3 document_generator.py \
  --topic "examples/sample_topic.txt" \
  --style "examples/sample_writing_style.txt" \
  --audience "healthcare executives" \
  --type "executive summary" \
  --size "1 page" \
  --output "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Test 2 passed${NC}"
    echo -e "Output file created in: ${BLUE}$OUTPUT_DIR${NC}"

    # Check if file was created
    if ls "$OUTPUT_DIR"/generated_*.md 1> /dev/null 2>&1; then
        FILE=$(ls "$OUTPUT_DIR"/generated_*.md | head -1)
        echo -e "File: ${BLUE}$FILE${NC}"
        echo "File size: $(wc -c < "$FILE") bytes"
        echo "First few lines:"
        echo "---"
        head -10 "$FILE"
        echo "---"
    fi
else
    echo ""
    echo -e "${RED}✗ Test 2 failed${NC}"
    echo "This is likely due to an invalid API key"
fi
echo ""

# Test 3: Command-line mode with direct text
echo "=========================================="
echo "Test 3: Generate with Direct Text Input"
echo "=========================================="
echo "Testing command-line mode with direct text input..."
echo ""

python3 document_generator.py \
  --topic "The importance of cybersecurity for small businesses. Include tips for protecting customer data." \
  --audience "small business owners" \
  --type "blog post" \
  --size "500 words" \
  --output "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Test 3 passed${NC}"
else
    echo ""
    echo -e "${RED}✗ Test 3 failed${NC}"
    echo "This is likely due to an invalid API key"
fi
echo ""

# Test 4: Check example files exist
echo "=========================================="
echo "Test 4: Verify Example Files"
echo "=========================================="
if [ -f "examples/sample_writing_style.txt" ] && [ -f "examples/sample_topic.txt" ]; then
    echo -e "${GREEN}✓ Example files exist${NC}"
    echo "  - examples/sample_writing_style.txt ($(wc -c < examples/sample_writing_style.txt) bytes)"
    echo "  - examples/sample_topic.txt ($(wc -c < examples/sample_topic.txt) bytes)"
else
    echo -e "${RED}✗ Example files missing${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
if ls "$OUTPUT_DIR"/generated_*.md 1> /dev/null 2>&1; then
    echo -e "${GREEN}✓ Document generation successful${NC}"
    echo "Generated files:"
    ls -lh "$OUTPUT_DIR"/generated_*.md
    echo ""
    echo "To view generated documents:"
    echo -e "  ${BLUE}cat $OUTPUT_DIR/generated_*.md${NC}"
    echo ""
    echo "To convert to other formats:"
    echo -e "  ${BLUE}pandoc $OUTPUT_DIR/generated_*.md -o output.pdf${NC}"
    echo -e "  ${BLUE}pandoc $OUTPUT_DIR/generated_*.md -o output.docx${NC}"
else
    echo -e "${YELLOW}⚠ No documents generated${NC}"
    echo "This is likely due to API key issues"
    echo ""
    echo "To fix:"
    echo "1. Get an API key from https://console.anthropic.com/"
    echo "2. Add it to .env file:"
    echo -e "   ${BLUE}echo 'ANTHROPIC_API_KEY=your_key_here' > .env${NC}"
    echo "3. Run this test again"
fi

echo ""
echo "=========================================="
echo "Tests Complete!"
echo "=========================================="
