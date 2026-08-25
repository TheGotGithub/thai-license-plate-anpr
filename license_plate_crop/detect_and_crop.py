"""
สคริปต์นี้ทำ 3 อย่าง:
1. โหลดโมเดล YOLOv8 ที่เทรนมาสำหรับตรวจจับป้ายทะเบียน
2. ใช้โมเดลตรวจจับว่าป้ายทะเบียนอยู่ตรงไหนในแต่ละภาพ
3. ตัด (crop) เฉพาะส่วนป้ายทะเบียนออกมาเป็นภาพใหม่ แล้วบันทึกไฟล์
"""

from pathlib import Path
from ultralytics import YOLO
from PIL import Image

# ============================================================
# ขั้นตอนที่ 1: ตั้งค่าตัวแปรต่างๆ ที่จะใช้ในสคริปต์
# ============================================================

BASE_DIR = Path(__file__).parent                              # โฟลเดอร์ที่ไฟล์นี้อยู่
MODEL_PATH = BASE_DIR / "models" / "model1_plate_detect.pt"    # ไฟล์โมเดล YOLOv8
INPUT_DIR = BASE_DIR / "input_images"                          # โฟลเดอร์เก็บภาพต้นฉบับ
OUTPUT_DIR = BASE_DIR / "output_crops"                         # โฟลเดอร์เก็บภาพที่ตัดป้ายทะเบียนแล้ว
CONF_THRESHOLD = 0.5                                            # ความมั่นใจขั้นต่ำที่ยอมรับว่าเจอป้ายจริง (ค่า 0-1)


# ============================================================
# ขั้นตอนที่ 2: โหลดโมเดล YOLOv8
# ============================================================

def load_model():
    print("กำลังโหลดโมเดล...")
    return YOLO(MODEL_PATH)


# ============================================================
# ขั้นตอนที่ 3: หารายชื่อไฟล์ภาพทั้งหมดในโฟลเดอร์ input_images
# ============================================================

def get_image_files():
    image_files = []
    for file in INPUT_DIR.iterdir():
        if file.suffix.lower() in (".jpg", ".jpeg", ".png"):
            image_files.append(file)
    return image_files


# ============================================================
# ขั้นตอนที่ 4: ตรวจจับป้ายทะเบียนในภาพ 1 ภาพ แล้วตัดออกมาเป็นไฟล์ใหม่
# ============================================================

def detect_and_crop(model, image_path):
    # 4.1 ให้โมเดลตรวจจับตำแหน่งป้ายทะเบียนในภาพ
    results = model.predict(source=str(image_path), conf=CONF_THRESHOLD, verbose=False)
    boxes = results[0].boxes.xyxy.tolist()   # ตำแหน่งกรอบป้ายที่เจอ แต่ละกรอบคือ [x1, y1, x2, y2]

    # 4.2 เปิดภาพต้นฉบับขึ้นมาเตรียมตัด
    original_image = Image.open(image_path)

    # 4.3 ตัดภาพตามกรอบที่เจอทีละกรอบ (ถ้าเจอหลายป้ายในภาพเดียวจะได้หลายไฟล์)
    for index, (x1, y1, x2, y2) in enumerate(boxes):
        cropped_image = original_image.crop((x1, y1, x2, y2))

        output_name = f"{image_path.stem}_plate_{index}.jpg"
        cropped_image.save(OUTPUT_DIR / output_name)
        print(f"  บันทึกแล้ว: {output_name}")


# ============================================================
# ขั้นตอนที่ 5: รันทุกขั้นตอนข้างบนตามลำดับ
# ============================================================

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)   # สร้างโฟลเดอร์ output ถ้ายังไม่มี

    model = load_model()
    image_files = get_image_files()
    print(f"พบภาพทั้งหมด {len(image_files)} ไฟล์\n")

    for image_path in image_files:
        print(f"กำลังประมวลผล: {image_path.name}")
        detect_and_crop(model, image_path)


if __name__ == "__main__":
    main()
