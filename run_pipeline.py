"""
รัน pipeline ตรวจจับป้ายทะเบียนทั้งหมดในคำสั่งเดียว:
1. license_plate_crop  - ตรวจจับ + crop ป้ายทะเบียนด้วย YOLOv8
2. license_plate_ocr   - อ่านข้อความบนป้ายด้วย Tesseract OCR
3. license_plate_match - ทำความสะอาดข้อความ + match ชื่อจังหวัด
"""

import importlib.util
from pathlib import Path

BASE_DIR = Path(__file__).parent

def run_script(script_path):
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()

def main():
    print("=== ขั้นตอน 1: ตรวจจับ + Crop ป้ายทะเบียน (YOLOv8) ===")
    run_script(BASE_DIR / "license_plate_crop" / "detect_and_crop.py")

    print("\n=== ขั้นตอน 2: OCR อ่านข้อความป้ายทะเบียน (Tesseract) ===")
    run_script(BASE_DIR / "license_plate_ocr" / "ocr_plate.py")

    print("\n=== ขั้นตอน 3: Data Cleaning & Matching ===")
    run_script(BASE_DIR / "license_plate_match" / "clean_and_match.py")

    print("\nเสร็จสิ้น ผลลัพธ์สุดท้ายอยู่ที่ license_plate_match/output_data/plates_matched.csv")

if __name__ == "__main__":
    main()
