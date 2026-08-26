# Thai License Plate ANPR (Raspberry Pi 5)

ระบบตรวจจับและอ่านป้ายทะเบียนรถยนต์ภาษาไทยแบบครบวงจร (Automatic Number Plate Recognition)
รันบน Raspberry Pi 5 ตั้งแต่ถ่ายภาพจากกล้อง ตรวจจับตำแหน่งป้ายด้วย YOLOv8 อ่านตัวอักษรด้วย
Tesseract OCR ไปจนถึงจับคู่ชื่อจังหวัดให้ถูกต้อง พร้อมหน้าเว็บ Streamlit ให้ใช้งานได้โดยไม่ต้องพิมพ์คำสั่ง

```
📷 กล้อง (Capture)  →  🎯 YOLOv8 (Crop)  →  🔤 Tesseract (OCR)  →  🇹🇭 Match (77 จังหวัด)  →  💻 Streamlit GUI
```

โปรเจกต์นี้ใช้ประกอบการอบรมเชิงปฏิบัติการ "AI Camera — อ่านป้ายทะเบียนด้วย Raspberry Pi 5"
ของ Cytron Technologies (ดูสไลด์ประกอบได้ที่ [`slide/slides.html`](slide/slides.html))

## โครงสร้างโปรเจกต์

โค้ดแบ่งเป็น 5 โมดูลอิสระ ต่อกันเป็น pipeline ผ่าน `run_pipeline.py` หรือหน้าเว็บใน `license_plate_gui/`

| โมดูล | หน้าที่ | รายละเอียด |
|---|---|---|
| [`license_plate_capture/`](license_plate_capture/README.md) | ถ่ายภาพจากกล้อง Pi Camera (มีทั้งแบบ command line และหน้าเว็บที่มีภาพสด) | ใช้ได้เฉพาะบน Raspberry Pi |
| [`license_plate_crop/`](license_plate_crop/README.md) | ตรวจจับตำแหน่งป้ายทะเบียนด้วย YOLOv8 แล้ว crop ออกมา | รวมสคริปต์เทรนโมเดลด้วย |
| [`license_plate_ocr/`](license_plate_ocr/README.md) | อ่านตัวอักษรบนป้ายด้วย Tesseract OCR (รองรับภาษาไทย) | |
| [`license_plate_match/`](license_plate_match/README.md) | ทำความสะอาดข้อความ แยกเลขทะเบียน และจับคู่ชื่อจังหวัดจาก 77 จังหวัด | ใช้ fuzzy matching แก้ OCR อ่านเพี้ยน |
| [`license_plate_gui/`](license_plate_gui/README.md) | หน้าเว็บ Streamlit รวมทุกขั้นตอน เลือกอัปโหลดภาพหรือถ่ายจากกล้องได้ | โมดูลที่ผู้ใช้ทั่วไปควรเริ่มจากตรงนี้ |

ไฟล์อื่นๆ ที่ root:

| ไฟล์/โฟลเดอร์ | รายละเอียด |
|---|---|
| `run_pipeline.py` | รันทั้ง 3 ขั้นตอนหลัก (crop → OCR → match) ต่อกันในคำสั่งเดียวแบบ command line |
| `setup.sh` | ติดตั้งระบบให้อัตโนมัติ (Tesseract, picamera2, venv, dependencies) ใช้ครั้งแรกตอนตั้งเครื่อง |
| `requirements.txt` | รวม Python dependencies ของทุกโมดูลไว้ที่เดียว |
| `basic_python/`, `basic_command_line/` | ตัวอย่างโค้ด Python/คำสั่ง Terminal พื้นฐาน ใช้สอนในวันแรกของเวิร์กช็อป |
| `slide/` | สไลด์ประกอบการสอน (`slides.html` เปิดดูได้ตรงในเบราว์เซอร์) |
| `photo/` | ภาพตัวอย่างรถยนต์ไทยสำหรับทดสอบระบบ |

## เริ่มต้นใช้งาน

### 1. ติดตั้งระบบ (ครั้งแรกเท่านั้น)

บน Raspberry Pi (หรือ Linux ทั่วไป):
```bash
source setup.sh
```
สคริปต์นี้จะติดตั้ง Tesseract OCR + ภาษาไทย, `python3-picamera2` (สำหรับกล้อง), สร้าง Python
virtual environment (`venv/`), และติดตั้ง dependencies ทั้งหมดจาก `requirements.txt` ให้อัตโนมัติ
(ต้องรันด้วย `source` ไม่ใช่ `./setup.sh` เพื่อให้ venv ที่ activate ค้างอยู่ในเทอร์มินัล)

บน macOS/Windows (ใช้พัฒนา/ทดสอบเฉพาะส่วนที่ไม่ต้องใช้กล้อง): สร้าง venv เองแล้ว
`pip install -r requirements.txt` ได้เลย — โหมดที่ต้องใช้กล้อง Pi Camera (`picamera2`) จะใช้ไม่ได้
บนเครื่องเหล่านี้

### 2. ใช้งานผ่านหน้าเว็บ (แนะนำ)

```bash
./license_plate_gui/startGUI.sh
```
เปิด `http://localhost:8501` (หรือ `http://<IP ของ Pi>:8501` จากเครื่องอื่นในวง LAN) แล้วเลือก
อัปโหลดภาพหรือถ่ายภาพจากกล้องได้เลย

### 3. หรือใช้งานผ่าน command line

```bash
python3 run_pipeline.py
```
วางภาพไว้ใน `license_plate_crop/input_images/` ก่อนรัน ผลลัพธ์สุดท้ายจะอยู่ที่
`license_plate_match/output_data/plates_matched.csv`

## ฮาร์ดแวร์ที่ใช้

- Raspberry Pi 5 (4GB/8GB)
- Raspberry Pi Camera Module 3 (ต่อผ่านพอร์ต CSI)
- microSD การ์ด (แนะนำ 32GB ขึ้นไป)

## เทคโนโลยีที่ใช้

Python · OpenCV · [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) (PyTorch, CPU-only
บน Pi) · [picamera2](https://github.com/raspberrypi/picamera2) · Tesseract OCR · Streamlit
