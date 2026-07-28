import os
import re

RAW_PATH = os.path.join(os.path.dirname(__file__), "../../skills/raw")
EXTRACTED_PATH = os.path.join(os.path.dirname(__file__), "../../skills/extracted")

RELEVANT_HEADINGS = re.compile(
    r"prompt|image|video|skill|workflow|guide|best practice|structure",
    re.IGNORECASE,
)


def extract_skill(filepath: str) -> str:
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    relevant: list[str] = []
    capture = False
    heading_depth = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        heading_match = re.match(r"^(#+)\s+(.*)", stripped)
        if heading_match:
            depth = len(heading_match.group(1))
            text = heading_match.group(2)
            if RELEVANT_HEADINGS.search(text):
                capture = True
                heading_depth = depth
            else:
                capture = False
            if capture:
                relevant.append(stripped)
            continue

        if capture:
            if re.match(r"^#+", stripped):
                new_depth = len(re.match(r"^#+", stripped).group(0))
                if new_depth <= heading_depth:
                    capture = False
                    continue
            relevant.append(stripped)

    return "\n".join(relevant)


def extract_all() -> None:
    os.makedirs(EXTRACTED_PATH, exist_ok=True)

    if not os.path.isdir(RAW_PATH):
        print(f"Raw path not found: {RAW_PATH}")
        return

    for fname in sorted(os.listdir(RAW_PATH)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(RAW_PATH, fname)
        content = extract_skill(fpath)
        out_name = fname.replace(".md", ".extracted.md")
        out_path = os.path.join(EXTRACTED_PATH, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  -> {out_path} ({len(content)} chars)")


def main():
    print(f"Extracting skills from {RAW_PATH} to {EXTRACTED_PATH}")
    extract_all()
    print("Extraction complete.")


if __name__ == "__main__":
    main()
