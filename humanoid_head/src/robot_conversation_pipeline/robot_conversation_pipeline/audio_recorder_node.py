#!/home/kuweni/ssd/conda/envs/venv/bin/python3

from multiprocessing import get_logger
import sys
sys.path.append('/home/kuweni/ssd')

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, Int32, Int16, Empty
from array import array
from collections import deque
import pyaudio
import usb.core
from Python_Scripts.Natural_Conversation_System.Speech_to_Text.Respeaker_mic_array.usb_4_mic_array.tuning import Tuning
from custom_interfaces.msg import People, PeopleArray
import wave
import time
import random
import os
import csv



class RespeakerAudioRecorder(Node):
    def __init__(self):
        super().__init__('respeaker_audio_recorder_node')
        self.publisher_ = self.create_publisher(String, 'audio_file_path', 10)
        self.publisher_time = self.create_publisher(Int32, 'full_process_time', 10)
        self.doa_pb = self.create_publisher(
            Int32, "doa", 10)
        # self.publisher_response_generation = self.create_publisher(Bool, 'response_genration_flag', 10)
        self.publisher_doa = self.create_publisher(Int16, 'user_doa', 10)
        # self.publisher_2 = self.create_publisher(Bool, 'end_sentence', 10)
        # self.subscription_mouth_flag = self.create_subscription(Bool, 'mouth_flag', self.mouth_flag_callback, 10)
        self.active_users_sub = self.create_subscription(PeopleArray, "active_users", self.active_usrs_callback, 10)
        self.subscription_end_audio_response = self.create_subscription(Bool, 'end_audio_response', self.end_audio_response_callback, 10)
        # self.sub2 = self.create_subscription(String,"example", self.callback, 10)
        self.active_speaker_pub = self.create_publisher(People, "active_speaker",10)
        self.filler_words_pub = self.create_publisher(String, 'filler_words_audio_path', 10)
        
        self.response_start_sub = self.create_subscription(Empty, 'response_start', self.response_audio_start_callback, 10)

        self.mouth_flag = False  
        self.counter = 1
        self.got_a_sentence = False
        self.thinking_reponse_audio_path = None

        self.pa = pyaudio.PyAudio()
        # self.audio_save_path = f'/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/audio_{self.counter}.wav'

        # Parameters
        # self.declare_parameter('audio_save_path', f'/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/audio_{self.counter}.wav')
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
        self.channels = 1
        self.width = 2
        self.chunk_duration_ms = 30
        self.chunk_size = int(self.rate * self.chunk_duration_ms / 1000) * self.channels
        # self.device_index = self.get_parameter('device_index').get_parameter_value().integer_value

        # Other configurations
        # self.ring_buffer = deque(maxlen=int(750 / self.chunk_duration_ms))
        self.triggered = False
        self.active_usrs = []


        # USB Device
        self.dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
        # self.get_logger().info(f" self.dev : {self.dev}")
        if not self.dev:
            self.get_logger().error('ReSpeaker USB device not found! Exiting.')
            return

        self.tuning = Tuning(self.dev)
        # self.tuning.set_vad_threshold(8)
        self.true_threshold = 2
        self.sentence_pause_threshold = 25
        self.false_threshold = 40 #40

        self.pre_speech_buffer = deque(maxlen=20) 

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

        self.get_logger().info('Respeaker Audio Recorder Node Initialized.')
        self.record_audio()

        self.start = None

    # def mouth_flag_callback(self, msg):
    #     """Callback to update the mouth_flag state based on the topic."""
    #     # self.mouth_flag = msg.data
    #     self.get_logger().info(f"Received mouth_flag: {self.mouth_flag}")
    
    def response_audio_start_callback(self, msg: Empty):
        # end_audio_response = msg.data
        self.get_logger().info(f"Start of audio response")
        self.end_time = time.time()
        # self.get_logger().info(f"time taken from the start of detecting a human speech to the end of giving a response {self.end_time-self.human_speech_detected_time}")
        self.get_logger().warn(f"time taken to the response {self.end_time - self.end_of_human_speech}")

            # Path to the CSV file
        # csv_file_path = "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/testing_results/response_time_testing/response_times.csv"

        # # Check if file exists to write header only once
        # file_exists = os.path.isfile(csv_file_path)

        # # Append the response_delay to the CSV
        # with open(csv_file_path, mode='a', newline='') as file:
        #     writer = csv.writer(file)
        #     if not file_exists:
        #         writer.writerow(["ResponseDelay"])  # Header
        #     writer.writerow([self.end_time - self.end_of_human_speech])
            

    def end_audio_response_callback(self, msg: Bool):
        # end_audio_response = msg.data
        self.get_logger().info(f"End of audio response")
        self.end_time = time.time()
        # self.get_logger().info(f"time taken from the start of detecting a human speech to the end of giving a response {self.end_time-self.human_speech_detected_time}")
        # self.get_logger().info(f"time taken from the end of user's speech to the end of giving a response {self.end_time - self.end_of_human_speech}")
        
        if msg.data:
            self.got_a_sentence = False
        self.record_audio()

    # def callback(self, msg):
    #     self.get_logger().info("got it")


    def record_audio(self):
        # while rclpy.ok():
        # print(f"got a sentence, {self.got_a_sentence}")
        # if self.got_a_sentence:
        #     self.get_logger().info("Robot is speaking, not recording.")
        #     time.sleep(0.2)  # Wait for a moment before checking again
        #     return
            # continue  # Skip the recording loop if end of reponse is True
        self.stream.start_stream()
        self.get_logger().info('Listening for human voice...')
        raw_data = array('h')
       
        # self.got_a_sentence = False
        got_a_pause = False
        is_speech_detected = False
        true_cnt = 0
        false_cnt = 0
        pause_cnt = 0
        azimuth = 0
        try:
            while not self.got_a_sentence:
                chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
                raw_data.extend(array('h', chunk))
                chunk_array = array('h', chunk)
                # print(f"Source direction {self.tuning.direction}")
                # msg2 = Bool()
                # msg2.data = False
                # self.publisher_2.publish(msg2)
                if (self.tuning.is_speech()):
                    true_cnt += 1
                    false_cnt = 0
                    
                    # self.get_logger().info(f"Source direction {int((int(self.tuning.direction) + 180) % 360) - 180}")
                    # pause_cnt = 0
                else:
                    true_cnt = 0
                    false_cnt += 1
                    # pause_cnt += 1

                if not self.triggered:
                    # Keep a buffer of the most recent chunks
                    self.pre_speech_buffer.append(chunk_array)

                if is_speech_detected:
                    if ((time.time() - check_direction_time) > 1):  ####################################
                        angle = int((int(self.tuning.direction) + 180) % 360) - 180
                        self.get_logger().info(f"Source direction {angle}")
                        if -100 < angle < 100:
                            azimuth = (angle + azimuth)//2
                        check_direction_time =  time.time()

                # angle = int((int(self.tuning.direction) + 180) % 360) - 180
                # if -100 < angle < 100:
                #     azimuth = angle
                # print(f"Source direction {int((int(self.tuning.direction) + 180) % 360) - 180}")
                if not self.triggered:
                    if true_cnt > self.true_threshold:
                        self.get_logger().info('Detected human voice! Starting recording...')
                        self.sentence_start_time = time.time()
                        self.human_speech_detected_time = self.sentence_start_time
                        is_speech_detected = True
                        check_direction_time =  self.sentence_start_time
                        self.triggered = True
                        raw_data = array('h', chunk)
                        for old_chunk in self.pre_speech_buffer:
                            raw_data.extend(old_chunk)
                        self.get_logger().info(f"Source direction {int((int(self.tuning.direction) + 180) % 360) - 180}")
                        # msg_start_time = Int32()
                        # msg_start_time.data = self.human_speech_detected_time
                        # self.publisher_time.publish(msg_start_time)
                        
                elif false_cnt == self.sentence_pause_threshold:
                    self.get_logger().info("Detected a pause in the speech.")
                    pause_cnt = 0
                    self.got_a_sentence = False
                    got_a_pause = True
                    self.pre_speech_buffer.clear()
                    self.get_logger().info(f"time taken until the pause {time.time()-self.sentence_start_time}")
                    if (time.time()-self.sentence_start_time) >= 1:
                        self.get_logger().info("Sending the current record to stt model")
                        angle = int((int(self.tuning.direction) + 180) % 360) - 180
                        # print(f"Source direction {azimuth}")
                        if -100 < angle < 100:
                            azimuth = (angle + azimuth)//2
                        self.get_logger().info(f"Source direction {azimuth}")
                        msg = Int32()
                        msg.data = azimuth
                        self.doa_pb.publish(msg)
                        self.publish_active_speaker(azimuth)
                            # Path to the CSV file
                        # csv_file_path = "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/testing_results/sound_localization_results/sound_localization_150cm.csv"

                        # # Check if file exists to write header only once
                        # file_exists = os.path.isfile(csv_file_path)

                        # # Append the response_delay to the CSV
                        # with open(csv_file_path, mode='a', newline='') as file:
                        #     writer = csv.writer(file)
                        #     if not file_exists:
                        #         writer.writerow(["SoundDirection"])  # Header
                        #     writer.writerow([azimuth])
                        self.save_audio(raw_data)
                        msg_doa = Int16()
                        msg_doa.data = azimuth
                        self.publisher_doa.publish(msg_doa)
                        self.sentence_start_time = time.time()
                        raw_data = array('h', chunk)
                    else:
                        self.triggered = True
                        true_cnt = 0
                        false_cnt  = 0

                    
                elif false_cnt > self.false_threshold:
                    self.get_logger().info('Detected end of human voice.')
                    self.start = time.time()
                    self.end_of_human_speech = time.time()
                    is_speech_detected = False
                    self.triggered = False
                    self.got_a_sentence = True
                    got_a_pause = False
                    msg = String()
                    msg.data = "end"
                    self.publisher_.publish(msg)
                    
                    # msg2 = Bool()
                    # msg2.data = True
                    # self.publisher_2.publish(msg2)

            self.stream.stop_stream()
            if self.got_a_sentence:
                time.sleep(1)
                thinking_reponse_audio_paths = [
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/thinking_audio_clips/output_audio_1.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/thinking_audio_clips/output_audio_2.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/thinking_audio_clips/output_audio_3.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/thinking_audio_clips/output_audio_4.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/thinking_audio_clips/output_audio_5.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/thinking_audio_clips/output_audio_6.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/thinking_audio_clips/output_audio_7.wav",
                        "",
                        "",
                        ""
                    ]

                self.thinking_reponse_audio_path = random.choice(thinking_reponse_audio_paths)
                # self.get_logger().info('Recording stopped.')
                if self.thinking_reponse_audio_path != "":
                    msg_filler_words_audio = String()
                    msg_filler_words_audio.data = self.thinking_reponse_audio_path
                    self.filler_words_pub.publish(msg_filler_words_audio)
                    
                # self.stream.close()
                # self.pa.terminate()
                # self.got_a_sentence = False
                # self.triggered = False
                # self.pre_speech_buffer.clear()
            # self.stream.close()
            # self.save_audio(raw_data)

        except Exception as e:
            self.get_logger().error(f'Error while recording: {e}')
            
    def active_usrs_callback(self, msg:PeopleArray):
        self.active_usrs = msg.data

    def publish_active_speaker(self, azimuth):
        min_dif = 100
        closest_usr = None      
        for usr in self.active_usrs:
            if abs(usr.hor_angle - azimuth) < min_dif:
                # name = usr.name
                # id = usr.id
                closest_usr = usr
                min_dif = abs(usr.hor_angle - azimuth)
                

        # if response.name == "":
        #     response.name = "no matching user"
        # msg = People()
        # msg.name = name
        # msg.id = id
        if closest_usr is not None:
            self.active_speaker_pub.publish(closest_usr)
            self.get_logger().info(f"user Name: {closest_usr.name} sent")
        else:
            self.get_logger().info(f"No matching user")
        return


    def save_audio(self, raw_data):
        # audio_save_path = self.get_parameter('audio_save_path').get_parameter_value().string_value
        base_path = '/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/'
        audio_save_path = f'{base_path}audio_{self.counter}.wav'
        raw_save_path = f'{base_path}audio.raw'
        # audio_save_path = f'/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/audio_{self.counter}.wav'
        try:
            with wave.open(audio_save_path, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.pa.get_sample_size(self.pa.get_format_from_width(self.width)))
                wav_file.setframerate(self.rate)
                wav_file.writeframes(raw_data.tobytes())

            self.get_logger().info(f'Saved audio to {audio_save_path}')

            # if self.start is not None:
            #     end = time.time()
            #     self.get_logger().info(f"Time taken to save the audio: {end - self.start:.5f}s")

            # Publish file path
            # if self.got_a_sentence:
            msg = String()
            msg.data = audio_save_path
            self.publisher_.publish(msg)

            self.counter += 1

        except Exception as e:
            self.get_logger().error(f'Error saving audio: {e}')

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