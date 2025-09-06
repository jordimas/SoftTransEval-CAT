import json
import sys
from pathlib import Path

# Check for command-line argument
if len(sys.argv) < 2:
    print("Usage: python json_to_md.py <path_to_json_file>")
    sys.exit(1)

json_path = Path(sys.argv[1])

# Ensure file exists
if not json_path.is_file():
    print(f"File not found: {json_path}")
    sys.exit(1)

# Load JSON data
with open(json_path, "r") as f:
    data = json.load(f)

# Validate JSON structure
if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
    raise ValueError("Input JSON must be a list of objects")

# Extract headers
headers = list(data[0].keys())

# Build Markdown table
md_lines = []
md_lines.append("| " + " | ".join(headers) + " |")
md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

for row in data:
    md_lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")

# Determine output Markdown file path
md_path = json_path.with_suffix(".md")

# Write to Markdown file
with open(md_path, "w") as f:
    f.write("\n".join(md_lines))

print(f"Markdown table written to {md_path}")
