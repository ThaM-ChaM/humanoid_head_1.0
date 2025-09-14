# #!/home/kuweni/ssd/conda/envs/venv/bin/python3

# import sys
# sys.path.append('/home/kuweni/ssd')

# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import String
# from array import array
# from collections import deque
# import pyaudio
# import usb.core
# from Python_Scripts.Natural_Conversation_System.Speech_to_Text.Respeaker_mic_array.usb_4_mic_array.tuning import Tuning
# import wave
# import threading
# import subprocess
# import json
# import math
# import time

# # Utility: Convert (x, y) to azimuth angle
# def cartesian_to_azimuth(x, y):
#     angle = math.atan2(y, x)
#     degrees = math.degrees(angle)
#     return round(degrees)

# # Thread function: run ODAS tracker to get azimuth
# class ODASTracker(threading.Thread):
#     def __init__(self):
#         super().__init__()
#         self.azimuth = None
#         self.running = True
#         self.daemon = True

#     def run(self):
#         odas_cmd = [
#             "/media/dell/New Volume/Semester 7/EN4203 - Project - FYP/Moshintha's workspace/respeaker_mic_array_2.0/odas/build/bin/odaslive",
#             "-c",
#             "/media/dell/New Volume/Semester 7/EN4203 - Project - FYP/Moshintha's workspace/respeaker_mic_array_2.0/odas/config/odaslive/respeaker_usb_4_mic_array.cfg"
#         ]

#         try:
#             process = subprocess.Popen(odas_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
#             partial_data = ""

#             while self.running:
#                 time.sleep(0.0001)
#                 line = process.stdout.readline()
#                 if not line:
#                     break
#                 try:
#                     line_str = line.decode("utf-8").strip()
#                     partial_data += line_str
#                     if partial_data.startswith("{") and partial_data.endswith("}"):
#                         data = json.loads(partial_data)
#                         partial_data = ""
#                         if "src" in data:
#                             for src in data["src"]:
#                                 if "E" in src and src["E"] > 0.6:
#                                     x, y = src["x"], src["y"]
#                                     self.azimuth = cartesian_to_azimuth(x, y)
#                 except:
#                     continue
#         except Exception as e:
#             print(f"ODAS tracker error: {e}")
#         finally:
#             process.terminate()

#     def stop(self):
#         self.running = False


# class RespeakerAudioRecorder(Node):
#     def __init__(self):
#         super().__init__('respeaker_audio_recorder_node')
#         self.publisher_ = self.create_publisher(String, 'audio_file_path', 10)
#         self.counter = 1

#         self.declare_parameter('audio_save_path', f'/home/dell/fyp_ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio_inputs/audio_{self.counter}.wav')
#         self.declare_parameter('device_index', 6)
#         self.declare_parameter('chunk_duration_ms', 30)

#         self.rate = 16000
#         self.channels = 1
#         self.width = 2
#         self.chunk_duration_ms = self.get_parameter('chunk_duration_ms').get_parameter_value().integer_value
#         self.chunk_size = int(self.rate * self.chunk_duration_ms / 1000) * self.channels
#         self.device_index = self.get_parameter('device_index').get_parameter_value().integer_value

#         self.ring_buffer = deque(maxlen=int(1200 / self.chunk_duration_ms))
#         self.triggered = False

#         self.dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
#         if not self.dev:
#             self.get_logger().error('ReSpeaker USB device not found! Exiting.')
#             return

#         self.tuning = Tuning(self.dev)

#         self.pa = pyaudio.PyAudio()
#         self.stream = self.pa.open(
#             rate=self.rate,
#             format=self.pa.get_format_from_width(self.width),
#             channels=self.channels,
#             input=True,
#             start=False,
#             input_device_index=self.device_index,
#             frames_per_buffer=self.chunk_size
#         )

#         # Start ODAS tracker
#         self.odas_tracker = ODASTracker()
#         self.odas_tracker.start()

#         self.get_logger().info('Respeaker Audio Recorder with ODAS Tracking Started.')
#         self.record_audio()

#     def record_audio(self):
#         while rclpy.ok():
#             self.stream.start_stream()
#             raw_data = array('h')
#             got_a_sentence = False

#             try:
#                 while not got_a_sentence:
#                     chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
#                     raw_data.extend(array('h', chunk))

#                     is_speech = self.tuning.is_speech()
#                     self.ring_buffer.append(is_speech)

#                     if not self.triggered:
#                         if is_speech == 1:
#                             self.get_logger().info('🎙️ Human voice detected. Recording...')
#                             self.triggered = True
#                             raw_data = array('h', chunk)
#                             self.ring_buffer.clear()
#                     else:
#                         if all(val == 0 for val in self.ring_buffer):
#                             self.get_logger().info('🛑 End of speech.')
#                             self.triggered = False
#                             got_a_sentence = True

#                 self.stream.stop_stream()
#                 self.save_audio(raw_data)

#             except Exception as e:
#                 self.get_logger().error(f'Error while recording: {e}')

#     def save_audio(self, raw_data):
#         base_path = '/home/dell/fyp_ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio_inputs/'
#         audio_save_path = f'{base_path}audio_{self.counter}.wav'

#         try:
#             with wave.open(audio_save_path, 'wb') as wav_file:
#                 wav_file.setnchannels(self.channels)
#                 wav_file.setsampwidth(self.pa.get_sample_size(self.pa.get_format_from_width(self.width)))
#                 wav_file.setframerate(self.rate)
#                 wav_file.writeframes(raw_data.tobytes())

#             azimuth = self.odas_tracker.azimuth
#             self.get_logger().info(f'✅ Audio saved: {audio_save_path}')
#             if azimuth is not None:
#                 self.get_logger().info(f'🎯 Detected Direction: {azimuth}°')
#             else:
#                 self.get_logger().info('❌ Direction not detected.')

#             msg = String()
#             msg.data = audio_save_path
#             self.publisher_.publish(msg)

#             self.counter += 1

#         except Exception as e:
#             self.get_logger().error(f'Error saving audio: {e}')

#     def destroy_node(self):
#         self.stream.close()
#         self.pa.terminate()
#         self.odas_tracker.stop()
#         super().destroy_node()


# def main(args=None):
#     rclpy.init(args=args)
#     audio_recorder_node = RespeakerAudioRecorder()
#     try:
#         rclpy.spin(audio_recorder_node)
#     except KeyboardInterrupt:
#         audio_recorder_node.get_logger().info('🔻 Shutting down...')
#     finally:
#         audio_recorder_node.destroy_node()
#         rclpy.shutdown()


# if __name__ == '__main__':
#     main()


#!/usr/bin/env python3

import sys
sys.path.append('/home/kuweni/ssd')

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from array import array
from collections import deque
import pyaudio
import usb.core
from Python_Scripts.Natural_Conversation_System.Speech_to_Text.Respeaker_mic_array.usb_4_mic_array.tuning import Tuning
import wave
import threading
import subprocess
import json
import math
import time
import os

# Utility: Convert (x, y) to azimuth angle
def cartesian_to_azimuth(x, y):
    angle = math.atan2(y, x)
    degrees = math.degrees(angle)
    return round(degrees)

class RespeakerAudioRecorder(Node):
    def __init__(self):
        super().__init__('respeaker_audio_recorder_node')
        self.publisher_ = self.create_publisher(String, 'audio_file_path', 10)
        self.counter = 1

        self.declare_parameter('audio_save_path', f'/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/audio_{self.counter}.wav')
        self.declare_parameter('device_index', 24)
        self.declare_parameter('chunk_duration_ms', 30)

        self.rate = 16000
        self.channels = 6
        self.width = 2
        self.chunk_duration_ms = self.get_parameter('chunk_duration_ms').get_parameter_value().integer_value
        self.chunk_size = int(self.rate * self.chunk_duration_ms / 1000) * self.channels
        self.device_index = self.get_parameter('device_index').get_parameter_value().integer_value

        self.ring_buffer = deque(maxlen=int(1200 / self.chunk_duration_ms))
        self.triggered = False

        self.dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
        if not self.dev:
            self.get_logger().error('ReSpeaker USB device not found! Exiting.')
            return

        self.tuning = Tuning(self.dev)

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.rate,
            format=self.pa.get_format_from_width(self.width),
            channels=self.channels,
            input=True,
            start=False,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size
        )

        self.get_logger().info('Respeaker Audio Recorder with RAW ODAS File Tracking Started.')
        self.record_audio()

    def record_audio(self):
        while rclpy.ok():
            self.stream.start_stream()
            raw_data = array('h')
            got_a_sentence = False

            try:
                while not got_a_sentence:
                    chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    raw_data.extend(array('h', chunk))

                    is_speech = self.tuning.is_speech()
                    self.ring_buffer.append(is_speech)

                    if not self.triggered:
                        if is_speech == 1:
                            self.get_logger().info('🎙️ Human voice detected. Recording...')
                            self.triggered = True
                            raw_data = array('h', chunk)
                            self.ring_buffer.clear()
                    else:
                        if all(val == 0 for val in self.ring_buffer):
                            self.get_logger().info('🛑 End of speech.')
                            self.triggered = False
                            got_a_sentence = True

                self.stream.stop_stream()
                self.save_audio(raw_data)

            except Exception as e:
                self.get_logger().error(f'Error while recording: {e}')

    def save_audio(self, raw_data):
        base_path = '/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/'
        audio_save_path = f'{base_path}audio_{self.counter}.wav'
        raw_save_path = f'{base_path}audio.raw'

        try:
            # Save WAV
            with wave.open(audio_save_path, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.pa.get_sample_size(self.pa.get_format_from_width(self.width)))
                wav_file.setframerate(self.rate)
                wav_file.writeframes(raw_data.tobytes())
            print(type(raw_data))

            # Save RAW
            with open(raw_save_path, 'wb') as raw_file:
                raw_file.write(raw_data.tobytes())


            self.get_logger().info(f'Audio saved: {audio_save_path}')
            self.get_logger().info(f'Raw file saved: {raw_save_path}')

            msg = String()
            msg.data = audio_save_path
            self.publisher_.publish(msg)

            # Run ODAS with raw file
            azimuth = self.run_odas_on_raw(raw_save_path)
            if azimuth is not None:
                self.get_logger().info(f'🎯 Detected Direction: {azimuth}°')
            else:
                self.get_logger().info('❌ Direction not detected.')

            self.counter += 1

        except Exception as e:
            self.get_logger().error(f'Error saving audio: {e}')

    def run_odas_on_raw(self, raw_path):
        print("Starting ODASLive sound tracker... Press Ctrl+C to stop.")

        # Path to the ODAS live tracker executable and its configuration file
        odas_cmd = [
            "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_enhancement/Odas/odas/build/bin/odaslive",
            "-c",
            "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_enhancement/Odas/odas/config/odaslive/respeaker_usb_4_mic_array.cfg"
        ]

        try:
            # Start the ODAS process
            process = subprocess.Popen(
                odas_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1
            )
            # Initialize a variable to accumulate the partial JSON data
            partial_data = ""
            start_time = time.time()
            timeout = 2  # seconds

            while True:
                if time.time() - start_time > timeout:
                    process.terminate()
                    break

                time.sleep(0.0001)
                line = process.stdout.readline()
                if not line:
                    break

                try:
                    # Decode and strip any unwanted characters from the line
                    line_str = line.decode("utf-8").strip()

                    # Accumulate the lines to build the full JSON object
                    partial_data += line_str

                    # Check if we have a complete JSON object (i.e., starts with '{' and ends with '}')
                    if partial_data.startswith("{") and partial_data.endswith("}"):
                        # Try to load the accumulated JSON data
                        data = json.loads(partial_data)

                        # Reset partial data after successful parsing
                        partial_data = ""

                        if "src" in data:
                            sources = data["src"]
                            timestamp = data.get('timeStamp', '-')
                            print(data)

                            # Iterate over the sound sources and calculate azimuth for sources with non-zero ID
                            valid_sources = 0  # Counter for valid sources
                            for i, src in enumerate(sources):
                                #  print("i ", i)
                                #  print("src ", src)
                                if "E" in src and src["E"] > 0.6: # Exclude ID 0 sources
                                    valid_sources += 1
                                    x, y = src["x"], src["y"]
                                    az = cartesian_to_azimuth(x, y)
                                    # print(f"\n🎯 Time: {timestamp}")
                                    print(f"Source {valid_sources}: Azimuth = {az}°")
                                
                            # print()
                            # if valid_sources == 0:
                            #     print("⚠️ No valid sources with non-zero IDs detected.")
                            
                    # If we didn't have a valid JSON, just continue accumulating
                except json.JSONDecodeError:
                    # Skip lines that are not JSON or can't be parsed
                    continue
                except Exception as e:
                    # Handle any other exceptions, e.g., in case of malformed data
                    print(f"⚠️ Error processing line: {e}")
                    continue
        
        except Exception as e:
            self.get_logger().error(f'ODAS tracker error: {e}')
        finally:
            process.terminate()
        
        return az
        # except KeyboardInterrupt:
        #     # Graceful shutdown on Ctrl+C
        #     print("\nStopping ODASLive...")
        #     process.terminate()
        #     process.wait()
        #     print("ODASLive stopped.")

        # # Set up ODAS command
        # odas_cmd = [
        #     "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_enhancement/Odas/odas/build/bin/odaslive",
        #     "-c",
        #     "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_enhancement/Odas/odas/config/odaslive/respeaker_usb_4_mic_array.cfg"
        # ]

        # # # Update the config input to the raw file (optional: use dynamic config editing if needed)
        # # os.environ["ODAS_RAW_FILE"] = raw_path  # Custom env var if ODAS config supports it

        # azimuth = None
        # try:
        #     process = subprocess.Popen(odas_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
        #     start_time = time.time()
        #     timeout = 3  # seconds

        #     partial_data = ""

        #     while True:
        #         if time.time() - start_time > timeout:
        #             process.terminate()
        #             break

        #         line = process.stdout.readline()
        #         if not line:
        #             break
        #         try:
        #             line_str = line.decode("utf-8").strip()
        #             partial_data += line_str
        #             if partial_data.startswith("{") and partial_data.endswith("}"):
        #                 data = json.loads(partial_data)
        #                 partial_data = ""
        #                 if "src" in data:
        #                     for src in data["src"]:
        #                         if "E" in src and src["E"] > 0.6:
        #                             x, y = src["x"], src["y"]
        #                             azimuth = cartesian_to_azimuth(x, y)
        #         except:
        #             continue
        # except Exception as e:
        #     self.get_logger().error(f'ODAS tracker error: {e}')
        # finally:
        #     process.terminate()

        # return azimuth

    def destroy_node(self):
        self.stream.close()
        self.pa.terminate()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    audio_recorder_node = RespeakerAudioRecorder()
    try:
        rclpy.spin(audio_recorder_node)
    except KeyboardInterrupt:
        audio_recorder_node.get_logger().info('🔻 Shutting down...')
    finally:
        audio_recorder_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()