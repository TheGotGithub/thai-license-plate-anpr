# License Plate OCR

อ่านข้อความจากภาพป้ายทะเบียน (ที่ crop มาจาก `license_plate_crop/`) ด้วย Tesseract OCR รองรับภาษาไทย

## โครงสร้างโฟลเดอร์

```
license_plate_ocr/
├── output_text/         # ผลลัพธ์ข้อความที่อ่านได้ (plate_texts.csv)
└── ocr_plate.py         # สคริปต์หลัก
```

อ่านภาพต้นทางจาก `../license_plate_crop/output_crops/` โดยตรง (ผลลัพธ์จากขั้นตอนก่อนหน้า) ไม่ต้อง copy ไฟล์มาเอง

## ข้อกำหนดระบบ

ต้องติดตั้งโปรแกรม Tesseract OCR (ไม่ใช่แค่ไลบรารี Python) พร้อมชุดภาษาไทย:

```
brew install tesseract tesseract-lang   # macOS
```

ตรวจสอบว่ามีภาษาไทย (`tha`) ติดตั้งอยู่หรือไม่:
```
tesseract --list-langs
```

## หลักการทำงาน

ก่อนส่งเข้า Tesseract สคริปต์จะ preprocess ภาพก่อน (ดูฟังก์ชัน `preprocess` ใน `ocr_plate.py`):
1. ตัดขอบดำ/รอยสกรูของป้ายออก (`CROP_RATIO_Y`, `CROP_RATIO_X`) เพราะขอบป้ายมักรบกวนการแบ่งบล็อกข้อความจน Tesseract อ่านบรรทัดบนพลาด
2. แปลงเป็นภาพขาวดำ (grayscale) และขยายภาพ 3 เท่า (`UPSCALE`) ให้ตัวอักษรไทยที่มีรายละเอียดเยอะคมชัดขึ้น
3. ใช้ `--psm 11` (sparse text) เพื่อให้อ่านได้ทั้งบรรทัดตัวเลขและบรรทัดชื่อจังหวัด

หากใช้กับภาพป้ายทะเบียนที่มีสัดส่วน/ขอบต่างจากตัวอย่าง อาจต้องปรับค่า `CROP_RATIO_Y` / `CROP_RATIO_X` ในไฟล์ `ocr_plate.py` ให้เหมาะกับภาพของตัวเอง

## วิธีใช้งาน

1. ติดตั้ง dependencies (ใช้ไฟล์ `requirements.txt` ที่ root ของโปรเจกต์ รวมทุกโมดูลไว้ที่เดียว)
   ```
   pip install -r ../requirements.txt
   ```

2. รันขั้นตอน `license_plate_crop` ให้เสร็จก่อน เพื่อให้มีภาพอยู่ใน `../license_plate_crop/output_crops/`

3. รันสคริปต์
   ```
   python ocr_plate.py
   ```

4. ผลลัพธ์ข้อความจะแสดงในหน้าจอ และบันทึกไว้ที่ `output_text/plate_texts.csv`
