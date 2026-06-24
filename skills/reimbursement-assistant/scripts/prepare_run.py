import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


RUN_SUBDIRS = ["raw", "materials", "extracted", "review", "output"]


def unique_target(path):
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def copy_file(source, raw_dir, materials_dir, base=None):
    if base:
        relative = source.relative_to(base)
        raw_target = raw_dir / relative
        material_target = materials_dir / relative
    else:
        raw_target = raw_dir / source.name
        material_target = materials_dir / source.name
    raw_target = unique_target(raw_target)
    material_target = unique_target(material_target)
    raw_target.parent.mkdir(parents=True, exist_ok=True)
    material_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, raw_target)
    shutil.copy2(source, material_target)
    return {
        "source": str(source.resolve()),
        "raw": str(raw_target.resolve()),
        "material": str(material_target.resolve()),
    }


def iter_files(input_path):
    path = Path(input_path).resolve()
    if path.is_file():
        return path, [path]
    if path.is_dir():
        return path, sorted(p for p in path.rglob("*") if p.is_file())
    return path, []


def prepare(inputs, out_root, run_id=None):
    run_name = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path(out_root).resolve() / run_name
    dirs = {name: run_dir / name for name in RUN_SUBDIRS}
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)

    copied = []
    missing = []
    for value in inputs:
        base, files = iter_files(value)
        if not files:
            missing.append(str(base))
            continue
        for file_path in files:
            copied.append(copy_file(file_path, dirs["raw"], dirs["materials"], base if base.is_dir() else None))

    session = {
        "run_id": run_name,
        "run_dir": str(run_dir),
        "raw_dir": str(dirs["raw"]),
        "materials_dir": str(dirs["materials"]),
        "extracted_dir": str(dirs["extracted"]),
        "review_dir": str(dirs["review"]),
        "output_dir": str(dirs["output"]),
        "copied_count": len(copied),
        "copied_files": copied,
        "missing_inputs": missing,
    }
    (run_dir / "session.json").write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
    return session


def main():
    parser = argparse.ArgumentParser(description="Create a reimbursement run folder and copy source materials into it.")
    parser.add_argument("--input", action="append", required=True, help="File or folder to copy. Repeat for multiple inputs.")
    parser.add_argument("--out-root", default="reimbursement-runs", help="Folder that stores timestamped reimbursement runs.")
    parser.add_argument("--run-id", help="Optional run folder name. Defaults to YYYYMMDD-HHMMSS.")
    parser.add_argument("--session", help="Optional path for an extra session JSON copy.")
    args = parser.parse_args()

    session = prepare(args.input, args.out_root, args.run_id)
    if args.session:
        Path(args.session).write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(session, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
