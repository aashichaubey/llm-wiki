# 📝 Notes Pipeline

Converts handwritten Notability PDFs into structured markdown notes in Obsidian, queryable by Claude Code.

## How it works

```
Notability PDF (AirDrop from iPad)
        ↓
convert_pdf.py — PDF → page images
        ↓
extract_notes.py — Claude Vision reads each page → clean markdown
        ↓
Drops into Obsidian vault, organized by course
```

## Setup

```bash
git clone https://github.com/yourusername/notes-pipeline
cd notes-pipeline
pip install -r requirements.txt
cp env.example .env
# add your ANTHROPIC_API_KEY
```

Install poppler (required for pdf2image):
```bash
brew install poppler
```

## Usage

AirDrop your PDF from iPad to Mac, then:

```bash
python extract_notes.py ~/Desktop/lecture3.pdf ECE252 03
```

Notes land in your Obsidian vault at:
`LLM wiki/ECE252 - Systems Programming and Concurrency/lecture-03.md`

## Query your notes

```bash
cd "/Users/aashichaubey/Documents/LLM wiki/LLM wiki"
claude
```

Then ask anything:
- "Summarize what we covered in ECE252 so far"
- "Find everything related to concurrency and race conditions"
- "What's the difference between how ECE207 and ECE208 approach logic"

## Courses

| Code | Course |
|------|--------|
| ECE203 | Probability and Statistics |
| ECE207 | Signals and Systems |
| ECE208 | Discrete Mathematics and Logic |
| ECE224 | Embedded Microprocessor Systems |
| ECE252 | Systems Programming and Concurrency |
| ECE298 | Instrumentation Lab |
