# Quick Start Guide

## Getting Started in 60 Seconds

### 1. Run the application
```bash
cd ~/Development/Scripts/DocumentGenerator
python3 document_generator.py
```

### 2. Follow the prompts

**Writing Style**: Use the example file
```
examples/sample_writing_style.txt
```

**Topic**: Use the example file
```
examples/sample_topic.txt
```

**Audience**:
```
healthcare executives
```

**Output Type**:
```
whitepaper
```

**Size**:
```
3 pages
```

**Output Location**: Press Enter for current directory

### 3. Confirm and generate

Type `yes` when prompted to confirm.

### 4. View your document

The generated document will be saved as `generated_whitepaper.md` in your output location.

## Creating Your Own Content

### Writing Style File
Create a text file describing your unique voice:
- Tone (formal, casual, conversational)
- Structure preferences
- Language choices
- Examples of what to avoid

### Topic File
Create a file with:
- Main topic/thesis
- Key insights and data points
- Quotes from experts
- Real-world examples
- Points to cover

### Tips
- Be specific about your requirements
- Include concrete examples and data
- Clearly define your target audience
- Review and refine the output as needed

## Example Command Flow

```bash
$ python3 document_generator.py

# When prompted for writing style:
examples/sample_writing_style.txt

# When prompted for topic:
examples/sample_topic.txt

# For audience:
business leaders

# For output type:
blog post

# For size:
2 pages

# For output location:
(press Enter)

# Confirm:
yes
```

Your document will be generated and saved!

## Next Steps

1. Review the generated document
2. Make any necessary edits
3. Convert to other formats if needed:
   ```bash
   # To Word
   pandoc generated_whitepaper.md -o output.docx

   # To PDF
   pandoc generated_whitepaper.md -o output.pdf
   ```

## Need Help?

See the full [README.md](README.md) for detailed documentation.
