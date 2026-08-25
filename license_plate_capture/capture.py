"""
สคริปต์นี้ทำ 2 อย่าง (รันได้เฉพาะบน Raspberry Pi ที่ต่อกล้อง Pi Camera เท่านั้น):
1. เปิดกล้อง Pi Camera ด้วยไลบรารี picamera2
2. ถ่ายภาพ 1 รูป แล้วบันทึกลงโฟลเดอร์ input_images ของขั้นตอน crop
   เพื่อให้ run_pipeline.py หยิบไปตรวจจับป้ายทะเบียนต่อได้ทันที
"""

import time
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2

# ============================================================
# ขั้นตอนที่ 1: ตั้งค่าตัวแปรต่างๆ ที่จะใช้ในสคริปต์
# ============================================================

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR.parent / "license_plate_crop" / "input_images"   # บันทึกตรงเข้า input ของขั้นตอน crop
RESOLUTION = (2304, 1296)   # ขนาดภาพที่จะถ่าย (กว้าง, สูง) เป็นพิกเซล
WARMUP_SECONDS = 2          # เวลาที่ให้กล้องปรับแสง/โฟกัสก่อนถ่ายจริง


# ============================================================
# ขั้นตอนที่ 2: เปิดกล้อง เตรียมความพร้อม แล้วถ่ายภาพ 1 รูป
# ============================================================

def capture_photo():
    camera = Picamera2()

    # 2.1 ตั้งค่าความละเอียดภาพที่จะถ่าย
    config = camera.create_still_configuration(main={"size": RESOLUTION})
    camera.configure(config)

    # 2.2 เปิดกล้อง แล้วรอสักครู่ให้ปรับแสง/โฟกัสก่อน ไม่งั้นภาพแรกอาจเบลอ/มืดเกินไป
    camera.start()
    time.sleep(WARMUP_SECONDS)

    # 2.3 ตั้งชื่อไฟล์ตามเวลาปัจจุบัน กันชื่อซ้ำ แล้วบันทึกภาพ
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"capture_{timestamp}.jpg"
    camera.capture_file(str(output_path))

    camera.stop()
    print(f"ถ่ายภาพแล้ว: {output_path}")
    return output_path


# ============================================================
# ขั้นตอนที่ 3: รันขั้นตอนข้างบน
# ============================================================

def main():
    capture_photo()


if __name__ == "__main__":
    main()
