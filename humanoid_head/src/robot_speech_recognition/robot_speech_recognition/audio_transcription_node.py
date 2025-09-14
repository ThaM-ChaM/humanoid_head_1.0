#!/home/kuweni/ssd/conda/envs/venv/bin/python3


import sys
sys.path.append('/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_to_Text/faster_whisper')


import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import torch
import random
from faster_whisper import WhisperModel
import time
from std_msgs.msg import Bool


class TranscriptionNode(Node):
    def __init__(self):
        super().__init__('transcription_node')
        self.subscription = self.create_subscription(String, 'audio_file_path', self.transcribe_audio_callback, 10)
        self.subscription_time = self.create_subscription(String, 'trans_time', self.trans_time_callback, 10)
        # self.subscription_2 = self.create_subscription(Bool, 'end_sentence', self.end_sentence_time_callback, 10)
        self.publisher_1 = self.create_publisher(String, 'transcribed_text', 10)
        self.publisher_2 = self.create_publisher(String, 'unclear_audio_path', 10)
        
        # Load Whisper model
        # model_path = "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_to_Text/tiny_model"
        # model_path = "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_to_Text/base_model"
        # model_path = "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_to_Text/small_model/"
        model_path = "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_to_Text/medium_model"
        # model_path = "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Speech_to_Text/large_v1_model"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = WhisperModel(model_path, device=device, compute_type="float16", num_workers=3)
        self.words_of_sentence = ''
        self.response_audio_path = '"/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/response_5.wav"'
        self.clear_sentence = True
        print("Transcription node initialized\n")

    def trans_time_callback(self, msg_trans):
        trans_time = msg_trans.data
        if trans_time =="start":
            self.start_trans_time = time.time()
            self.get_logger().info(f"Starting trans: {trans_time}")
        elif trans_time =="end": 
            self.get_logger().info(f"ending trans: {time.time() - self.start_trans_time}")
        # self.get_logger().info(f"time starting trans: {start_trans_time}")  

    def end_sentence_time_callback(self, msg2):
        self.msg2 = msg2.data
        if self.msg2:
            end_time = time.time()
            self.get_logger().info(f"ending trans: {self.trans_time-end_time}")
        self.get_logger().info(f"ending trans: {self.msg2}")

    def transcribe_audio_callback(self, msg):
        audio_file_path = msg.data
        if audio_file_path == 'e':
            if self.clear_sentence:
                self.get_logger().info(f"Received end of sentence")
                self.get_logger().info(f"sentence : {self.words_of_sentence}")
                if self.words_of_sentence != '':
                    # Publish the transcribed text
                    text_msg = String()
                    text_msg.data = self.words_of_sentence
                    self.publisher_1.publish(text_msg)
                self.clear_sentence = True
            else: 
                self.get_logger().info(f"Unclear audio. reponse is {self.response_audio_path}")
                repsonse_audio_msg = String()
                repsonse_audio_msg.data = self.response_audio_path
                self.publisher_2.publish(repsonse_audio_msg)
            self.clear_sentence = True  
            self.words_of_sentence = ''
        else:
            self.get_logger().info(f"Received audio file path: {audio_file_path}")
            start = time.time()
            
            segments_generator, info = self.model.transcribe(audio_file_path, beam_size=5, temperature=1, language=None)
            transcribed_text = " ".join([segment.text for segment in segments_generator])
            self.get_logger().info("Detected language '%s' with probability %f" % (info.language, info.language_probability))
            self.get_logger().info(f"Transcribed text: {transcribed_text}\n")
            if (info.language != "en" or info.language_probability < 0.3 or transcribed_text == ""):
                responses = [
                    "I'm sorry, I didn't quite understand that. Could you try again?",
                    "I’m having trouble understanding. Can you repeat that in English, please?",
                    "Oh, sorry I did not catch that. Can you say it one more time please?",
                    "Sorry, I didn’t hear you clearly. Can you repeat that?",
                    "Can you say that again? I didn’t quite get it",
                    "I'm sorry, could you rephrase that for me?"
                ]
                
                repsonse_audio_paths = [
                    "/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/response_1.wav",
                    "/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/response_2.wav",
                    "/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/response_3.wav",
                    "/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/response_4.wav",
                    "/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/response_5.wav",
                    "/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/audio/response_6.wav"
                ]
                transcribed_text = random.choice(responses)
                self.response_audio_path = random.choice(repsonse_audio_paths)

                self.get_logger().info(transcribed_text)
                current_time = time.time()

                self.get_logger().info(f"Time taken to generate response: {self.response_audio_path} is  {current_time - start:.5f}s")

                

                self.clear_sentence = False
                
            else:
                self.get_logger().info(f"Transcribed text: {transcribed_text}\n")
                self.words_of_sentence = self.words_of_sentence + transcribed_text

                current_time = time.time()

                self.get_logger().info(f"Time taken to generate transcription: {current_time - start:.5f}s")






def main(args=None):

    rclpy.init(args=args)
    transcription_node = TranscriptionNode()
    rclpy.spin(transcription_node)
    transcription_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()