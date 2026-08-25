"""
Data Cleaning & Matching
รับข้อความดิบจาก OCR (license_plate_ocr) มาทำความสะอาด แยกเป็นเลขทะเบียน + จังหวัด
แล้ว match ชื่อจังหวัดกับรายชื่อ 77 จังหวัดจริงของไทย (แก้ OCR อ่านเพี้ยนเล็กน้อยด้วย fuzzy match)
"""

import csv
import re
import difflib
from pathlib import Path

# ---------- ตั้งค่า ----------
BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR.parent / "license_plate_ocr" / "output_text" / "plate_texts.csv"
PROVINCE_LIST_FILE = BASE_DIR / "provinces_th.txt"
OUTPUT_FILE = BASE_DIR / "output_data" / "plates_matched.csv"
MATCH_CUTOFF = 0.6   # ความคล้ายขั้นต่ำ (0-1) ที่ยอมรับว่า match กับชื่อจังหวัด

PLATE_NUMBER_PATTERN = re.compile(r"[ก-ฮ]{1,3}\s?\d{1,4}")

def clean_segment(text):
    # เก็บเฉพาะตัวอักษรไทย ตัวเลข และเว้นวรรค ตัดสัญลักษณ์รบกวนจาก OCR ทิ้ง
    text = re.sub(r"[^ก-๏0-9\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()

def extract_plate_number(segments):
    for seg in segments:
        match = PLATE_NUMBER_PATTERN.search(seg)
        if match:
            return match.group().strip()
    return ""

def match_province(segments, provinces):
    best_name, best_score = "", 0.0
    for seg in segments:
        candidates = difflib.get_close_matches(seg, provinces, n=1, cutoff=MATCH_CUTOFF)
        if candidates:
            score = difflib.SequenceMatcher(None, seg, candidates[0]).ratio()
            if score > best_score:
                best_name, best_score = candidates[0], score
    return best_name, round(best_score, 2)

def main():
    provinces = [p.strip() for p in PROVINCE_LIST_FILE.read_text(encoding="utf-8").splitlines() if p.strip()]

    with open(INPUT_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "plate_number", "province", "province_match_score"])

        for row in rows:
            segments = [clean_segment(s) for s in row["raw_text"].split("|")]
            segments = [s for s in segments if s]

            plate_number = extract_plate_number(segments)
            province, score = match_province(segments, provinces)

            print(f"{row['image']}: เลขทะเบียน={plate_number!r} จังหวัด={province!r} ({score})")
            writer.writerow([row["image"], plate_number, province, score])

if __name__ == "__main__":
    main()
