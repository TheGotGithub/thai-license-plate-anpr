# 04_functions.py - การสร้างฟังก์ชันใช้งานซ้ำ
def check_plate(plate, allowed_list):
    if plate in allowed_list:
        return "อนุญาตผ่าน (ALLOWED)"
    return "ไม่อนุญาต (DENIED)"

whitelist = ["1กก1234", "2ขข5678"]
result = check_plate("1กก1234", whitelist)
print("ผลการตรวจสอบ:", result)
