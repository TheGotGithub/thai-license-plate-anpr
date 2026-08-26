"""
หน้าเว็บ GUI สำหรับถ่ายภาพจากกล้อง Pi Camera พร้อมดูภาพสด (live stream) ก่อนถ่ายจริง
รันได้เฉพาะบน Raspberry Pi ที่ต่อกล้อง Pi Camera เท่านั้น (ใช้ไม่ได้บน Mac/PC ทั่วไป)
"""

import socket
from datetime import datetime
from pathlib import Path

import streamlit as st
from picamera2 import Picamera2

from mjpeg_stream import start_mjpeg_server

# ============================================================
# ขั้นตอนที่ 1: ตั้งค่าตัวแปรต่างๆ ที่จะใช้ในสคริปต์
# ============================================================

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR.parent / "license_plate_crop" / "input_images"   # บันทึกตรงเข้า input ของขั้นตอน crop
STILL_RESOLUTION = (2304, 1296)     # ขนาดภาพตอนถ่ายจริง (กว้าง, สูง) เป็นพิกเซล
PREVIEW_RESOLUTION = (820, 462)     # ขนาดภาพตอนสตรีมสด (เล็กกว่าเพื่อให้ลื่นไหล ไม่กระตุก)
STREAM_PORT = 8765                  # พอร์ตของ MJPEG server (คนละพอร์ตกับ Streamlit)


# ============================================================
# ขั้นตอนที่ 2: เปิดกล้อง + เริ่มสตรีมภาพสดแค่ครั้งเดียว
# (ไม่เปิดใหม่ทุกครั้งที่กดปุ่ม เพราะ Streamlit รันสคริปต์ใหม่ทุกครั้งที่มีการโต้ตอบ)
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
    if "camera" not in st.session_state:
        camera = Picamera2()
        start_mjpeg_server(camera, STREAM_PORT, PREVIEW_RESOLUTION, STILL_RESOLUTION)
        st.session_state.camera = camera
    return st.session_state.camera


# ============================================================
# ขั้นตอนที่ 3: ถ่ายภาพความละเอียดเต็ม แล้วบันทึกลงโฟลเดอร์ input_images
# (ดึงจากสตรีม "main" ที่วิ่งคู่ขนานกับสตรีมสดอยู่แล้ว ไม่ต้องหยุด/สลับโหมดกล้อง
# สตรีมสดจึงไม่กระตุกหรือหยุดเลยระหว่างถ่ายภาพ)
# ============================================================

def capture_and_save():
    camera = get_camera()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"capture_{timestamp}.jpg"

    request = camera.capture_request()
    request.save("main", str(output_path))
    request.release()
    return output_path


# ============================================================
# ขั้นตอนที่ 4: สร้างหน้าเว็บ
# ============================================================

st.set_page_config(page_title="ถ่ายภาพป้ายทะเบียน")
st.title("ถ่ายภาพจากกล้อง Pi Camera")
st.caption("ภาพด้านล่างเป็นภาพสดจากกล้อง เล็งมุมให้พร้อมแล้วกดถ่ายภาพได้เลย")

get_camera()   # เปิดกล้อง + เริ่มสตรีม (ถ้ายังไม่ได้เปิด)

# ฝัง <img> ที่ชี้ไปที่ MJPEG server โดยตรง เบราว์เซอร์จะอัปเดตภาพเองต่อเนื่อง
# ไม่ต้องพึ่งการ rerun ของ Streamlit เลย (ใส่ IP ของ Pi ตรงๆ แทนที่จะใช้ <script>
# เพราะ st.markdown ไม่รันแท็ก <script> ที่ฝังเข้าไป)
stream_url = f"http://{get_local_ip()}:{STREAM_PORT}/stream.mjpg"
st.markdown(
    f'<img src="{stream_url}" style="width:100%; max-width:640px; border-radius:8px; display:block;">',
    unsafe_allow_html=True,
)

if st.button("ถ่ายภาพและบันทึก", type="primary"):
    saved_path = capture_and_save()
    st.success(f"บันทึกแล้ว: {saved_path.name}")
    st.image(str(saved_path), caption="ภาพที่บันทึก")
