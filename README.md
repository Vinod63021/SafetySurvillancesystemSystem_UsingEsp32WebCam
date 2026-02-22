🤖 AI Child Safety Robot System










An intelligent real-time AI-powered child safety monitoring system built using ESP32-CAM, YOLOv8, Flask, and Twilio.

This system detects dangerous situations involving children and sends instant SMS alerts to parents while streaming live video over WiFi.

📌 Project Overview

The AI Child Safety Robot combines:

📡 IoT live video streaming

🧠 Real-time object detection

🚨 Risk analysis engine

📩 Instant SMS alert system

🤖 Remote robot control

It is designed to enhance child safety in homes, schools, and daycare environments.

🧠 Key Features
👶 Child Detection

Detects a child using YOLOv8 real-time object detection.

🚨 Fall Detection

Detects:

Horizontal body posture

Sudden downward movement

Triggers:

CRITICAL: CHILD FALL DETECTED!
⚠ Dangerous Object Detection

Monitors proximity to:

Knife

Dog

Car

Truck

Triggers alert if object is too close.

📩 Instant SMS Alerts

Uses Twilio API to notify parents immediately.

📸 Incident Snapshot Saving

Automatically saves alert images in /incidents folder.

🤖 Remote Robot Control

Available API routes:

/forward
/backward
/left
/right
/stop
/servo?angle=90
📡 Live Streaming

Direct stream link:

http://ESP32_IP:81/stream
🏗 System Architecture
ESP32-CAM  →  WiFi  →  Flask Server  →  YOLOv8
                             ↓
                        Risk Analysis
                             ↓
                          Twilio SMS
🛠 Tech Stack
Component	Technology
Microcontroller	ESP32-CAM
Backend	Flask (Python)
AI Model	YOLOv8 (Ultralytics)
Vision Processing	OpenCV
SMS Service	Twilio
Streaming	MJPEG over WiFi
📂 Project Structure
AI_Child_Safety/
│
├── app.py
├── board_config.h
├── templates/
│   └── index.html
├── incidents/
│   └── alert_*.jpg
├── yolov8n.pt
└── venv/
🚀 Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/yourusername/AI_Child_Safety.git
cd AI_Child_Safety
2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate
3️⃣ Install Dependencies
pip install flask opencv-python ultralytics twilio requests
4️⃣ Run Flask Server
python app.py

Server will run at:

http://127.0.0.1:5000
⚙ ESP32-CAM Configuration

Optimized for smooth streaming:

Frame Size: QVGA (320x240)

JPEG Quality: 18

Double Frame Buffer

WiFi Sleep Disabled

After uploading code, open:

http://ESP32_IP

Stream link:

http://ESP32_IP:81/stream
📊 Risk Levels
Risk Level	Meaning
10	Safe
80+	Warning
95+	Critical
100	Fall Detected
💡 Real-World Applications

👶 Baby monitoring system

🏫 Kindergarten safety

🏠 Smart home child safety

🏥 Pediatric ward monitoring

🛡 AI-based surveillance research

🔐 Security Notice

⚠ Never expose:

Twilio SID

Twilio Auth Token

WiFi Credentials

Store them securely using environment variables.

📈 Future Improvements

🤖 Auto-follow child mode

📊 Live risk analytics dashboard

📱 Mobile app integration

☁ Cloud database logging

🧠 Edge AI on ESP32-S3

🏆 Innovation Highlights

✔ AI + Robotics Integration
✔ Real-time Fall Detection
✔ Proximity-Based Danger Analysis
✔ IoT Live Streaming
✔ Automated Emergency Alerts

📜 License

This project is licensed under the MIT License.

👨‍💻 Author

Sammidi Vinod Kumar
AI + Robotics Enthusiast
