"""
สคริปต์นี้ทำ 3 อย่าง:
1. เตรียมภาพป้ายทะเบียน (ที่ crop มาจากขั้นตอนก่อนหน้า) ให้ Tesseract อ่านง่ายขึ้น
2. ใช้ Tesseract OCR อ่านตัวหนังสือบนป้าย (รองรับภาษาไทย)
3. บันทึกข้อความที่อ่านได้ทั้งหมดลงไฟล์ CSV
"""

from pathlib import Path
import csv
import cv2
import pytesseract

# ============================================================
# ขั้นตอนที่ 1: ตั้งค่าตัวแปรต่างๆ ที่จะใช้ในสคริปต์
# ============================================================

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR.parent / "license_plate_crop" / "output_crops"   # ภาพที่ crop มาจากขั้นตอนก่อนหน้า
OUTPUT_FILE = BASE_DIR / "output_text" / "plate_texts.csv"            # ไฟล์ผลลัพธ์ที่จะบันทึก

LANG = "tha+eng"                # อ่านทั้งภาษาไทยและอังกฤษ (ตัวเลขบนป้าย)
TESSERACT_CONFIG = "--psm 11"   # sparse text: อ่านได้ทั้งบรรทัดเลขและบรรทัดจังหวัด

# ค่าสำหรับเตรียมภาพก่อนอ่าน (ดูรายละเอียดในฟังก์ชัน preprocess_image)
CROP_RATIO_Y = 0.18   # ตัดขอบบน-ล่างออกกี่ % ของความสูงภาพ
CROP_RATIO_X = 0.10   # ตัดขอบซ้าย-ขวาออกกี่ % ของความกว้างภาพ
UPSCALE = 3            # ขยายภาพกี่เท่า


# ============================================================
# ขั้นตอนที่ 2: เตรียมภาพให้ Tesseract อ่านง่ายขึ้น
# ============================================================

def preprocess_image(image_path):
    img = cv2.imread(str(image_path))
    height, width = img.shape[:2]

    # 2.1 ตัดขอบดำ/รอยสกรูของป้ายออก เพราะมักทำให้ Tesseract อ่านบรรทัดบนพลาด
    pad_y = int(height * CROP_RATIO_Y)
    pad_x = int(width * CROP_RATIO_X)
    inner_image = img[pad_y:height - pad_y, pad_x:width - pad_x]

    # 2.2 แปลงเป็นภาพขาวดำ (grayscale) เพราะ Tesseract อ่านภาพขาวดำได้แม่นกว่า
    gray_image = cv2.cvtColor(inner_image, cv2.COLOR_BGR2GRAY)

    # 2.3 ขยายภาพให้ใหญ่ขึ้น ตัวหนังสือจะได้คมชัดขึ้น อ่านง่ายขึ้น
    gray_height, gray_width = gray_image.shape
    new_size = (gray_width * UPSCALE, gray_height * UPSCALE)
    return cv2.resize(gray_image, new_size, interpolation=cv2.INTER_CUBIC)


# ============================================================
# ขั้นตอนที่ 3: หารายชื่อไฟล์ภาพทั้งหมดในโฟลเดอร์ input
# ============================================================

def get_image_files():
    image_files = []
    for file in INPUT_DIR.iterdir():
        if file.suffix.lower() in (".jpg", ".jpeg", ".png"):
            image_files.append(file)
    return image_files


# ============================================================
# ขั้นตอนที่ 4: อ่านข้อความจากภาพ 1 ภาพด้วย Tesseract
# ============================================================

def read_text_from_image(image_path):
    processed_image = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_image, lang=LANG, config=TESSERACT_CONFIG)

    # Tesseract มักอ่านได้หลายบรรทัด (เช่น เลขทะเบียน + จังหวัด คนละบรรทัด)
    # เก็บเฉพาะบรรทัดที่ไม่ว่าง แล้วรวมเป็นข้อความเดียวคั่นด้วย " | " เพื่อบันทึกลง CSV ได้ง่าย
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    return " | ".join(lines)


# ============================================================
# ขั้นตอนที่ 5: รันทุกขั้นตอนข้างบนตามลำดับ แล้วบันทึกผลลัพธ์เป็น CSV
# ============================================================

def main():
    image_files = get_image_files()
    print(f"พบภาพทั้งหมด {len(image_files)} ไฟล์\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "raw_text"])   # แถวหัวตาราง

        for image_path in image_files:
            raw_text = read_text_from_image(image_path)
            print(f"{image_path.name}: {raw_text}")
            writer.writerow([image_path.name, raw_text])


if __name__ == "__main__":
    main()
