# voice-scribbler
Voice Scribbler: A voice-controlled automatic writing machine that converts speech to handwriting using G-code and Microcontroller control.
## 🚀 Features

- 🎙️ Converts voice to text using speech recognition
- ✒️ Translates text to SVG and G-code
- 🤖 Controls X-Y plotter to write with a pen
- 🛠️ Microcontroller firmware parses G-code for motion
- 🔁 End-to-end automation from speech to handwriting

---

## 📂 Project Structure

voice-scribbler/
│
├── firmware/ # Microcontroller code (e.g. for Raspberry Pi Pico / PIC)
│ └── pico_gcode_parser.py
│
├── speech_to_text/ # Python script to recognize voice and store as text
│ └── recognize_voice.py
│
├── automation/ # Scripts to automate SVG generation and plotting
│ └── convert_and_plot.ps1
│
├── examples/ # Sample G-code or SVG outputs
│ └── hello_world.gcode
│
├── README.md
└── requirements.txt # Python dependencies

---

## 🧠 Technologies Used

- **MicroPython / Embedded C** – Firmware for G-code parsing and plotter control  
- **Python** – Speech recognition and automation scripts  
- **Google Speech API** – Voice-to-text conversion  
- **Inkscape + AxiDraw Extension** – SVG to G-code generation  
- **Servo Motor & Stepper Motor Drivers** – For pen lift and X-Y motion

---

## 🛠️ Setup Instructions

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt

2. Run Voice Recognition

cd speech_to_text
python recognize_voice.py
3. Convert Text to G-code and Plot
Ensure:

Inkscape is installed

AxiDraw extension is configured

PowerShell automation script is edited with correct paths

Then:

powershell
Copy
Edit
powershell .\automation\convert_and_plot.ps1
4. Upload Firmware
Upload the pico_gcode_parser.py to Raspberry Pi Pico (or your microcontroller) using Thonny or USB connection
