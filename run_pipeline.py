"""
สคริปต์นี้รัน pipeline ตรวจจับป้ายทะเบียนทั้งหมดในคำสั่งเดียว โดยเรียก 3 สคริปต์ตามลำดับ:
1. license_plate_crop/detect_and_crop.py - ตรวจจับ + crop ป้ายทะเบียนด้วย YOLOv8
2. license_plate_ocr/ocr_plate.py        - อ่านข้อความบนป้ายด้วย Tesseract OCR
3. license_plate_match/clean_and_match.py - ทำความสะอาดข้อความ + match ชื่อจังหวัด
"""

import importlib.util
from pathlib import Path

# ============================================================
# ขั้นตอนที่ 1: ตั้งค่า path ไปยังแต่ละสคริปต์
# ============================================================

BASE_DIR = Path(__file__).parent
CROP_SCRIPT = BASE_DIR / "license_plate_crop" / "detect_and_crop.py"
OCR_SCRIPT = BASE_DIR / "license_plate_ocr" / "ocr_plate.py"
MATCH_SCRIPT = BASE_DIR / "license_plate_match" / "clean_and_match.py"


# ============================================================
# ขั้นตอนที่ 2: ฟังก์ชันสำหรับโหลดสคริปต์อีกไฟล์มารัน (เหมือนกดรัน python script.py)
# ============================================================

def run_script(script_path):
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)   # โหลดโค้ดในไฟล์นั้นเข้ามา
    module.main()                     # แล้วเรียกฟังก์ชัน main() ของไฟล์นั้น


# ============================================================
# ขั้นตอนที่ 3: รันทั้ง 3 ขั้นตอนตามลำดับ
# ============================================================

def main():
    print("=== ขั้นตอนที่ 1: ตรวจจับ + Crop ป้ายทะเบียน (YOLOv8) ===")
    run_script(CROP_SCRIPT)

    print("\n=== ขั้นตอนที่ 2: OCR อ่านข้อความป้ายทะเบียน (Tesseract) ===")
    run_script(OCR_SCRIPT)

    print("\n=== ขั้นตอนที่ 3: Data Cleaning & Matching ===")
    run_script(MATCH_SCRIPT)

    print("\nเสร็จสิ้น ผลลัพธ์สุดท้ายอยู่ที่ license_plate_match/output_data/plates_matched.csv")


if __name__ == "__main__":
    main()
