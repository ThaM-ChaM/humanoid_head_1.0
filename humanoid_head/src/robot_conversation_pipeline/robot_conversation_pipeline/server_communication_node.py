#!/home/kuweni/ssd/conda/envs/venv/bin/python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int16
import paramiko
import time
import re
import shlex
import torch
from custom_interfaces.msg import People
import sys
# Add custom Python module path
sys.path.append('/home/kuweni/ssd/python')

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# from custom_interfaces.srv import GivePeopleName

class ServerCommunicationNode(Node):
    def __init__(self):
        super().__init__('server_communication_node')
        self.subscription = self.create_subscription(String, 'transcribed_text', self.send_to_server_callback, 10)
        # self.active_user_subscription = self.subscription(People, 'active_speaker' , self.active_speaker_callback, 10)
        # self.subscription_doa = self.create_subscription(Int16, 'user_doa', self.user_doa_callback, 10)
        self.new_usr_publisher = self.create_publisher(People, 'new_user', 10)
        self.active_speaker_sub = self.create_subscription(People,"active_speaker",self.active_speaker_callback,10)
        # self.id_client = self.create_client(GivePeopleName, "user_id")

        self.user_name = ''
        self.speaker_id = -1
        # self.single_user_doa = 0
        # self.doa = 0
        
        # Server details
        self.server_ip = '192.248.10.69'
        self.username = 'fyp3-2'
        self.password = 'cvpr*2022*BSMM'
        
        
        model_path = "/home/kuweni/ssd/Python_Scripts/Natural_Conversation_System/Text_classification/Name_entity_recognition"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForTokenClassification.from_pretrained(model_path).to(self.device)
        self.ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

        
        
        self.get_logger().info(f"Server Communication Node initialized\n")

    # def id_server_callback(self, request: People.Request, response: People.Response):
    #     self.user_name = request.id
    #     print(f"incoming identity {self.user_name}")
    #     if self.user_name == "Unknown":
    #         response.name = "Isuru"
    #     else:
    #         response.name = self.user_name
    #     print(f"sending identity {response.name}")
    #     return response

    # def user_doa_callback(self, msg):
    #     self.single_user_doa = msg.data
    #     print(f"Recived direction of arrival for single user {self.single_user_doa}")

    def active_speaker_callback(self, msg):
        self.speaker_id = msg.id
        self.user_name = msg.name
        
    def named_entity_recognition(self, name):
        results = self.ner_pipeline(name)
        
        print(f"NER results: {results}")
        merged_entities = []
        current_entity = None

        for token in results:
            word = token["word"]
            entity = token["entity"]
            score = token["score"]

            if word.startswith("##"):
                if current_entity and "PER" in current_entity["entity"] and "PER" in entity:
                    current_entity["word"] += word[2:]
                    current_entity["score"] = max(current_entity["score"], score)
            else:
                if current_entity:
                    merged_entities.append(current_entity)
                current_entity = {"entity": entity, "word": word, "score": score}

        if current_entity:
            merged_entities.append(current_entity)
            
        # Print merged result
        # for ent in merged_entities:
        #     print(f"{ent['entity']}: {ent['word']} (score: {ent['score']:.2f})")

        person_names = [ent["word"] for ent in merged_entities if "PER" in ent["entity"]]
        return " ".join(person_names) if person_names else "Unknown"

    def extract_name(self, query):
        pattern = r"(?:my name is|i am|it's|call me|Hello, my name is|Hi i'm|Hi i am|you can call me|the name'?s|i'm) (\w+)"
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            match_name = match.group(1).capitalize()
            # match_name = query #### changed 
            self.get_logger().info(f"Extracted before name: {match_name}")
            # name = match_name
            name = self.named_entity_recognition(match_name)
            self.get_logger().info(f"Extracted name: {name}")
            if name != "Unknown":
                name = match_name
            self.get_logger().warn(f"Extracted after name: {name}")
            return name
        else:
            return "Unknown"
    
    # def active_speaker_callback(self, msg):
    #     self.user_name = msg.name

    # def set_user_id(self, future):
    #     response = future.result()
    #     self.user_name = response.name
    #     self.get_logger().info(f"received user name from face rec {response.name}")

    def send_to_server_callback(self, msg):
        # print(f"Current single user doa received {self.single_user_doa}")
        # self.doa = msg.doa
        text = msg.data
        # self.doa = self.single_user_doa
        # text = msg.data
        # request = GivePeopleName.Request()
        # request.doa = self.doa
                
        # future = self.id_client.call_async(request)
        # self.get_logger().info("Request send to face recong")
        # future.add_done_callback(self.set_user_id)

        # count = 0
        # # Wait for the future to complete
        # while not future.done():
        #     # rclpy.spin_once(self)
        #     count += 1
        #     if count > 100:
        #         self.get_logger().info("user id server is not responding")
        #         # future.cancel()
        #         break
        #     time.sleep(0.01)


        # self.user_name = "Isuru"
        # sending_text = self.user_name + " : " + text
        # if self.user_name =
        # print(text)
        detected_name = self.extract_name(text)

        if detected_name != "Unknown":
            sending_text = detected_name + " : " + text
            msg = People()
            msg.id = self.speaker_id
            msg.name = detected_name
            self.new_usr_publisher.publish(msg)
            self.user_name = detected_name
            self.get_logger().warn(f"{msg.name} is sent as new user")
        else:
            sending_text = self.user_name + " : " + text
        # print(f"user identity {self.user_name}")
        self.get_logger().info(f"Sending full text - {sending_text}\n")
        
        start = time.time()

        # Send text to server
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(self.server_ip, username=self.username, password=self.password)

            escaped_text = shlex.quote(sending_text)
            command = f"echo {escaped_text} | python3 /home/fyp3-2/Desktop/Batch20/moshintha_ws/full_pipeline/version_2/user_query_save.py"

            # command = f"echo '{sending_text}' | python3 /home/fyp3-2/Desktop/Batch20/moshintha_ws/full_pipeline/version_2/user_query_save.py"
            stdin, stdout, stderr = ssh.exec_command(command)

            response = stdout.read().decode()
            errors = stderr.read().decode()

            if response:
                self.get_logger().info(f"Server Response: {response}\n")
            if errors:
                self.get_logger().error(f"Errors: {errors}\n")

            end = time.time()

            self.get_logger().info(f"Time taken to send the query to the server: {end - start:.5f}s")

        finally:
            ssh.close()


def main(args=None):
    rclpy.init(args=args)
    server_communication_node = ServerCommunicationNode()
    rclpy.spin(server_communication_node)
    server_communication_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()