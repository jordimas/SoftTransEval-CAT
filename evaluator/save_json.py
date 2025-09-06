import json
import os
from datetime import datetime


def save_json(
    prompt_version,
    prompt_comment,
    tp,
    fp,
    fn,
    tn,
    precision,
    recall,
    f1,
    total_time,
    processed,
):
    json_path = f"output/stats_{processed}.json"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = {
        "date_time": now,
        "prompt_version": prompt_version,
        "prompt_comment": prompt_comment,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1": round(f1, 2),
        "total_time": round(total_time, 2),
        "strings": processed,
    }

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as fh:
            try:
                data = json.load(fh)
                if not isinstance(data, list):
                    data = [data]  # ensure it's always a list
            except json.JSONDecodeError:
                data = []
        data.append(record)
    else:
        data = [record]

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
