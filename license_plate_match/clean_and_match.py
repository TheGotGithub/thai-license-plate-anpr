"""
Data Cleaning & Matching

สคริปต์นี้ทำ 3 อย่าง:
1. รับข้อความดิบจาก OCR (license_plate_ocr) มาทำความสะอาด ตัดสัญลักษณ์รบกวนทิ้ง
2. แยกข้อความออกเป็น 2 ส่วน คือ "เลขทะเบียน" กับ "จังหวัด"
3. เทียบชื่อจังหวัดกับรายชื่อ 77 จังหวัดจริงของไทย เพื่อแก้กรณี OCR อ่านตัวอักษรเพี้ยนเล็กน้อย
"""

import csv
import re
import difflib
from pathlib import Path

# ============================================================
# ขั้นตอนที่ 1: ตั้งค่าตัวแปรต่างๆ ที่จะใช้ในสคริปต์
# ============================================================

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR.parent / "license_plate_ocr" / "output_text" / "plate_texts.csv"
PROVINCE_LIST_FILE = BASE_DIR / "provinces_th.txt"
OUTPUT_FILE = BASE_DIR / "output_data" / "plates_matched.csv"

MATCH_CUTOFF = 0.6   # ความคล้ายขั้นต่ำ (0-1) ที่ยอมรับว่า match กับชื่อจังหวัด

# รูปแบบเลขทะเบียนไทย: พยัญชนะไทย 1-3 ตัว ตามด้วยตัวเลข 1-4 หลัก เช่น "กท 1234"
PLATE_NUMBER_PATTERN = re.compile(r"[ก-ฮ]{1,3}\s?\d{1,4}")


# ============================================================
# ขั้นตอนที่ 2: โหลดรายชื่อ 77 จังหวัดจากไฟล์ provinces_th.txt
# ============================================================

def load_provinces():
    provinces = []
    for line in PROVINCE_LIST_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            provinces.append(line)
    return provinces


# ============================================================
# ขั้นตอนที่ 3: ทำความสะอาดข้อความ 1 ท่อน (ตัดสัญลักษณ์รบกวนทิ้ง)
# ============================================================

def clean_segment(text):
    # เก็บเฉพาะตัวอักษรไทย ตัวเลข และเว้นวรรค ตัดสัญลักษณ์อื่นๆ ที่ OCR อ่านผิดพลาดทิ้ง
    text = re.sub(r"[^ก-๏0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# ขั้นตอนที่ 4: หา "เลขทะเบียน" จากข้อความที่ทำความสะอาดแล้ว
# ============================================================

def extract_plate_number(segments):
    for segment in segments:
        match = PLATE_NUMBER_PATTERN.search(segment)
        if match:
            return match.group().strip()
    return ""


# ============================================================
# ขั้นตอนที่ 5: หา "จังหวัด" ที่ใกล้เคียงที่สุดจากข้อความที่ทำความสะอาดแล้ว
# ============================================================

def match_province(segments, provinces):
    best_name = ""
    best_score = 0.0

    for segment in segments:
        # difflib.get_close_matches หาชื่อจังหวัดที่สะกดใกล้เคียงกับ segment มากที่สุด
        candidates = difflib.get_close_matches(segment, provinces, n=1, cutoff=MATCH_CUTOFF)
        if not candidates:
            continue

        best_candidate = candidates[0]
        score = difflib.SequenceMatcher(None, segment, best_candidate).ratio()
        if score > best_score:
            best_name = best_candidate
            best_score = score

    return best_name, round(best_score, 2)


# ============================================================
# ขั้นตอนที่ 6: อ่านผลลัพธ์ OCR ของภาพ 1 แถว มาทำความสะอาด + match จังหวัด
# ============================================================

def process_row(row, provinces):
    raw_segments = row["raw_text"].split("|")

    segments = []
    for raw_segment in raw_segments:
        cleaned = clean_segment(raw_segment)
        if cleaned:
            segments.append(cleaned)

    plate_number = extract_plate_number(segments)
    province, score = match_province(segments, provinces)
    return plate_number, province, score


# ============================================================
# ขั้นตอนที่ 7: รันทุกขั้นตอนข้างบนตามลำดับ แล้วบันทึกผลลัพธ์เป็น CSV
# ============================================================

def main():
    provinces = load_provinces()

    with open(INPUT_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "plate_number", "province", "province_match_score"])

        for row in rows:
            plate_number, province, score = process_row(row, provinces)
            print(f"{row['image']}: เลขทะเบียน={plate_number!r} จังหวัด={province!r} ({score})")
            writer.writerow([row["image"], plate_number, province, score])


if __name__ == "__main__":
    main()
