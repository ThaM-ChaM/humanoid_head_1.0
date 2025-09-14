
#!/home/kuweni/ssd/conda/envs/venv/bin/python3

import sys
sys.path.append('/home/kuweni/ssd')

# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import String, Bool, Int32, Int16
from array import array
from collections import deque
import pyaudio
import usb.core
from Python_Scripts.Natural_Conversation_System.Speech_to_Text.Respeaker_mic_array.usb_4_mic_array.tuning import Tuning
from custom_interfaces.msg import People, PeopleArray
import wave
import time

import pyaudio
import wave
import numpy as np
import os
import threading


p = pyaudio.PyAudio()
num_devices = p.get_device_count()

# Iterate over all the devices
for i in range(0, num_devices):
    # Get device info for the current device
    device_info = p.get_device_info_by_index(i)
    
    # Check if the device has input channels (i.e., it's a microphone)
    if device_info.get('maxInputChannels') > 0 and device_info.get('name')[:30] == "ReSpeaker 4 Mic Array (UAC1.0)":
        # print(f"Input Device id {i} - {device_info.get('name')}")
        device_index = i
        print(f"Respaker mic array detected with device id {i}")


# Configuration
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6  # Adjust based on firmware
RESPEAKER_WIDTH = 2
RESPEAKER_INDEX = device_index # Update this to the correct device index
CHUNK = 1024 
RECORD_SECONDS = 10
OUTPUT_DIR = "./recorded_6_channels/recordings"

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Initialize PyAudio
# p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(
    rate=RESPEAKER_RATE,
    format=p.get_format_from_width(RESPEAKER_WIDTH),
    channels=RESPEAKER_CHANNELS,
    input=True,
    input_device_index=RESPEAKER_INDEX,
)

# USB Device
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
if not dev:
    print(f'ReSpeaker USB device not found! Exiting.')
    



# def recorder():
#     print("HI recorder")
#     print("* Recording...")

#     # Prepare storage for each channel
#     frames = [[] for _ in range(RESPEAKER_CHANNELS)]

#     for _ in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
#         data = stream.read(CHUNK)
#         audio_data = np.frombuffer(data, dtype=np.int16)

#         # Separate channels and store data
#         for ch in range(RESPEAKER_CHANNELS):
#             frames[ch].append(audio_data[ch::RESPEAKER_CHANNELS].tobytes())

#     print("* Done recording")

#     # Stop and close the stream
#     stream.stop_stream()
#     stream.close()
#     p.terminate()

#     # Save each channel as a separate WAV file
#     for ch in range(RESPEAKER_CHANNELS):
#         filename = os.path.join(OUTPUT_DIR, f"channel_{ch}.wav")
#         with wave.open(filename, 'wb') as wf:
#             wf.setnchannels(1)  # Mono file for each channel
#             wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
#             wf.setframerate(RESPEAKER_RATE)
#             wf.writeframes(b''.join(frames[ch]))

#     print(f"All channels saved in '{OUTPUT_DIR}'")



# def direction():
#     print("Hi direction")
#     tuning = Tuning(dev)
#     angle = int((int(tuning.direction) + 180) % 360) - 180
#     print(angle)
#     pass






# def main():
#     """Main function to start face tracking and recognition threads."""
#     # Start tracking thread
#     thread_track = threading.Thread(
#         target=recorder)
#     thread_track.start()

#     # Start recognition thread
#     thread_recognize = threading.Thread(target=direction)
#     thread_recognize.start()


# if __name__ == "__main__":
#     main()


def recorder():
    while True:
        global speaking
        if speaking:
            print("* Recording...")
            
            frames = [[] for _ in range(RESPEAKER_CHANNELS)]

            try:
                for _ in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
                    try:
                        data = stream.read(CHUNK, exception_on_overflow=False)
                    except IOError as e:
                        print(f"[Recorder] Stream read error: {e}")
                        continue

                    audio_data = np.frombuffer(data, dtype=np.int16)

                    for ch in range(RESPEAKER_CHANNELS):
                        frames[ch].append(audio_data[ch::RESPEAKER_CHANNELS].tobytes())
            finally:
                print("* Done recording")
                stream.stop_stream()
                stream.close()
                # p.terminate()  # Don't terminate here if another thread is using PyAudio

                for ch in range(RESPEAKER_CHANNELS):
                    filename = os.path.join(OUTPUT_DIR, f"channel_{ch}.wav")
                    with wave.open(filename, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
                        wf.setframerate(RESPEAKER_RATE)
                        wf.writeframes(b''.join(frames[ch]))

                print(f"All channels saved in '{OUTPUT_DIR}'")


                global record_finish
                record_finish = True
            break
                


def direction():
    print("* Getting direction...")
    tuning = Tuning(dev)
    global record_finish
    global speaking

    while True: 
        if tuning.is_speech():
            speaking = True
        if record_finish:
            break # Or use while True if you want continuous direction logging
        angle = int((int(tuning.direction) + 180) % 360) - 180
        print(f"[Direction] Angle: {angle}")
        time.sleep(0.1)


def main():
    global record_finish
    record_finish = False
    global speaking
    speaking = False
    print("entering main function")
    thread_rec = threading.Thread(target=recorder)
    thread_dir = threading.Thread(target=direction)

    thread_rec.start()
    print("start thread_rec")
    thread_dir.start()
    print("thread_dir")

    thread_rec.join()
    thread_dir.join()

    # Now it's safe to terminate PyAudio
    p.terminate()

if __name__ == "__main__":
    main()

