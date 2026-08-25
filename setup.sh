#!/bin/bash
# ตั้งค่าโปรเจกต์นี้บน Raspberry Pi (หรือเครื่องอื่นที่ใช้ Linux) แบบอัตโนมัติ:
# 1. สร้าง Python venv (ถ้ายังไม่มี)
# 2. เปิดใช้งาน (activate) venv
# 3. ติดตั้ง dependencies ทั้งหมดจาก requirements.txt
#
# วิธีใช้: ต้องรันด้วยคำสั่ง "source" เท่านั้น ห้ามรันแบบ ./setup.sh เฉยๆ
# เพราะ venv จะ activate อยู่แค่ใน subshell ของสคริปต์ แล้วหายไปทันทีที่สคริปต์จบ
#
#   source setup.sh
#   หรือ
#   . setup.sh

# ============================================================
# ขั้นตอนที่ 0: เตือนถ้าไม่ได้ใช้ source รันสคริปต์
# ============================================================

if [ "$0" = "$BASH_SOURCE" ]; then
    echo "คำเตือน: กรุณารันด้วย 'source setup.sh' แทน './setup.sh'"
    echo "ไม่งั้น venv จะไม่ค้าง activate อยู่ใน terminal ของคุณ"
    echo ""
fi

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$BASE_DIR/venv"

# ============================================================
# ขั้นตอนที่ 1: ติดตั้ง Tesseract OCR + ภาษาไทยระดับระบบ (ถ้ายังไม่มี)
# ============================================================

if ! command -v tesseract >/dev/null 2>&1; then
    echo "กำลังติดตั้ง Tesseract OCR..."
    sudo apt-get update -qq
    sudo apt-get install -y tesseract-ocr tesseract-ocr-tha
fi

# ============================================================
# ขั้นตอนที่ 2: สร้าง venv ถ้ายังไม่มี
# ============================================================

if [ ! -d "$VENV_DIR" ]; then
    echo "กำลังสร้าง venv..."
    python3 -m venv "$VENV_DIR"
fi

# ============================================================
# ขั้นตอนที่ 3: เปิดใช้งาน (activate) venv
# ============================================================

source "$VENV_DIR/bin/activate"
echo "เปิดใช้งาน venv แล้ว: $VENV_DIR"

# ============================================================
# ขั้นตอนที่ 4: ติดตั้ง dependencies
# ============================================================

pip install --upgrade pip -q

# ติดตั้ง torch แบบ CPU-only ก่อน กัน pip ดึงแพ็กเกจ CUDA มาโดยไม่จำเป็น
# (บอร์ดอย่าง Raspberry Pi ไม่มี GPU ของ NVIDIA ใช้ CUDA ไม่ได้อยู่แล้ว)
if ! python3 -c "import torch" 2>/dev/null; then
    echo "กำลังติดตั้ง torch (CPU-only)..."
    pip install torch --index-url https://download.pytorch.org/whl/cpu
fi

echo "กำลังติดตั้ง dependencies ที่เหลือ..."
pip install -r "$BASE_DIR/requirements.txt"

# บังคับติดตั้ง torchvision จาก index เดียวกับ torch เสมอ เพื่อให้ build ตรงกัน
# (ถ้า build ไม่ตรงกันจะรันแล้วเจอ error "operator torchvision::nms does not exist")
pip install --force-reinstall --no-deps torchvision --index-url https://download.pytorch.org/whl/cpu -q

echo ""
echo "ติดตั้งเสร็จสมบูรณ์ พร้อมใช้งาน (venv เปิดอยู่ในเทอร์มินัลนี้แล้ว)"
echo "ทดสอบรัน pipeline: python3 run_pipeline.py"
