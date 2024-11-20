import json
from pathlib import Path

TARGET_DIR = Path("examples")
TARGET_GLOB = "*.ipynb"
DEST_DIR = Path("examples_json")


def main():
    for child in TARGET_DIR.glob(TARGET_GLOB):
        assert child.is_file()

        result = []
        notebook_content = json.loads(child.read_bytes())
        for index, cell in enumerate(notebook_content["cells"]):
            if cell["cell_type"] == "markdown":
                result.append(
                    {
                        "index": index,
                        "source": cell["source"],
                    }
                )

        with (DEST_DIR / f"{child.stem}.json").open("w", encoding="utf-8") as fp:
            json.dump(result, fp, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
