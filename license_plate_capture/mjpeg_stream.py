"""
เซิร์ฟเวอร์ MJPEG อย่างง่าย สำหรับสตรีมภาพสดจากกล้อง Pi Camera ไปแสดงบนหน้าเว็บ
(อ้างอิงแพทเทิร์นมาตรฐานจากตัวอย่างทางการของ picamera2: mjpeg_server.py)

หน้าเว็บฝั่ง browser แค่เปิด <img src="http://.../stream.mjpg"> ก็จะเห็นภาพอัปเดตต่อเนื่อง
เองโดยอัตโนมัติ ไม่ต้องพึ่งการ rerun ของ Streamlit เลย
"""

import io
import socketserver
import threading
from http import server
from threading import Condition

from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput


# ============================================================
# ขั้นตอนที่ 1: ที่พักเก็บเฟรมล่าสุดที่กล้องเข้ารหัสเป็น JPEG มาแล้ว
# ============================================================

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()   # ปลุกทุก client ที่รออยู่ว่ามีเฟรมใหม่แล้ว


# ============================================================
# ขั้นตอนที่ 2: ตัวจัดการคำขอ HTTP — ส่งเฟรมใหม่ให้ client ทุกครั้งที่มีภาพเข้ามา
# ============================================================

class _StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/stream.mjpg":
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Age", "0")
        self.send_header("Cache-Control", "no-cache, private")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
        self.end_headers()
        try:
            while True:
                with self.server.output.condition:
                    self.server.output.condition.wait()
                    frame = self.server.output.frame
                self.wfile.write(b"--FRAME\r\n")
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(frame)))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b"\r\n")
        except (BrokenPipeError, ConnectionResetError):
            pass   # ผู้ใช้ปิดหน้าเว็บ/รีเฟรช ไม่ต้องแจ้ง error

    def log_message(self, format, *args):
        pass   # ปิด log ของ HTTP server กันรกหน้าจอ terminal


class _StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


# ============================================================
# ขั้นตอนที่ 3: เริ่มสตรีมจากกล้องที่ส่งเข้ามา แล้วรัน HTTP server อยู่เบื้องหลัง
# ============================================================

def start_mjpeg_server(camera, port, preview_resolution, still_resolution):
    # ใช้ 2 สตรีมพร้อมกัน: "lores" (เล็ก) สำหรับสตรีมสด และ "main" (ใหญ่) สำรองไว้
    # ถ่ายภาพนิ่งความละเอียดเต็มได้ทุกเมื่อโดยไม่ต้องหยุด/สลับโหมดกล้องเลย
    video_config = camera.create_video_configuration(
        main={"size": still_resolution},
        lores={"size": preview_resolution},
        encode="lores",
    )
    camera.configure(video_config)

    output = StreamingOutput()
    camera.start_recording(MJPEGEncoder(), FileOutput(output))

    httpd = _StreamingServer(("", port), _StreamingHandler)
    httpd.output = output   # ให้ _StreamingHandler เข้าถึงเฟรมล่าสุดผ่าน self.server.output

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd
