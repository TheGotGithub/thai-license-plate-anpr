# License Plate Crop

เทรน YOLOv8 (Model 1) เพื่อตรวจจับตำแหน่งป้ายทะเบียน แล้ว crop เฉพาะบริเวณป้ายออกมาเป็นไฟล์ใหม่

## โครงสร้างโฟลเดอร์

```
license_plate_crop/
├── dataset/            # dataset ป้ายทะเบียน (ดาวน์โหลดจาก Roboflow) สำหรับเทรนโมเดล
├── models/             # เก็บไฟล์โมเดล YOLOv8 (.pt) ที่เทรนเสร็จแล้ว
├── input_images/       # วางภาพต้นฉบับที่ต้องการตรวจจับ
├── output_crops/       # ภาพป้ายทะเบียนที่ crop แล้วจะถูกบันทึกที่นี่
├── train_model1.py     # สคริปต์เทรนโมเดล Model 1
├── detect_and_crop.py  # สคริปต์ตรวจจับ + crop
└── requirements.txt
```

## วิธีใช้งาน

### 1. ติดตั้ง dependencies
```
pip install -r requirements.txt
```

### 2. เตรียม dataset สำหรับเทรน

ไปที่ Roboflow Universe แล้วเลือก dataset ป้ายทะเบียนที่รองรับ YOLOv8 เช่น:
- https://universe.roboflow.com/yolov8-license-plate
- https://universe.roboflow.com/christine-ndtou/license-plate-detection-yolov8
- https://universe.roboflow.com/search?q=class:%22license+plate%22 (ค้นหาเพิ่มเติม)

กด **Download Dataset** เลือกฟอร์แมต **YOLOv8** จะได้ไฟล์ zip ที่มี `data.yaml`, โฟลเดอร์ `train/`, `valid/`, `test/`
แตกไฟล์แล้ววางไว้ในโฟลเดอร์ `dataset/` ของโปรเจกต์นี้ (ให้ `dataset/data.yaml` อยู่ตรงตำแหน่งนั้นพอดี)

### 3. เทรนโมเดล
```
python train_model1.py
```
โมเดลที่เทรนเสร็จจะถูกบันทึกไว้ที่ `runs/detect/train/weights/best.pt`

คัดลอกไฟล์นั้นไปไว้ที่ `models/model1_plate_detect.pt`:
```
cp runs/detect/train/weights/best.pt models/model1_plate_detect.pt
```

### 4. ตรวจจับและ crop ป้ายทะเบียน

นำภาพที่ต้องการตรวจจับไปวางไว้ในโฟลเดอร์ `input_images/` แล้วรัน
```
python detect_and_crop.py
```
ภาพป้ายทะเบียนที่ crop แล้วจะอยู่ในโฟลเดอร์ `output_crops/`
