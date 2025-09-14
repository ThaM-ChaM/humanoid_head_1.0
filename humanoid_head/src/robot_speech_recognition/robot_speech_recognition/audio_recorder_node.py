#!/home/kuweni/ssd/conda/envs/venv/bin/python3

import sys
sys.path.append('/home/kuweni/ssd')

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from array import array
from collections import deque
import pyaudio
import usb.core
from Python_Scripts.Natural_Conversation_System.Speech_to_Text.Respeaker_mic_array.usb_4_mic_array.tuning import Tuning
import wave
import time



class RespeakerAudioRecorder(Node):
    def __init__(self):
        super().__init__('respeaker_audio_recorder_node')
        self.publisher_ = self.create_publisher(String, 'audio_file_path', 10)
        self.publisher_time = self.create_publisher(String, 'trans_time', 10)
        self.publisher_response_generation = self.create_publisher(Bool, 'response_genration_flag', 10)
        # self.publisher_2 = self.create_publisher(Bool, 'end_sentence', 10)
        # self.subscription_mouth_flag = self.create_subscription(Bool, 'mouth_flag', self.mouth_flag_callback, 10)
        self.subscription_end_audio_response = self.create_subscription(Bool, 'end_audio_response', self.end_audio_response_callback, 10)
        # self.sub2 = self.create_subscription(String,"example", self.callback, 10)

        self.mouth_flag = False  
        self.counter = 1
        self.got_a_sentence = False
        # self.audio_save_path = f'/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/audio_{self.counter}.wav'

        # Parameters
        # self.declare_parameter('audio_save_path', f'/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/audio_{self.counter}.wav')
        self.declare_parameter('device_index', 24)
        self.declare_parameter('chunk_duration_ms', 30)

        # Initialize audio settings
        self.rate = 16000
        self.channels = 1
        self.width = 2
        self.chunk_duration_ms = self.get_parameter('chunk_duration_ms').get_parameter_value().integer_value
        self.chunk_size = int(self.rate * self.chunk_duration_ms / 1000) * self.channels
        self.device_index = self.get_parameter('device_index').get_parameter_value().integer_value

        # Other configurations
        # self.ring_buffer = deque(maxlen=int(750 / self.chunk_duration_ms))
        self.triggered = False


        # USB Device
        self.dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
        if not self.dev:
            self.get_logger().error('ReSpeaker USB device not found! Exiting.')
            return

        self.tuning = Tuning(self.dev)
        self.tuning.set_vad_threshold(8)
        self.true_threshold = 2
        self.sentence_pause_threshold = 25
        self.false_threshold = 40

        # PyAudio Stream
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
        true_cnt = 0
        false_cnt = 0
        pause_cnt = 0

        try:
            while not self.got_a_sentence:
                chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
                raw_data.extend(array('h', chunk))
                # msg2 = Bool()
                # msg2.data = False
                # self.publisher_2.publish(msg2)
                if (self.tuning.is_voice() and self.tuning.is_speech()):
                    true_cnt += 1
                    false_cnt = 0
                    # pause_cnt = 0
                else:
                    true_cnt = 0
                    false_cnt += 1
                    # pause_cnt += 1

                if not self.triggered:
                    if true_cnt > self.true_threshold:
                        self.get_logger().info('Detected human voice! Starting recording...')
                        self.sentence_start_time = time.time()
                        self.triggered = True
                        raw_data = array('h', chunk)
                        msg_trns = String()
                        msg_trns.data = "start"
                        self.publisher_time.publish(msg_trns)
                        

                elif false_cnt == self.sentence_pause_threshold:
                    self.get_logger().info("Detected a pause in the speech.")
                    pause_cnt = 0
                    self.got_a_sentence = False
                    got_a_pause = True
                    self.get_logger().info(f"time taken {time.time()-self.sentence_start_time}")
                    if (time.time()-self.sentence_start_time) >= 1:
                        self.get_logger().info("Sending the current record to stt model")
                        self.save_audio(raw_data)
                        self.sentence_start_time = time.time()
                        raw_data = array('h', chunk)

                    
                elif false_cnt > self.false_threshold:
                    self.get_logger().info('Detected end of human voice.')
                    self.start = time.time()
                    self.triggered = False
                    self.got_a_sentence = True
                    got_a_pause = False
                    msg = String()
                    msg.data = "e"
                    self.publisher_.publish(msg)
                    # msg2 = Bool()
                    # msg2.data = True
                    # self.publisher_2.publish(msg2)

                    

            self.stream.stop_stream()
            # self.save_audio(raw_data)

        except Exception as e:
            self.get_logger().error(f'Error while recording: {e}')


    def save_audio(self, raw_data):
        # audio_save_path = self.get_parameter('audio_save_path').get_parameter_value().string_value
        base_path = '/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/'
        audio_save_path = f'{base_path}audio_{self.counter}.wav'
        raw_save_path = f'{base_path}audio.raw'
        # audio_save_path = f'/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/audio_{self.counter}.wav'
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