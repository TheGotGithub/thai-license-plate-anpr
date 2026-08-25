# License Plate Data Cleaning & Matching

รับข้อความดิบจาก OCR (`license_plate_ocr/output_text/plate_texts.csv`) มาทำความสะอาด
แยกเป็น **เลขทะเบียน** กับ **จังหวัด** แล้ว match ชื่อจังหวัดกับรายชื่อ 77 จังหวัดจริงของไทย
เพื่อแก้กรณี OCR อ่านตัวอักษรเพี้ยนเล็กน้อย (fuzzy matching)

## โครงสร้างโฟลเดอร์

```
license_plate_match/
├── provinces_th.txt      # รายชื่อ 77 จังหวัดของไทย ใช้เป็นฐานสำหรับ matching
├── output_data/           # ผลลัพธ์ที่ทำความสะอาด+match แล้ว (plates_matched.csv)
└── clean_and_match.py     # สคริปต์หลัก
```

ไม่ต้องติดตั้ง dependency เพิ่ม (ใช้แค่ไลบรารีมาตรฐานของ Python: `csv`, `re`, `difflib`)

## หลักการทำงาน

1. **Cleaning**: ตัดสัญลักษณ์รบกวนที่ OCR อ่านผิดเพี้ยนออก (เหลือแค่ตัวอักษรไทย ตัวเลข เว้นวรรค)
2. **แยกเลขทะเบียน**: หาข้อความที่ตรงรูปแบบ "พยัญชนะไทย 1-3 ตัว + ตัวเลข 1-4 หลัก" เช่น `กท 1234`
3. **Matching จังหวัด**: เทียบข้อความที่เหลือกับรายชื่อ 77 จังหวัดใน `provinces_th.txt` ด้วย `difflib`
   (fuzzy match แก้ตัวอักษรเพี้ยนเล็กน้อยได้ เช่น `กรงเทพมหานคร` → `กรุงเทพมหานคร`)
4. บันทึกผลลัพธ์เป็น `output_data/plates_matched.csv` พร้อมคะแนนความเหมือน (`province_match_score`)

## วิธีใช้งาน

รันต่อจากขั้นตอน OCR (`license_plate_ocr/ocr_plate.py`) ที่สร้างไฟล์
`license_plate_ocr/output_text/plate_texts.csv` ไว้แล้ว:

```
python clean_and_match.py
```

ผลลัพธ์จะอยู่ที่ `output_data/plates_matched.csv` มีคอลัมน์:
- `image` — ชื่อไฟล์ภาพป้ายทะเบียน
- `plate_number` — เลขทะเบียนที่แยกออกมา
- `province` — ชื่อจังหวัดที่ match ได้ (ว่างถ้าไม่พบจังหวัดที่ใกล้เคียงพอ)
- `province_match_score` — คะแนนความเหมือน 0-1 (1.0 = ตรงเป๊ะ)
