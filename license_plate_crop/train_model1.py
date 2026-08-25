"""
เทรน YOLOv8 (Model 1) สำหรับตรวจจับตำแหน่งป้ายทะเบียน
ใช้ dataset ที่ดาวน์โหลดมาจาก Roboflow Universe (รูปแบบ YOLOv8)
"""

from pathlib import Path
from ultralytics import YOLO

# ---------- ตั้งค่า ----------
BASE_DIR = Path(__file__).parent
DATA_YAML = BASE_DIR / "dataset" / "data.yaml"   # ไฟล์ data.yaml ที่มากับ dataset จาก Roboflow
BASE_MODEL = "yolov8n.pt"                        # โมเดลตั้งต้น (จะดาวน์โหลดอัตโนมัติครั้งแรกที่รัน)
EPOCHS = 50
IMG_SIZE = 640

def main():
    model = YOLO(BASE_MODEL)
    model.train(data=DATA_YAML, epochs=EPOCHS, imgsz=IMG_SIZE)
    # โมเดลที่เทรนเสร็จจะถูกบันทึกไว้ที่ runs/detect/train/weights/best.pt
    # ให้คัดลอกไฟล์นั้นไปไว้ที่ models/model1_plate_detect.pt เพื่อใช้กับ detect_and_crop.py

if __name__ == "__main__":
    main()
