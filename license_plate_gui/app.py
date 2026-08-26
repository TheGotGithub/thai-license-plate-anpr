"""
หน้าเว็บ (GUI) สำหรับรัน pipeline ตรวจจับป้ายทะเบียนทั้งหมดผ่านเบราว์เซอร์
ทำงานเป็นขั้นตอนเดียวกับ run_pipeline.py ทุกอย่าง เลือกได้ว่าจะอัปโหลดภาพเอง
หรือถ่ายภาพจากกล้อง Pi Camera โดยตรง (โหมดถ่ายภาพใช้ได้เฉพาะบน Raspberry Pi)
"""

import csv
import importlib.util
import socket
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# ============================================================
# ขั้นตอนที่ 1: ตั้งค่า path ต่างๆ ที่จะใช้ในสคริปต์
# ============================================================

BASE_DIR = Path(__file__).parent.parent
INPUT_IMAGES_DIR = BASE_DIR / "license_plate_crop" / "input_images"
OUTPUT_CROPS_DIR = BASE_DIR / "license_plate_crop" / "output_crops"
MATCHED_CSV = BASE_DIR / "license_plate_match" / "output_data" / "plates_matched.csv"

# รายชื่อ 3 ขั้นตอนของ pipeline ที่จะรันตามลำดับ (ชื่อที่แสดงบนจอ, ไฟล์สคริปต์)
PIPELINE_SCRIPTS = [
    ("ตรวจจับ + Crop ป้ายทะเบียน", BASE_DIR / "license_plate_crop" / "detect_and_crop.py"),
    ("OCR อ่านข้อความ", BASE_DIR / "license_plate_ocr" / "ocr_plate.py"),
    ("Data Cleaning & Matching", BASE_DIR / "license_plate_match" / "clean_and_match.py"),
]

# ค่าสำหรับโหมดถ่ายภาพจากกล้อง (ใช้ mjpeg_stream.py ตัวเดียวกับ license_plate_capture)
STILL_RESOLUTION = (2304, 1296)
PREVIEW_RESOLUTION = (820, 462)
STREAM_PORT = 8765
sys.path.insert(0, str(BASE_DIR / "license_plate_capture"))


# ============================================================
# ขั้นตอนที่ 2: ฟังก์ชันช่วยเหลือทั่วไป
# ============================================================

def run_script(script_path):
    """โหลดสคริปต์อีกไฟล์มารัน (เหมือนกดรัน python script.py)"""
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


def save_uploaded_image(uploaded_file):
    """บันทึกไฟล์ที่ผู้ใช้อัปโหลด ลงโฟลเดอร์ input_images ของขั้นตอน crop"""
    INPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image_path = INPUT_IMAGES_DIR / uploaded_file.name
    image_path.write_bytes(uploaded_file.getvalue())
    return image_path


def read_matched_rows(image_stem):
    """อ่านผลลัพธ์จาก CSV เฉพาะแถวที่เป็นของภาพนี้"""
    if not MATCHED_CSV.exists():
        return []

    with open(MATCHED_CSV, encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))

    matched_rows = []
    for row in all_rows:
        if row["image"].startswith(f"{image_stem}_plate_"):
            matched_rows.append(row)
    return matched_rows


def show_result(row):
    """แสดงผลลัพธ์ 1 ป้ายทะเบียน (ภาพที่ crop ได้ + เลขทะเบียน + จังหวัด)"""
    crop_path = OUTPUT_CROPS_DIR / row["image"]
    col_image, col_text = st.columns([1, 2])

    with col_image:
        if crop_path.exists():
            st.image(str(crop_path), caption="ป้ายทะเบียนที่ตรวจพบ")

    with col_text:
        st.metric("เลขทะเบียน", row["plate_number"] or "-")
        st.metric("จังหวัด", row["province"] or "-")
        st.caption(f"ความมั่นใจในการ match จังหวัด: {row['province_match_score']}")


def process_image(image_path):
    """รัน pipeline ทั้ง 3 ขั้นตอน แล้วแสดงผลลัพธ์ของภาพที่เพิ่งได้มา"""
    with st.status("กำลังประมวลผล...") as status:
        for label, script_path in PIPELINE_SCRIPTS:
            status.update(label=label)
            run_script(script_path)
        status.update(label="เสร็จสิ้น", state="complete")

    results = read_matched_rows(image_path.stem)
    if not results:
        st.warning("ไม่พบป้ายทะเบียนในภาพนี้")
    for row in results:
        show_result(row)


# ============================================================
# ขั้นตอนที่ 3: ฟังก์ชันสำหรับโหมด "ถ่ายภาพจากกล้อง"
# ============================================================

def get_local_ip():
    # เปิด socket แบบ UDP ไปยัง IP ภายนอก (ไม่ได้ส่งข้อมูลจริง) เพื่ออ่าน IP วง LAN ของ Pi เอง
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def get_camera():
    """เปิดกล้อง + เริ่มสตรีมภาพสดแค่ครั้งเดียว (import picamera2 แบบ lazy
    เพื่อให้โหมดอัปโหลดภาพยังใช้งานได้ปกติบนเครื่องที่ไม่มี picamera2 เช่น Mac)"""
    if "camera" not in st.session_state:
        from mjpeg_stream import start_mjpeg_server
        from picamera2 import Picamera2

        camera = Picamera2()
        start_mjpeg_server(camera, STREAM_PORT, PREVIEW_RESOLUTION, STILL_RESOLUTION)
        st.session_state.camera = camera
    return st.session_state.camera


def capture_from_camera():
    """ถ่ายภาพความละเอียดเต็มจากกล้อง แล้วบันทึกลงโฟลเดอร์ input_images"""
    camera = get_camera()
    INPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = INPUT_IMAGES_DIR / f"capture_{timestamp}.jpg"

    request = camera.capture_request()
    request.save("main", str(image_path))
    request.release()
    return image_path


# ============================================================
# ขั้นตอนที่ 4: สร้างหน้าเว็บ
# ============================================================

st.set_page_config(page_title="ตรวจจับป้ายทะเบียนรถ")
st.title("ตรวจจับป้ายทะเบียนรถ")

input_mode = st.radio(
    "เลือกวิธีนำเข้าภาพ",
    ["อัปโหลดภาพ", "ถ่ายภาพจากกล้อง Pi Camera"],
    horizontal=True,
)

if input_mode == "อัปโหลดภาพ":
    uploaded_file = st.file_uploader("เลือกภาพรถ", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        st.image(uploaded_file, caption="ภาพต้นฉบับ", width=400)

        if st.button("ประมวลผล"):
            image_path = save_uploaded_image(uploaded_file)
            process_image(image_path)

else:
    try:
        get_camera()
    except ImportError:
        st.error("โหมดนี้ใช้ได้เฉพาะบน Raspberry Pi ที่ต่อกล้อง Pi Camera เท่านั้น (ไม่พบ picamera2)")
    else:
        st.caption("ภาพด้านล่างเป็นภาพสดจากกล้อง เล็งมุมให้พร้อมแล้วกดถ่ายภาพได้เลย")
        stream_url = f"http://{get_local_ip()}:{STREAM_PORT}/stream.mjpg"
        st.markdown(
            f'<img src="{stream_url}" style="width:100%; max-width:500px; border-radius:8px; display:block;">',
            unsafe_allow_html=True,
        )

        if st.button("ถ่ายภาพและประมวลผล", type="primary"):
            image_path = capture_from_camera()
            st.success(f"ถ่ายภาพแล้ว: {image_path.name}")
            process_image(image_path)
