#!/home/kuweni/ssd/conda/envs/venv/bin/python3

import sys
sys.path.append('/home/kuweni/ssd')

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, Int32
from array import array
import pyaudio
from collections import deque
import numpy as np
import usb.core
from Python_Scripts.Natural_Conversation_System.Speech_to_Text.Respeaker_mic_array.usb_4_mic_array.tuning import Tuning
import wave
import time
import subprocess
import json
import math
import os


class RespeakerAudioRecorder(Node):
    def __init__(self):
        super().__init__('respeaker_audio_recorder_node')
        # self.publisher_ = self.create_publisher(String, 'audio_file_path', 10)
        self.publisher_time = self.create_publisher(Int32, 'full_process_time', 10)
        # self.publisher_response_generation = self.create_publisher(Bool, 'response_genration_flag', 10)
        self.publisher_pause_detection = self.create_publisher(String, 'speech_pause', 10)
        self.publisher_ch0_mic_audio = self.create_publisher(String , 'ch0_mic_audio_path', 10)
        # self.publisher_2 = self.create_publisher(Bool, 'end_sentence', 10)
        # self.subscription_mouth_flag = self.create_subscription(Bool, 'mouth_flag', self.mouth_flag_callback, 10)
        self.subscription_end_audio_response = self.create_subscription(Bool, 'end_audio_response', self.end_audio_response_callback, 10)
        # self.sub2 = self.create_subscription(String,"example", self.callback, 10)

        self.mouth_flag = False  
        self.counter = 1
        self.got_a_sentence = False
        # self.audio_save_path = f'/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/audio_{self.counter}.wav'

        # Parameters
        self.pa = pyaudio.PyAudio()

        # Get the number of available audio devices
        num_devices = self.pa.get_device_count()

        # Iterate over all the devices
        for i in range(0, num_devices):
            # Get device info for the current device
            device_info = self.pa.get_device_info_by_index(i)
            
            # Check if the device has input channels (i.e., it's a microphone)
            if device_info.get('maxInputChannels') > 0 and device_info.get('name')[:30] == "ReSpeaker 4 Mic Array (UAC1.0)":
                # print(f"Input Device id {i} - {device_info.get('name')}")
                self.device_index = i
                print(f"Respaker mic array detected with device id {i}")
                
        # Initialize audio settings
        self.rate = 16000
        self.channels = 6
        self.width = 2
        self.chunk_duration_ms = 30
        self.chunk_size = int(self.rate * self.chunk_duration_ms / 1000) * self.channels
        # self.device_index = self.get_parameter('device_index').get_parameter_value().integer_value

        # Other configurations
        # self.ring_buffer = deque(maxlen=int(750 / self.chunk_duration_ms))
        self.triggered = False


        # USB Device
        self.dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
        if not self.dev:
            self.get_logger().error('ReSpeaker USB device not found! Exiting.')
            return

        self.tuning = Tuning(self.dev)
        # self.tuning.set_vad_threshold(8) #8
        self.true_threshold = 2
        self.sentence_pause_threshold = 5
        self.sentence_end_threshold = 15

        # PyAudio Stream
        
        self.stream = self.pa.open(
            rate=self.rate,
            format=self.pa.get_format_from_width(self.width),
            channels=self.channels,
            input=True,
            start=False,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size
        )

        self.base_path = '/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/'
        self.raw_save_path = '/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/audio.raw'

        self.get_logger().info('Respeaker Audio Recorder Node Initialized.')
        self.record_audio()

        self.start = None

    # def mouth_flag_callback(self, msg):
    #     """Callback to update the mouth_flag state based on the topic."""
    #     # self.mouth_flag = msg.data
    #     self.get_logger().info(f"Received mouth_flag: {self.mouth_flag}")

    def end_audio_response_callback(self, msg: Bool):
        # end_audio_response = msg.data
        self.get_logger().info(f"End of audio response")
        if msg.data:
            self.got_a_sentence = False
        self.record_audio()

    # def callback(self, msg):
    #     self.get_logger().info("got it")

    # def cartesian_to_azimuth(self, x, y):
    #     angle = math.atan2(y, x)
    #     degrees = math.degrees(angle)
    #     return round(degrees)


    def record_audio(self):
        self.stream.start_stream()
        self.get_logger().info('Listening for human voice...')

        raw_data_all_channels = []  # List to collect NumPy chunks
        got_a_pause = False
        true_cnt = 0
        false_cnt = 0
        pause_cnt = 0

        self.pre_speech_buffer = deque(maxlen=18)

        try:
            while not self.got_a_sentence:
                chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)

                # Convert chunk to NumPy array and reshape
                chunk_np = np.frombuffer(chunk, dtype=np.int16).reshape(-1, self.channels)

                # Slice only channels 0 to 4
                # frames_0_to_4 = chunk_np[:, :6]

                self.pre_speech_buffer.append(chunk_np)

                # Append this chunk to our list
                raw_data_all_channels.append(chunk_np)

                # print("checking voice")
                if self.tuning.is_speech(): #and self.tuning.is_voice():
                    true_cnt += 1
                    false_cnt = 0
                else:
                    true_cnt = 0
                    false_cnt += 1
                # print("finish checking")

                if not self.triggered:
                    if true_cnt > self.true_threshold:
                        self.get_logger().info('Detected human voice! Starting recording...')
                        self.sentence_start_time = time.time()
                        self.human_speech_detected_time = time.time()
                        self.triggered = True
                        raw_data_all_channels = list(self.pre_speech_buffer)  
                        msg_start_time = Int32()
                        msg_start_time.data = int(self.human_speech_detected_time)
                        self.publisher_time.publish(msg_start_time)
                        # raw_data_all_channels = [frames_0_to_4]  # Start fresh from this chunk

                elif false_cnt == self.sentence_pause_threshold:
                    self.get_logger().info("Detected a pause in the speech.")
                    # self.get_logger().info(f"time taken {time.time() - self.sentence_start_time}")
                    if (time.time() - self.sentence_start_time) >= 1:
                        # self.get_logger().info("Sending the current record to speech separation node")
                        # print(f"Source direction from mic {int((int(self.tuning.direction) + 90) % 360) - 180}")
                        # Stack all chunks and save
                        audio_np = np.vstack(raw_data_all_channels)
                        self.save_audio(audio_np)
                        
                        self.sentence_start_time = time.time()
                        raw_data_all_channels = [chunk_np]#[frames_0_to_4]  # Start next recording
                    else:
                        self.triggered = True
                        true_cnt = 0
                        false_cnt  = 0
                        

                elif false_cnt > self.sentence_end_threshold:
                    self.get_logger().info('Detected end of human voice.')
                    self.start = time.time()
                    self.triggered = False
                    self.got_a_sentence = True
                    got_a_pause = False
                    msg_pause_detection = String()
                    msg_pause_detection.data = "end"
                    self.publisher_pause_detection.publish(msg_pause_detection)
                    # azimuth = self.run_odas_on_raw(self.raw_save_path)
                    # if azimuth is not None:
                    #     self.get_logger().info(f'Detected Direction: {azimuth}°')
                    # else:
                    #     self.get_logger().info('Direction not detected.')

            self.stream.stop_stream()

        except Exception as e:
            self.get_logger().error(f'Error while recording: {e}')



    def save_audio(self, audio_np):
 
        # base_path = '/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/'
        audio_save_path = f'{self.base_path}audio_{self.counter}.wav'
        # raw_save_path = f'{base_path}audio.raw'

        try:
            # Save channel 0 WAV file
            channel_0 = audio_np[:, 0]  # Take channel 0 (shape: [samples])
            channel_0_bytes = channel_0.astype(np.int16).tobytes()

            # channel_0_bytes = np.array(raw_data_channel_0, dtype=np.int16).tobytes()

            # print("created channel 0 bytes")

            with wave.open(audio_save_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(self.pa.get_sample_size(self.pa.get_format_from_width(self.width)))
                wav_file.setframerate(self.rate)
                wav_file.writeframes(channel_0_bytes)

            msg_ch0_mic_audio = String()
            msg_ch0_mic_audio.data = audio_save_path
            self.publisher_ch0_mic_audio.publish(msg_ch0_mic_audio)

            
            # self.get_logger().info(f'Saved channel 0 WAV to {audio_save_path}')

            """audio_np is a NumPy array of shape (n_samples, 5)"""
            interleaved_data = audio_np.astype(np.int16).flatten()
            with open(self.raw_save_path, 'wb') as f:
                f.write(interleaved_data.tobytes())

            msg_pause_detection = String()
            msg_pause_detection.data = "pause"
            self.publisher_pause_detection.publish(msg_pause_detection)

            # azimuth = self.run_odas_on_raw(self.raw_save_path)
            # if azimuth is not None:
            #     self.get_logger().info(f'Detected Direction: {azimuth}°')
            #     doa = ((azimuth + 315) % 360)  - 180
            #     self.get_logger().info(f"Motor direction: {doa}")
            #     msg = Int32()
            #     msg.data = doa
            #     self.publisher_doa.publish(msg)
            #     self.get_logger().info(f"doa: {doa}")
            # else:
            #     self.get_logger().info('Direction not detected.')

            self.counter += 1

        except Exception as e:
            self.get_logger().error(f'Error saving audio: {e}')

        
    # def run_odas_on_raw(self, raw_path):
    #     print("Starting ODASLive sound tracker...")

    #     az = None

    #     # Path to the ODAS live tracker executable and its configuration file
    #     odas_cmd = [
    #         "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_enhancement/Odas/odas/build/bin/odaslive",
    #         "-c",
    #         "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_enhancement/Odas/odas/config/odaslive/respeaker_usb_4_mic_array.cfg"
    #     ]

    #     try:
    #         # Start the ODAS process
    #         process = subprocess.Popen(
    #             odas_cmd,
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.STDOUT,
    #             bufsize=1
    #         )
    #         # Initialize a variable to accumulate the partial JSON data
    #         partial_data = ""
    #         # start_time = time.time()
    #         # timeout = 2  # seconds

    #         while True:
    #             # if time.time() - start_time > timeout:
    #             #     process.terminate()
    #             #     break

    #             # time.sleep(0.0001)
    #             line = process.stdout.readline()
    #             if not line:
    #                 break

    #             try:
    #                 # Decode and strip any unwanted characters from the line
    #                 line_str = line.decode("utf-8").strip()

    #                 # Accumulate the lines to build the full JSON object
    #                 partial_data += line_str

    #                 # Check if we have a complete JSON object (i.e., starts with '{' and ends with '}')
    #                 if partial_data.startswith("{") and partial_data.endswith("}"):
    #                     # Try to load the accumulated JSON data
    #                     data = json.loads(partial_data)

    #                     # Reset partial data after successful parsing
    #                     partial_data = ""

    #                     if "src" in data:
    #                         sources = data["src"]
    #                         timestamp = data.get('timeStamp', '-')
    #                         if 220 > timestamp > 200:
    #                             print(data)
    #                             print()
    #                         # print(data)
    #                         # print()
    #                         # Iterate over the sound sources and calculate azimuth for sources with non-zero ID
    #                         valid_sources = 0  # Counter for valid sources
    #                         for i, src in enumerate(sources):
    #                             #  print("i ", i)
    #                             # print("src ", src)
    #                             if "E" in src and src["E"] > 0.5: # Exclude ID 0 sources
    #                                 valid_sources += 1
    #                                 x, y = src["x"], src["y"]
    #                                 az = self.cartesian_to_azimuth(x, y)
    #                                 # print(f"Time: {timestamp}")
    #                                 # print(f"Source {valid_sources}: Azimuth = {az}°")
                                
    #                         # print()
    #                         # if valid_sources == 0:
    #                         #     print("⚠️ No valid sources with non-zero IDs detected.")
                            
    #                 # If we didn't have a valid JSON, just continue accumulating
    #             except json.JSONDecodeError:
    #                 # Skip lines that are not JSON or can't be parsed
    #                 continue
    #             except Exception as e:
    #                 # Handle any other exceptions, e.g., in case of malformed data
    #                 print(f"Error processing line: {e}")
    #                 continue
        
    #     except Exception as e:
    #         self.get_logger().error(f'ODAS tracker error: {e}')
    #     finally:
    #         process.terminate()
    #     return az

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
        audio_recorder_node.get_logger().info('Shutting down Respeaker Audio Recorder Node.')
    finally:
        audio_recorder_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()