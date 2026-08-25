# License Plate GUI

หน้าเว็บสำหรับอัปโหลดภาพรถ แล้วรัน pipeline ตรวจจับป้ายทะเบียนทั้งหมด
(`license_plate_crop` → `license_plate_ocr` → `license_plate_match`) ในคลิกเดียว พร้อมแสดงผลลัพธ์

## โครงสร้างโฟลเดอร์

```
license_plate_gui/
└── app.py           # หน้าเว็บ Streamlit
```

## วิธีใช้งาน

1. ติดตั้ง dependencies (ใช้ไฟล์ `requirements.txt` ที่ root ของโปรเจกต์ รวมทุกโมดูลไว้ที่เดียว)
   ```
   pip install -r ../requirements.txt
   ```

2. รัน
   ```
   streamlit run app.py
   ```
   จะเปิดหน้าเว็บที่ `http://localhost:8501` อัตโนมัติ

3. อัปโหลดภาพรถ แล้วกด "ประมวลผล" ระบบจะรันตรวจจับป้าย, OCR, และจับคู่จังหวัดให้ครบ
   แล้วแสดงภาพป้ายทะเบียนที่ตรวจพบ พร้อมเลขทะเบียนและจังหวัดที่อ่านได้

## หมายเหตุ

ภาพที่อัปโหลดจะถูกบันทึกไว้ใน `../license_plate_crop/input_images/` และผลลัพธ์แต่ละขั้นตอน
จะถูกเขียนทับไฟล์ output เดิมของแต่ละโมดูล (`output_crops/`, `output_text/`, `output_data/`)
เช่นเดียวกับตอนรัน `run_pipeline.py` ตามปกติ
