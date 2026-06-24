import argparse
import os
from pathlib import Path

from lib_reimbursement import file_kind, file_sha256, material_display_path, write_json


def scan(input_path):
    root = Path(input_path).resolve()
    files = []
    if root.is_file():
        paths = [root]
        base = root.parent
    else:
        paths = [Path(dirpath) / name for dirpath, _, names in os.walk(root) for name in names]
        base = root
    for path in sorted(paths):
        if not path.is_file():
            continue
        stat = path.stat()
        files.append(
            {
                "path": str(path.resolve()),
                "relative_path": material_display_path(path, base),
                "name": path.name,
                "extension": path.suffix.lower(),
                "kind": file_kind(path),
                "size_bytes": stat.st_size,
                "sha256": file_sha256(path),
            }
        )
    return {"input": str(root), "file_count": len(files), "files": files}


def main():
    parser = argparse.ArgumentParser(description="Scan reimbursement material files.")
    parser.add_argument("--input", required=True, help="Material folder or file.")
    parser.add_argument("--output", required=True, help="Output materials JSON.")
    args = parser.parse_args()
    write_json(args.output, scan(args.input))


if __name__ == "__main__":
    main()

