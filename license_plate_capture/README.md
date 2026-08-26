# License Plate Capture

ถ่ายภาพจากกล้อง Pi Camera บน Raspberry Pi แล้วบันทึกตรงเข้าโฟลเดอร์
`license_plate_crop/input_images/` เพื่อให้ pipeline ตรวจจับป้ายทะเบียนหยิบไปใช้ต่อได้ทันที

**รันได้เฉพาะบน Raspberry Pi ที่ต่อกล้อง Pi Camera เท่านั้น** (ใช้ไม่ได้บน Mac/PC ทั่วไป)

## โครงสร้างโฟลเดอร์

```
license_plate_capture/
├── capture.py          # สคริปต์ถ่ายภาพแบบ command line (ถ่าย 1 รูปแล้วจบ)
├── capture_gui.py       # หน้าเว็บ GUI ถ่ายภาพ พร้อมดูตัวอย่างก่อนถ่ายจริง
└── startCaptureGUI.sh   # สคริปต์เปิดหน้าเว็บ capture_gui.py แบบไม่ต้อง activate venv เอง
```

## ข้อกำหนดระบบ

ใช้ไลบรารี `picamera2` ซึ่งเป็นไลบรารีระดับระบบที่มากับ Raspberry Pi OS อยู่แล้ว
(ติดตั้งผ่าน `apt` ไม่ใช่ผ่าน `pip`) เพราะต้องพึ่ง libcamera ที่คอมไพล์เฉพาะรุ่นบอร์ด/กล้อง

ถ้ายังไม่มี ติดตั้งด้วย:
```
sudo apt install -y python3-picamera2
```

**สำคัญ:** venv ของโปรเจกต์นี้ต้องสร้างด้วยแฟล็ก `--system-site-packages`
(หรือแก้ไฟล์ `venv/pyvenv.cfg` เปลี่ยน `include-system-site-packages = false` เป็น `true`)
ไม่งั้น venv จะมองไม่เห็น `picamera2` ที่ติดตั้งไว้ระดับระบบ — `setup.sh` ที่ root โปรเจกต์
สร้าง venv ด้วยแฟล็กนี้ให้อัตโนมัติอยู่แล้ว

## วิธีใช้งาน

### แบบ command line (ถ่าย 1 รูปแล้วจบ)
```
python capture.py
```

### แบบ GUI (ดูตัวอย่างก่อนถ่ายจริง)
```
./startCaptureGUI.sh
```
จะเปิดหน้าเว็บที่ `http://localhost:8501` มีปุ่ม 2 ปุ่ม:
- **ดูตัวอย่าง** — ถ่ายภาพตัวอย่างมาแสดง (กดซ้ำได้เรื่อยๆ เพื่อดูมุมกล้องปัจจุบัน ยังไม่บันทึกไฟล์)
- **ถ่ายภาพและบันทึก** — ถ่ายภาพความละเอียดเต็มแล้วบันทึกไฟล์จริง

ทั้งสองแบบจะบันทึกภาพไว้ที่ `../license_plate_crop/input_images/capture_<วันที่เวลา>.jpg`
จากนั้นรัน `python ../run_pipeline.py` เพื่อตรวจจับป้ายทะเบียนในภาพที่เพิ่งถ่ายต่อได้เลย

## ปรับแต่ง

แก้ค่าตัวแปรในไฟล์ `capture.py` หรือ `capture_gui.py`:
- `RESOLUTION` — ขนาดภาพที่จะถ่าย (ค่าเริ่มต้น 2304x1296)
- `WARMUP_SECONDS` (มีเฉพาะใน `capture.py`) — เวลารอให้กล้องปรับแสง/โฟกัสก่อนถ่ายจริง (ค่าเริ่มต้น 2 วินาที)
