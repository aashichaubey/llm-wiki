"""
Step 2: Gemini Flash (via OpenRouter) reads each page image and outputs clean markdown.
Usage: python extract_notes.py <path_to_pdf> <course_code> <lecture_number>

Example: python extract_notes.py ~/Desktop/lecture3.pdf ECE252 03
"""

import sys
import os
import base64
import httpx
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from convert_pdf import convert_pdf_to_images

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-3-flash-preview"

OBSIDIAN_VAULT = Path("/Users/aashichaubey/Documents/LLM wiki/LLM wiki")

COURSE_FOLDERS = {
    "ECE203": "ECE203 - Probability and Statistics",
    "ECE207": "ECE207 - Signals and Systems",
    "ECE208": "ECE208 - Discrete Mathematics and Logic",
    "ECE224": "ECE224 - Embedded Microprocessor Systems",
    "ECE252": "ECE252 - Systems Programming and Concurrency",
    "ECE298": "ECE298 - Instrumentation Lab",
}

SYSTEM_PROMPT = """You are an expert note transcriber for a computer engineering student at the University of Waterloo.

You will be given an image of a handwritten lecture note page. Your job is to:
1. Extract ALL content — text, equations, diagrams descriptions, bullet points
2. Format it as clean structured markdown
3. For diagrams you cannot fully represent in text, write [DIAGRAM: brief description of what it shows]
4. For equations, use proper markdown math notation where possible
5. Preserve the logical structure and flow of the notes
6. Do not add anything that isn't in the notes
7. Do not summarize — capture everything

Output only the markdown content, no preamble."""

TITLE_SYSTEM_PROMPT = "Given these lecture notes, generate a short descriptive title of 3-6 words that captures the main topic. Return only the title, nothing else."

def image_to_base64(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

def extract_page(image_path: Path) -> str:
    print(f"  Reading {image_path.name}...")
    image_data = image_to_base64(image_path)

    response = httpx.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 4096,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            },
                        },
                        {
                            "type": "text",
                            "text": "Please transcribe this lecture note page into clean markdown."
                        }
                    ],
                }
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def generate_notes_title(notes_content: str) -> str:
    response = httpx.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 64,
            "messages": [
                {"role": "system", "content": TITLE_SYSTEM_PROMPT},
                {"role": "user", "content": notes_content},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    title = response.json()["choices"][0]["message"]["content"].strip()
    return title.replace("\n", " ")

def process_pdf(pdf_path: str, course_code: str, lecture_number: str):
    course_code = course_code.upper()
    if course_code not in COURSE_FOLDERS:
        print(f"Error: Unknown course {course_code}. Options: {', '.join(COURSE_FOLDERS.keys())}")
        sys.exit(1)

    # convert PDF to images
    image_paths = convert_pdf_to_images(pdf_path)

    # extract each page
    print(f"Extracting notes with Gemini Flash...")
    all_pages = []
    for image_path in image_paths:
        page_content = extract_page(image_path)
        all_pages.append(page_content)

    # merge all pages into one markdown file
    lecture_num = lecture_number.zfill(2)
    pdf_name = Path(pdf_path).stem
    now = datetime.now()
    display_date = f"{now.strftime('%B')} {now.day}, {now.year}"
    filename_date = now.strftime("%b").lower() + f"{now.day:02d}"
    pages_merged_content = "\n\n---\n\n".join(all_pages)

    notes_title = generate_notes_title(pages_merged_content)

    merged_content = f"# {course_code} — Lecture {lecture_num} ({display_date})\n\n"
    merged_content += f"## {notes_title}\n\n"
    merged_content += f"**Course**: {COURSE_FOLDERS[course_code]}\n"
    merged_content += f"**Source**: {pdf_name}\n\n"
    merged_content += "---\n\n"
    merged_content += pages_merged_content

    # save to Obsidian vault
    course_folder = OBSIDIAN_VAULT / COURSE_FOLDERS[course_code]
    course_folder.mkdir(parents=True, exist_ok=True)

    output_path = course_folder / f"lecture-{lecture_num}-{filename_date}.md"
    output_path.write_text(merged_content, encoding="utf-8")

    print(f"\n✓ Saved to Obsidian: {output_path}")
    print(f"  {len(image_paths)} pages processed")

    # cleanup temp images
    import shutil
    shutil.rmtree(Path("temp_images") / Path(pdf_path).stem, ignore_errors=True)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python extract_notes.py <path_to_pdf> <course_code> <lecture_number>")
        print("Example: python extract_notes.py ~/Desktop/lecture3.pdf ECE252 03")
        sys.exit(1)

    process_pdf(sys.argv[1], sys.argv[2], sys.argv[3])
