"""
หน้าเว็บ GUI สำหรับถ่ายภาพจากกล้อง Pi Camera พร้อมดูตัวอย่างภาพก่อนถ่ายจริง
รันได้เฉพาะบน Raspberry Pi ที่ต่อกล้อง Pi Camera เท่านั้น (ใช้ไม่ได้บน Mac/PC ทั่วไป)
"""

from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image
from picamera2 import Picamera2

# ============================================================
# ขั้นตอนที่ 1: ตั้งค่าตัวแปรต่างๆ ที่จะใช้ในสคริปต์
# ============================================================

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR.parent / "license_plate_crop" / "input_images"   # บันทึกตรงเข้า input ของขั้นตอน crop
RESOLUTION = (2304, 1296)   # ขนาดภาพที่จะถ่ายจริง (กว้าง, สูง) เป็นพิกเซล


# ============================================================
# ขั้นตอนที่ 2: เปิดกล้องแค่ครั้งเดียว แล้วเก็บไว้ใช้ซ้ำ
# (ไม่เปิดใหม่ทุกครั้งที่กดปุ่ม เพราะ Streamlit รันสคริปต์ใหม่ทุกครั้งที่มีการกดปุ่ม)
# ============================================================

def get_camera():
    if "camera" not in st.session_state:
        camera = Picamera2()
        config = camera.create_still_configuration(main={"size": RESOLUTION})
        camera.configure(config)
        camera.start()
        st.session_state.camera = camera
    return st.session_state.camera


# ============================================================
# ขั้นตอนที่ 3: ถ่ายภาพตัวอย่าง (ดูอย่างเดียว ไม่บันทึกไฟล์)
# ============================================================

def capture_preview():
    camera = get_camera()
    frame = camera.capture_array()   # ได้ภาพปัจจุบันจากกล้องเป็น numpy array
    return Image.fromarray(frame)


# ============================================================
# ขั้นตอนที่ 4: ถ่ายภาพจริง แล้วบันทึกลงโฟลเดอร์ input_images ของขั้นตอน crop
# ============================================================

def capture_and_save():
    camera = get_camera()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"capture_{timestamp}.jpg"
    camera.capture_file(str(output_path))
    return output_path


# ============================================================
# ขั้นตอนที่ 5: สร้างหน้าเว็บ
# ============================================================

st.set_page_config(page_title="ถ่ายภาพป้ายทะเบียน")
st.title("ถ่ายภาพจากกล้อง Pi Camera")
st.caption("กด 'ดูตัวอย่าง' เพื่อเช็คมุมกล้องก่อน แล้วค่อยกด 'ถ่ายภาพและบันทึก' เมื่อพร้อม")

col_preview, col_capture = st.columns(2)

with col_preview:
    if st.button("ดูตัวอย่าง", use_container_width=True):
        st.session_state.shown_image = capture_preview()
        st.session_state.saved_path = None

with col_capture:
    if st.button("ถ่ายภาพและบันทึก", type="primary", use_container_width=True):
        saved_path = capture_and_save()
        st.session_state.shown_image = Image.open(saved_path)
        st.session_state.saved_path = saved_path

if st.session_state.get("saved_path"):
    st.success(f"บันทึกแล้ว: {st.session_state.saved_path.name}")

if st.session_state.get("shown_image") is not None:
    st.image(st.session_state.shown_image, caption="ภาพจากกล้อง", width=500)
else:
    st.info("ยังไม่มีภาพ กดปุ่ม 'ดูตัวอย่าง' เพื่อเริ่มต้น")
