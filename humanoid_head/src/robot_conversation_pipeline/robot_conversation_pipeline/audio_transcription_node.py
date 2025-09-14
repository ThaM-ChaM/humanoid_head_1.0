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
from rapidfuzz import process, fuzz
import sys
sys.path.append('/home/kuweni/ssd/python')

from langdetect import detect, detect_langs

# Add custom Python module path
# sys.path.append('/home/kuweni/ssd/python')
# from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

import csv
from datetime import datetime
import os

class AudioTranscriptionNode(Node):
    def __init__(self):
        super().__init__('audio_transcription_node')
        self.subscription = self.create_subscription(String, 'audio_file_path', self.transcribe_audio_callback, 10)
        # self.subscription = self.create_subscription(String, 'selected_source_audio_path', self.transcribe_audio_callback, 10)
        # self.subscription_time = self.create_subscription(String, 'full_process_time', self.trans_time_callback, 10)
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
        self.model = WhisperModel(model_path, device=device, compute_type="int8") #float_16 #num_workers = 3
        self.words_of_sentence = ''
        self.response_audio_path = '/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/response_for_unclear_queries/response_5.wav'
        self.clear_sentence = True
        # model_path = "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Text_classification/Name_entity_recognition"
        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # tokenizer = AutoTokenizer.from_pretrained(model_path)
        # model = AutoModelForTokenClassification.from_pretrained(model_path).to(self.device)
        # self.ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

        


        # List of known names to match against
        # self.names = ["Moshintha", "Charuka", "Tharusha", "Sahan", "Ravindu", "Isuru", "Nadeesha", "Tinal", "Ranga", "Thayaparan Subramaniam", "Kapila Jayasinghe", "Dileeka Dias", "Kithsiri Samarasinghe", "Ajith Pasquel", "Rohan Munasinghe", "Peshala Jayasekara", "Subodha Charles", "Ranga Rodrigo", "Kasun Hemachandra", "Samiru Gayan", "Sampath Perera", "Upekha Premaratne", "Tharaka Samarasinghe", "Rukshani Liyanaarachchi", "Chamira Edissooriya", "Mevan Gunawardena", "Dinithi Fernando", "Thilanka Udara", "Sadeep Jayasumana", "Wageesha Manamperi", "Pranjeevan Kulasingham"]  

        self.get_logger().info(f"Transcription node initialized\n")

    # def trans_time_callback(self, msg_trans):
    #     trans_time = msg_trans.data
    #     if trans_time =="start":
    #         self.start_trans_time = time.time()
    #         self.get_logger().info(f"Starting trans: {trans_time}")
    #     elif trans_time =="end": 
    #         self.get_logger().info(f"ending trans: {time.time() - self.start_trans_time}")
        # self.get_logger().info(f"time starting trans: {start_trans_time}")  

    # def end_sentence_time_callback(self, msg2):
    #     self.msg2 = msg2.data
    #     if self.msg2:
    #         end_time = time.time()
    #         self.get_logger().info(f"ending trans: {self.trans_time-end_time}")
    #     self.get_logger().info(f"ending trans: {self.msg2}")
    # def named_entity_recognition(self, name):
    #     results = self.ner_pipeline(name)
        
    #     print(f"NER results: {results}")
    #     merged_entities = []
    #     current_entity = None

    #     for token in results:
    #         word = token["word"]
    #         entity = token["entity"]
    #         score = token["score"]

    #         if word.startswith("##"):
    #             if current_entity and "PER" in current_entity["entity"] and "PER" in entity:
    #                 current_entity["word"] += word[2:]
    #                 current_entity["score"] = max(current_entity["score"], score)
    #         else:
    #             if current_entity:
    #                 merged_entities.append(current_entity)
    #             current_entity = {"entity": entity, "word": word, "score": score}

    #     if current_entity:
    #         merged_entities.append(current_entity)
            
    #     # Print merged result
    #     for ent in merged_entities:
    #         print(f"{ent['entity']}: {ent['word']} (score: {ent['score']:.2f})")

    #     person_names = [ent["word"] for ent in merged_entities if "PER" in ent["entity"]]
    #     return " ".join(person_names) if person_names else "not_a_name"

    # def fix_names(self, text):
    #     out = []
    #     for word in text.split():
    #         match, score, _ = process.extractOne(word, self.names, scorer=fuzz.WRatio)
    #         self.get_logger().info(f"word: {word} match: {match} score: {score}")
    #         if score > 80:
    #             name = self.named_entity_recognition(match)
    #             if name == "not_a_name":
    #                 out.append(word)
    #             else:
    #                 out.append(match)
    #         else:
    #             out.append(word)
    #     return " ".join(out)




    def log_transcription(self, audio_path, transcribed_text, save_path):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'a', newline='') as f:
            writer = csv.writer(f)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, audio_path, transcribed_text])


    def transcribe_audio_callback(self, msg):
        audio_file_path = msg.data
        self.get_logger().info(f"Received path {audio_file_path}")
        if audio_file_path == 'end':
            if self.clear_sentence:
                self.get_logger().info(f"Received end of sentence")
                self.get_logger().info(f"sentence : {self.words_of_sentence}")
                if self.words_of_sentence != '':
                    # Publish the transcribed text
                    text_msg = String()
                    text_msg.data = self.words_of_sentence
                    self.publisher_1.publish(text_msg)
                else:
                    self.get_logger().info(f"Unclear audio. reponse is {self.response_audio_path}")
                    repsonse_audio_msg = String()
                    repsonse_audio_msg.data = self.response_audio_path
                    self.publisher_2.publish(repsonse_audio_msg)
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
            log_path = "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/testing_results/word_error_rate_testing/stt_logs.csv" ###############
            self.log_transcription(audio_file_path, transcribed_text, log_path) ###########################
            if (((info.language != "en") or info.language_probability < 0.2) or transcribed_text == ""):
                # if transcribed_text != "":
                #     print(f"detected language {detect(transcribed_text)} and score {detect_langs(transcribed_text)[0].prob}")
                if (transcribed_text == "") or (detect(transcribed_text) != 'en') or ((detect(transcribed_text) == 'en') and (detect_langs(transcribed_text)[0].prob)) < 0.5:
                    
                    responses = [
                        "I'm sorry, I didn't quite understand that. Could you try again?",
                        "I’m having trouble understanding. Can you repeat that in English, please?",
                        "Oh, sorry I did not catch that. Can you say it one more time please?",
                        "Sorry, I didn’t hear you clearly. Can you repeat that?",
                        "Can you say that again? I didn’t quite get it",
                        "I'm sorry, could you rephrase that for me?"
                    ]
                    
                    repsonse_audio_paths = [
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/response_for_unclear_queries/response_1.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/response_for_unclear_queries/response_2.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/response_for_unclear_queries/response_3.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/response_for_unclear_queries/response_4.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/response_for_unclear_queries/response_5.wav",
                        "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/response_for_unclear_queries/response_6.wav"
                    ]
                    # transcribed_text = random.choice(responses)
                    self.response_audio_path = random.choice(repsonse_audio_paths)

                    self.get_logger().info(transcribed_text)
                    current_time = time.time()

                    # self.get_logger().info(f"Time taken to generate response: {self.response_audio_path} is  {current_time - start:.5f}s")

                    

                    self.clear_sentence = False
                else:
                    self.words_of_sentence = self.words_of_sentence + transcribed_text
                    current_time = time.time()
            else:
                # corrected_text = self.fix_names(transcribed_text)
                # self.get_logger().info(f"Corrected transcribed text: {corrected_text}\n")
                self.words_of_sentence = self.words_of_sentence + transcribed_text

                current_time = time.time()

                # self.get_logger().info(f"Time taken to generate transcription: {current_time - start:.5f}s")






def main(args=None):

    rclpy.init(args=args)
    audio_transcription_node = AudioTranscriptionNode()
    rclpy.spin(audio_transcription_node)
    audio_transcription_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()