import csv
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".heic"}
DOCUMENT_EXTENSIONS = {".pdf", ".ofd"}
SPREADSHEET_EXTENSIONS = {".csv", ".xlsx", ".xlsm", ".xls"}
TEXT_EXTENSIONS = {".txt", ".md"}
DATA_EXTENSIONS = {".json", ".jsonl"}


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    ensure_parent(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ensure_parent(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def load_yaml_or_json(path):
    if not path:
        return {}
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return read_json(path)
    try:
        import yaml
    except Exception as exc:
        raise RuntimeError("YAML input requires PyYAML. Use JSON instead or install PyYAML.") from exc
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_kind(path):
    ext = Path(path).suffix.lower()
    name = Path(path).name.lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in DOCUMENT_EXTENSIONS:
        return "document"
    if ext in SPREADSHEET_EXTENSIONS:
        return "spreadsheet"
    if ext in TEXT_EXTENSIONS:
        return "text"
    if ext in DATA_EXTENSIONS:
        return "data"
    if any(token in name for token in ["invoice", "发票", "receipt", "票据"]):
        return "possible_receipt"
    return "unknown"


def stable_id(*parts):
    raw = "|".join("" if p is None else str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def parse_amount(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    text = str(value).replace(",", "")
    match = re.search(r"[-+]?\d+(?:\.\d{1,2})?", text)
    if not match:
        return None
    return round(float(match.group(0)), 2)


def normalize_date(value):
    if not value:
        return ""
    text = str(value).strip()
    patterns = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%Y年%m月%d日",
        "%m/%d/%Y",
    ]
    for pattern in patterns:
        try:
            return datetime.strptime(text, pattern).strftime("%Y-%m-%d")
        except ValueError:
            pass
    match = re.search(r"(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})", text)
    if match:
        y, m, d = match.groups()
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
    return text


def read_csv_records(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    ensure_parent(path)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def material_display_path(path, root=None):
    try:
        if root:
            return str(Path(path).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        pass
    return str(path)


def nested_get(data, dotted):
    current = data
    for part in dotted.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def normalize_record(raw, source_file="", default_evidence_type="unknown"):
    record = dict(raw or {})
    source = record.get("source_file") or source_file
    amount = parse_amount(record.get("amount"))
    date = normalize_date(record.get("date"))
    invoice_number = str(record.get("invoice_number") or record.get("ticket_number") or "").strip()
    merchant = str(record.get("merchant") or record.get("seller_name") or record.get("route") or "").strip()
    record.update(
        {
            "id": str(record.get("id") or stable_id(source, date, merchant, amount, invoice_number)),
            "source_file": str(source),
            "date": date,
            "merchant": merchant,
            "amount": amount,
            "currency": record.get("currency") or "CNY",
            "category": record.get("category") or "",
            "invoice_number": invoice_number,
            "evidence_type": record.get("evidence_type") or default_evidence_type,
            "confidence": float(record.get("confidence") or 0),
            "suggested_action": record.get("suggested_action") or "review",
            "warnings": list(record.get("warnings") or []),
        }
    )
    return record


def category_label(category):
    labels = {
        "intercity_transport": "Intercity transport",
        "local_transport": "Local transport",
        "lodging": "Lodging",
        "meals": "Meals",
        "office": "Office",
        "communication": "Communication",
        "meeting": "Meeting",
        "entertainment": "Entertainment",
        "procurement": "Procurement",
        "payment_record": "Payment record",
        "approval_material": "Approval material",
        "other": "Other",
        "non_reimbursable": "Non reimbursable",
    }
    return labels.get(category, category or "Unclassified")


def safe_filename(name):
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "_", str(name or "file"))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:160] or "file"

