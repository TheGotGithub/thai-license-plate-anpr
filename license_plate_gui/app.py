"""
GUI สำหรับรัน pipeline ตรวจจับป้ายทะเบียนทั้งหมด (crop -> OCR -> matching) ผ่านเบราว์เซอร์
"""

import csv
import importlib.util
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).parent.parent
INPUT_IMAGES_DIR = BASE_DIR / "license_plate_crop" / "input_images"
OUTPUT_CROPS_DIR = BASE_DIR / "license_plate_crop" / "output_crops"
MATCHED_CSV = BASE_DIR / "license_plate_match" / "output_data" / "plates_matched.csv"

PIPELINE_SCRIPTS = [
    ("ตรวจจับ + Crop ป้ายทะเบียน", BASE_DIR / "license_plate_crop" / "detect_and_crop.py"),
    ("OCR อ่านข้อความ", BASE_DIR / "license_plate_ocr" / "ocr_plate.py"),
    ("Data Cleaning & Matching", BASE_DIR / "license_plate_match" / "clean_and_match.py"),
]

def run_script(script_path):
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()

def read_matched_rows(image_stem):
    if not MATCHED_CSV.exists():
        return []
    with open(MATCHED_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if r["image"].startswith(f"{image_stem}_plate_")]

st.set_page_config(page_title="ตรวจจับป้ายทะเบียนรถ")
st.title("ตรวจจับป้ายทะเบียนรถ")

uploaded_file = st.file_uploader("เลือกภาพรถ", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="ภาพต้นฉบับ", width=400)

    if st.button("ประมวลผล"):
        INPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        image_path = INPUT_IMAGES_DIR / uploaded_file.name
        image_path.write_bytes(uploaded_file.getvalue())

        with st.status("กำลังประมวลผล...") as status:
            for label, script_path in PIPELINE_SCRIPTS:
                status.update(label=label)
                run_script(script_path)
            status.update(label="เสร็จสิ้น", state="complete")

        results = read_matched_rows(image_path.stem)
        if not results:
            st.warning("ไม่พบป้ายทะเบียนในภาพนี้")
        for row in results:
            crop_path = OUTPUT_CROPS_DIR / row["image"]
            col1, col2 = st.columns([1, 2])
            with col1:
                if crop_path.exists():
                    st.image(str(crop_path), caption="ป้ายทะเบียนที่ตรวจพบ")
            with col2:
                st.metric("เลขทะเบียน", row["plate_number"] or "-")
                st.metric("จังหวัด", row["province"] or "-")
                st.caption(f"ความมั่นใจในการ match จังหวัด: {row['province_match_score']}")
