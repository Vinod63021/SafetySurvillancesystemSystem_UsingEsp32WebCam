from flask import Flask, render_template, Response, jsonify, request
import cv2
import time
import math
import os
from ultralytics import YOLO
from twilio.rest import Client

danger_active = False

app = Flask(__name__)

# -----------------------------
# CONFIGURATION
# -----------------------------

import requests

ESP32_IP = "http://172.20.10.4"   # <-- Your ESP32 IP


VIDEO_SOURCE = "http://172.20.10.3:81/stream"
# For testing use: 
#VIDEO_SOURCE = 0

model = YOLO("yolov8n.pt")

SAFE_ZONE = (50, 50, 590, 430)
DANGEROUS_CLASSES = ['dog', 'knife', 'car', 'truck']
DISTANCE_THRESHOLD = 120
ALERT_COOLDOWN = 20  # seconds

# -----------------------------
# TWILIO CONFIG
# -----------------------------
TWILIO_SID = ""
TWILIO_AUTH = ""
TWILIO_FROM = ""
PARENT_PHONE = ""

twilio_client = Client(TWILIO_SID, TWILIO_AUTH)

# -----------------------------
# GLOBAL VARIABLES
# -----------------------------
current_status = {
    "risk_level": 0,
    "status": "Safe",
    "timestamp": time.time()
}

os.makedirs("incidents", exist_ok=True)

camera = cv2.VideoCapture(VIDEO_SOURCE)

last_alert_time = 0
previous_child_center_y = None


# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------

def calculate_distance(box1, box2):
    c1_x = (box1[0] + box1[2]) // 2
    c1_y = (box1[1] + box1[3]) // 2
    c2_x = (box2[0] + box2[2]) // 2
    c2_y = (box2[1] + box2[3]) // 2
    return math.sqrt((c1_x - c2_x)**2 + (c1_y - c2_y)**2)


def check_inside(box, zone):
    cx = (box[0] + box[2]) // 2
    cy = (box[1] + box[3]) // 2
    return zone[0] <= cx <= zone[2] and zone[1] <= cy <= zone[3]


def send_sms(message):
    try:
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=PARENT_PHONE
        )
        print("📩 SMS Sent Successfully")
    except Exception as e:
        print("Twilio Error:", e)


def send_alert(message, frame, force=False):
    global last_alert_time

    # If not forced, apply cooldown
    if not force:
        if time.time() - last_alert_time < ALERT_COOLDOWN:
            return

    last_alert_time = time.time()

    print("🚨 ALERT:", message)

    # Save snapshot
    filename = f"incidents/alert_{int(time.time())}.jpg"
    cv2.imwrite(filename, frame)

    # Send SMS immediately
    send_sms(message)



# -----------------------------
# VIDEO PROCESSING
# -----------------------------

def generate_frames():
    global current_status, previous_child_center_y, danger_active

    while True:
        success, frame = camera.read()
        if not success:
            break

        results = model(frame, verbose=False)
        result = results[0]

        child_box = None
        dangerous_objects = []

        # ❌ SAFE ZONE DRAWING REMOVED
        # (sx1, sy1, sx2, sy2) = SAFE_ZONE
        # cv2.rectangle(frame, (sx1, sy1), (sx2, sy2), (0, 255, 0), 2)

        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            confidence = float(box.conf[0])

            if confidence < 0.5:
                continue

            coords = [int(c) for c in box.xyxy[0]]
            (x1, y1, x2, y2) = coords

            if class_name == 'person':
                child_box = coords
                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0), 2)

            if class_name in DANGEROUS_CLASSES:
                dangerous_objects.append((class_name, coords))
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)

        risk_level = 10
        status_text = "Safe"
        danger_now = False

        if child_box:
            x1, y1, x2, y2 = child_box
            width = x2 - x1
            height = y2 - y1
            center_y = (y1 + y2) // 2

            fall_detected = False

            # 1️⃣ Horizontal body detection
            if width > height * 1.2:
                fall_detected = True

            # 2️⃣ Sudden downward movement
            if previous_child_center_y is not None:
                if center_y - previous_child_center_y > 40:
                    fall_detected = True

            previous_child_center_y = center_y

            # -----------------------------
            # FALL DETECTION
            # -----------------------------
            if fall_detected:
                status_text = "CRITICAL: CHILD FALL DETECTED!"
                risk_level = 100
                danger_now = True

            # ❌ SAFE ZONE CHECK DISABLED
            # elif not check_inside(child_box, SAFE_ZONE):
            #     status_text = "WARNING: Child Outside Safe Zone!"
            #     risk_level = 80
            #     danger_now = True

            # -----------------------------
            # DANGEROUS OBJECT PROXIMITY
            # -----------------------------
            for obj_name, obj_box in dangerous_objects:
                distance = calculate_distance(child_box, obj_box)
                if distance < DISTANCE_THRESHOLD:
                    status_text = f"CRITICAL: Child Near {obj_name.upper()}!"
                    risk_level = 95
                    danger_now = True

        # -----------------------------
        # SMS LOGIC
        # -----------------------------
        if danger_now and not danger_active:
            send_sms(status_text)

            filename = f"incidents/alert_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)

            print("🚨 SMS SENT:", status_text)
            danger_active = True

        if not danger_now:
            danger_active = False

        # -----------------------------
        # UPDATE STATUS
        # -----------------------------
        current_status = {
            "risk_level": risk_level,
            "status": status_text,
            "timestamp": time.time()
        }

        color = (0,0,255) if risk_level > 50 else (0,255,0)
        cv2.putText(frame, status_text, (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# -----------------------------
# ROUTES
# -----------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_status')
def get_status():
    return jsonify(current_status)

# -----------------------------
# ROBOT CONTROL ROUTES
# -----------------------------

def send_command(command):
    try:
        requests.get(f"{ESP32_IP}/{command}", timeout=0.3)
    except:
        pass


@app.route('/forward')
def move_forward():
    send_command("forward")
    return "OK"


@app.route('/backward')
def move_backward():
    send_command("backward")
    return "OK"


@app.route('/left')
def move_left():
    send_command("left")
    return "OK"


@app.route('/right')
def move_right():
    send_command("right")
    return "OK"


@app.route('/stop')
def move_stop():
    send_command("stop")
    return "OK"


@app.route('/servo')
def move_servo():
    try:
        angle = request.args.get("angle", 90)
        angle = int(angle)

        url = f"{ESP32_IP}/servo"
        params = {"angle": angle}

        requests.get(url, params=params, timeout=0.5)

        return "OK"
    except Exception as e:
        print("Servo Error:", e)
        return "Error", 500


# -----------------------------
# RUN SERVER
# -----------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
