import os
import argparse
import json
import nest_asyncio
from pathlib import Path
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

load_dotenv()
nest_asyncio.apply()

def parse_pdf(input_path, output_format="markdown", output_dir=None, language="ko"):

    if not os.path.exists(input_path):
        print(f"Error: File not found at {input_path}")
        return

    print(f"Parsing {input_path}...")
    
    parser = LlamaParse(
        result_type=output_format if output_format == "markdown" else "text", # internal result type
        num_workers=8,
        verbose=True,
        language=language,
    )

    file_extractor = {".pdf": parser}
    
    documents = SimpleDirectoryReader(
        input_files=[input_path],
        file_extractor=file_extractor,
    ).load_data()

    output_content = ""
    if output_format == "json":
        docs_data = []
        for doc in documents:
            docs_data.append({
                "text": doc.text,
                "metadata": doc.metadata
            })
        output_content = json.dumps(docs_data, ensure_ascii=False, indent=2)
    else:
        output_content = "\n\n".join([doc.text for doc in documents])

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    ext = "json" if output_format == "json" else "md"
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{base_name}.{ext}")
    else:
        input_dir = os.path.dirname(input_path)
        output_path = os.path.join(input_dir, f"{base_name}.{ext}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_content)
        
    print(f"Successfully saved parsed content to {output_path}")

def process_directory(input_dir, output_format="markdown", output_dir=None, language="ko"):
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"Error: Directory not found at {input_dir}")
        return
    
    if not input_path.is_dir():
        print(f"Error: {input_dir} is not a directory")
        return
    
    pdf_files = list(input_path.glob("*.pdf"))
    total = len(pdf_files)
    
    if total == 0:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {total} PDF files to process\n")
    
    success_count = 0
    error_count = 0
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        try:
            print(f"\n[{idx}/{total}] Processing: {pdf_file.name}")
            parse_pdf(str(pdf_file), output_format, output_dir, language)
            success_count += 1
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {str(e)}")
            error_count += 1
            continue
    
    print(f"Processing complete: {success_count} succeeded, {error_count} failed")

def main():
    parser = argparse.ArgumentParser(description="Parse PDF files using LlamaParse.")
    parser.add_argument("input_path", help="Path to the input PDF file or directory containing PDF files")
    parser.add_argument("--output_format", choices=["markdown", "json"], default="markdown", help="Output format (markdown or json)")
    parser.add_argument("--output_dir", help="Directory to save the output file(s)", default=None)
    parser.add_argument("--language", help="Language code (e.g., ko, en)", default="ko")

    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    
    if input_path.is_dir():
        process_directory(args.input_path, args.output_format, args.output_dir, args.language)
    elif input_path.is_file():
        parse_pdf(args.input_path, args.output_format, args.output_dir, args.language)
    else:
        print(f"Error: {args.input_path} is neither a file nor a directory")

if __name__ == "__main__":
    main()
