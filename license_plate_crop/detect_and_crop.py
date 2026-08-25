"""
ตรวจจับตำแหน่งป้ายทะเบียนด้วย YOLOv8 (Model 1) แล้ว crop เฉพาะบริเวณป้ายออกมา
"""

from pathlib import Path
from ultralytics import YOLO
from PIL import Image

# ---------- ตั้งค่า ----------
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "models" / "model1_plate_detect.pt"   # โมเดล YOLOv8 สำหรับตรวจจับป้ายทะเบียน
INPUT_DIR = BASE_DIR / "input_images"               # โฟลเดอร์ภาพต้นฉบับ
OUTPUT_DIR = BASE_DIR / "output_crops"                         # โฟลเดอร์เก็บภาพที่ crop แล้ว
CONF_THRESHOLD = 0.5

def main():
    model = YOLO(MODEL_PATH)
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    image_paths = [
        p for p in Path(INPUT_DIR).iterdir()
        if p.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]

    for img_path in image_paths:
        results = model.predict(source=str(img_path), conf=CONF_THRESHOLD, verbose=False)
        image = Image.open(img_path)

        boxes = results[0].boxes.xyxy.tolist()
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            cropped = image.crop((x1, y1, x2, y2))
            out_name = f"{img_path.stem}_plate_{i}.jpg"
            cropped.save(Path(OUTPUT_DIR) / out_name)
            print(f"บันทึก: {out_name}")

if __name__ == "__main__":
    main()
