import json
import sys
from pathlib import Path

def load_json(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
        raise ValueError("Input JSON must be a list of objects")
    return data

def build_md_table(data: list[dict], headers: list[str]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |"
    ]
    for row in data:
        lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
    return "\n".join(lines)

def save_md(content: str, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    if len(sys.argv) < 2:
        print("Usage: python json_to_md.py <path_to_json_file>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    data = load_json(json_path)

    # Full version
    all_headers = list(data[0].keys())
    full_md = build_md_table(data, all_headers)
    save_md(full_md, json_path.with_suffix(".md"))
    print(f"Full Markdown table written to {json_path.with_suffix('.md')}")

    small_headers = [h for h in all_headers if h not in ["date_time", "strings"]]
    if small_headers:
        small_md = build_md_table(data, small_headers)
        save_md(small_md, json_path.with_name(json_path.stem + "_small.md"))
        print(f"Small Markdown table written to {json_path.with_name(json_path.stem + '_small.md')}")
    else:
        print("No columns A, B, C found in JSON. Skipping small version.")

if __name__ == "__main__":
    main()

