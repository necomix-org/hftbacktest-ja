import json
from pathlib import Path

TARGET_DIR = Path("examples_json")
TARGET_GLOB = "*.json"
DEST_DIR = Path("examples")


def main():
    for child in TARGET_DIR.glob(TARGET_GLOB):
        assert child.is_file()

        notebook_json_content = json.loads(child.read_bytes())
        dest_file = DEST_DIR / f"{child.stem}.ipynb"
        notebook_content = json.loads(dest_file.read_bytes())

        for cell_obj in notebook_json_content:
            notebook_content["cells"][cell_obj["index"]]["source"] = cell_obj["source"]

        data = json.dumps(notebook_content, indent=1, ensure_ascii=False)
        dest_file.write_text(f"{data}\n")


if __name__ == "__main__":
    main()
