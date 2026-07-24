from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def read_topics_xlsx(path: str | Path) -> list[tuple[str, str]]:
    """Read the supplied single-column XLSX without an Excel runtime."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    with zipfile.ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(si.itertext()) for si in root]
        sheet_name = "xl/worksheets/sheet1.xml"
        root = ET.fromstring(archive.read(sheet_name))
        values: dict[int, str] = {}
        for cell in root.iter():
            if not cell.tag.endswith("}c"):
                continue
            ref = cell.attrib.get("r", "")
            if not ref.startswith("A"):
                continue
            row_match = re.search(r"\d+", ref)
            if not row_match:
                continue
            value_node = next((n for n in cell if n.tag.endswith("}v")), None)
            inline_node = next((n for n in cell if n.tag.endswith("}is")), None)
            if value_node is not None and value_node.text is not None:
                value = shared[int(value_node.text)] if cell.attrib.get("t") == "s" else value_node.text
            elif inline_node is not None:
                value = "".join(inline_node.itertext())
            else:
                value = ""
            values[int(row_match.group())] = value.strip()
    topics = [(f"A{row}", values[row]) for row in range(3, 34) if values.get(row)]
    if len(topics) != 31:
        raise ValueError(f"Expected 31 topics in A3:A33, got {len(topics)}")
    return topics
