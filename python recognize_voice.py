#speech_to_text4
import speech_recognition as sr
import os
import subprocess

# create a recognizer instance using the recognizer method
r = sr.Recognizer()

# get a list of available audio input devices
devices = sr.Microphone.list_microphone_names()
print(devices)

file = open("output.txt", "w")
# find the index of the Bluetooth earphone in the device list
bluetooth_device_index = 0

# getting all devices connected to the computer and selecting the required input device
for i, device in enumerate(devices):
    print(device)
    if 'headset (wi-xb400)' in device.lower():
        bluetooth_device_index = i
        break

# if Bluetooth earphone is found, use it as the audio source
if bluetooth_device_index is not None:
    # setting the selected device as input microphone
    collected_text = ""
    try:
        with sr.Microphone(device_index=bluetooth_device_index) as source:
            print("Listening...")
            while True:
                # listen for audio and convert it to text
                audio = r.listen(source)
                # using respective methods for sending recorded audio to Google's STT API
                try:
                    text = r.recognize_google(audio)
                    print(f"Text: {text}")
                    file.write(text)
                    collected_text += text + " "
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Request error: {e}")
    except KeyboardInterrupt:
        print("\nStopping speech recognition...")

        # Save text
        with open("output.txt", "w") as file:
            file.write("\n".join(collected_text.strip().split("\n")))

        ps_script_path = r"C:\Users\Sowmya\OneDrive\Desktop\my_project\generate_and_open.ps1"

        if os.path.exists(ps_script_path):
            print("Generating SVG and opening in Inkscape...")
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script_path], shell=True)
        else:
            print(f"Error: PowerShell script not found at {ps_script_path}")

else:
    print("Bluetooth earphone not found")
