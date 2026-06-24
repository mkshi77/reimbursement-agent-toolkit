import argparse
import re

from lib_reimbursement import normalize_record, read_json, write_json


CATEGORY_KEYWORDS = [
    ("non_reimbursable", ["红包", "转账", "收入", "退款", "微信零钱", "理财", "充值", "withdraw", "refund", "transfer"]),
    ("intercity_transport", ["高铁", "动车", "火车", "铁路", "机票", "航班", "机场", "train", "flight", "railway"]),
    ("local_transport", ["滴滴", "出租", "打车", "网约车", "地铁", "公交", "taxi", "didi", "uber", "metro"]),
    ("lodging", ["酒店", "宾馆", "住宿", "旅店", "hotel", "lodging", "inn"]),
    ("meals", ["餐", "饭", "咖啡", "美团", "饿了么", "restaurant", "meal", "coffee"]),
    ("communication", ["话费", "流量", "通信", "快递", "邮费", "mobile", "phone", "postage"]),
    ("office", ["办公", "文具", "打印", "复印", "office", "stationery", "printing"]),
    ("meeting", ["会议", "会务", "培训", "签到", "meeting", "training"]),
    ("entertainment", ["接待", "招待", "宴请", "banquet", "reception"]),
    ("procurement", ["采购", "材料", "设备", "合同", "验收", "purchase", "asset"]),
]

KNOWN_CATEGORIES = {
    "intercity_transport",
    "local_transport",
    "lodging",
    "meals",
    "office",
    "communication",
    "meeting",
    "entertainment",
    "procurement",
    "payment_record",
    "approval_material",
    "other",
    "non_reimbursable",
}


def detect_category(record):
    text = " ".join(
        str(record.get(k, ""))
        for k in ["merchant", "seller_name", "note", "reason", "source_file", "category"]
    ).lower()
    for category, keywords in CATEGORY_KEYWORDS[:1]:
        if any(keyword.lower() in text for keyword in keywords):
            return category
    existing = str(record.get("category") or "").strip()
    if existing in KNOWN_CATEGORIES:
        return existing
    for category, keywords in CATEGORY_KEYWORDS[1:]:
        if any(keyword.lower() in text for keyword in keywords):
            return category
    evidence = record.get("evidence_type", "")
    if evidence == "payment_record":
        return "payment_record"
    return record.get("category") or "other"


def classify(record, low_confidence_threshold=0.8):
    record = normalize_record(record)
    warnings = list(record.get("warnings") or [])
    category = detect_category(record)
    amount = record.get("amount")
    confidence = float(record.get("confidence") or 0)

    if record.get("category") and record.get("category") == category:
        confidence = max(confidence, 0.75)
    if category != "other" and not record.get("category"):
        confidence = max(confidence, 0.72)
    if amount is not None:
        confidence = max(confidence, 0.55)
    if "vision_required" in warnings:
        confidence = 0

    suggested = "include"
    reason = "Likely reimbursable."
    if category == "non_reimbursable":
        suggested = "exclude"
        reason = "Likely transfer, refund, income, or private item."
    elif "vision_required" in warnings:
        suggested = "review"
        reason = "Needs OCR/vision extraction before reimbursement."
    elif amount is None:
        suggested = "review"
        reason = "Missing amount."
        warnings.append("missing_amount")
    elif confidence < low_confidence_threshold:
        suggested = "review"
        reason = "Low confidence classification."
        warnings.append("low_confidence")
    elif record.get("evidence_type") in {"payment_record", "text"} and not record.get("invoice_number"):
        suggested = "review"
        reason = "Payment proof may need matching invoice."
        warnings.append("payment_only_or_no_invoice")

    record.update(
        {
            "category": category,
            "confidence": round(min(max(confidence, 0), 1), 2),
            "suggested_action": suggested,
            "included": suggested == "include",
            "reason": record.get("reason") or reason,
            "warnings": sorted(set(warnings)),
        }
    )
    return record


def main():
    parser = argparse.ArgumentParser(description="Classify extracted reimbursement records.")
    parser.add_argument("--input", required=True, help="Extracted claim JSON.")
    parser.add_argument("--output", required=True, help="Output classified claim JSON.")
    parser.add_argument("--low-confidence-threshold", type=float, default=0.8)
    args = parser.parse_args()
    data = read_json(args.input)
    records = [classify(r, args.low_confidence_threshold) for r in data.get("records", [])]
    data["records"] = records
    write_json(args.output, data)


if __name__ == "__main__":
    main()
