"""
อ่านข้อความจากภาพป้ายทะเบียน (ที่ crop มาแล้ว) ด้วย Tesseract OCR รองรับภาษาไทย
"""

from pathlib import Path
import csv
import cv2
import pytesseract

# ---------- ตั้งค่า ----------
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR.parent / "license_plate_crop" / "output_crops"   # ภาพที่ crop มาจากขั้นตอนก่อนหน้า
OUTPUT_FILE = BASE_DIR / "output_text" / "plate_texts.csv"
LANG = "tha+eng"                        # อ่านทั้งภาษาไทยและอังกฤษ (ตัวเลขบนป้าย)
TESSERACT_CONFIG = "--psm 11"           # sparse text: อ่านได้ทั้งบรรทัดเลขและบรรทัดจังหวัด

# ตัดขอบดำ/รอยสกรูของป้ายออก (มักทำให้ OCR อ่านตัวอักษรแถวบนพลาด) แล้วขยายภาพให้ตัวหนังสือคมขึ้น
CROP_RATIO_Y, CROP_RATIO_X = 0.18, 0.10
UPSCALE = 3

def preprocess(image_path):
    img = cv2.imread(str(image_path))
    h, w = img.shape[:2]
    pad_y, pad_x = int(h * CROP_RATIO_Y), int(w * CROP_RATIO_X)
    inner = img[pad_y:h - pad_y, pad_x:w - pad_x]

    gray = cv2.cvtColor(inner, cv2.COLOR_BGR2GRAY)
    ih, iw = gray.shape
    return cv2.resize(gray, (iw * UPSCALE, ih * UPSCALE), interpolation=cv2.INTER_CUBIC)

def main():
    image_paths = [
        p for p in INPUT_DIR.iterdir()
        if p.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "raw_text"])
        for img_path in image_paths:
            processed = preprocess(img_path)
            text = pytesseract.image_to_string(processed, lang=LANG, config=TESSERACT_CONFIG).strip()
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            raw_text = " | ".join(lines)   # รวมหลายบรรทัด (เลขทะเบียน/จังหวัด) เป็นบรรทัดเดียวต่อภาพ
            print(f"{img_path.name}: {raw_text}")
            writer.writerow([img_path.name, raw_text])

if __name__ == "__main__":
    main()
