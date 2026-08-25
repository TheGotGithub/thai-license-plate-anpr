"""
หน้าเว็บ (GUI) สำหรับรัน pipeline ตรวจจับป้ายทะเบียนทั้งหมดผ่านเบราว์เซอร์
ทำงานเป็นขั้นตอนเดียวกับ run_pipeline.py ทุกอย่าง แค่มีหน้าเว็บให้อัปโหลดภาพและดูผลลัพธ์
"""

import csv
import importlib.util
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


# ============================================================
# ขั้นตอนที่ 2: ฟังก์ชันช่วยเหลือ
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
    """อ่านผลลัพธ์จาก CSV เฉพาะแถวที่เป็นของภาพที่เพิ่งอัปโหลด"""
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


# ============================================================
# ขั้นตอนที่ 3: สร้างหน้าเว็บ
# ============================================================

st.set_page_config(page_title="ตรวจจับป้ายทะเบียนรถ")
st.title("ตรวจจับป้ายทะเบียนรถ")

uploaded_file = st.file_uploader("เลือกภาพรถ", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="ภาพต้นฉบับ", width=400)

    if st.button("ประมวลผล"):
        # 3.1 บันทึกภาพที่อัปโหลด
        image_path = save_uploaded_image(uploaded_file)

        # 3.2 รัน pipeline ทั้ง 3 ขั้นตอนตามลำดับ
        with st.status("กำลังประมวลผล...") as status:
            for label, script_path in PIPELINE_SCRIPTS:
                status.update(label=label)
                run_script(script_path)
            status.update(label="เสร็จสิ้น", state="complete")

        # 3.3 แสดงผลลัพธ์ที่ได้
        results = read_matched_rows(image_path.stem)
        if not results:
            st.warning("ไม่พบป้ายทะเบียนในภาพนี้")

        for row in results:
            show_result(row)
