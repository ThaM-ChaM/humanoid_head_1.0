import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String, Bool
import numpy as np
import wave
import subprocess
import json
import time
import math
import os

from custom_interfaces.msg import People, PeopleArray

class SourceExtractorNode(Node):
    def __init__(self):
        super().__init__('source_extractor_node')

        self.subscription_doa = self.create_subscription(String, 'speech_pause', self.speech_pause_callback, 10)
        self.subscription_ch0_mic_audio = self.create_subscription(String, 'ch0_mic_audio_path', self.ch0_mic_audio_callback, 10)
        self.publisher_audio_path = self.create_publisher(String, 'audio_file_path', 10)
        self.active_users_sub = self.create_subscription(PeopleArray, "active_users", self.active_usrs_callback, 10)
        self.active_speaker_pub = self.create_publisher(People, "active_speaker",10)

        # Active users infront of the camera
        self.active_usrs = []

        # Constants
        self.sample_rate = 16000
        self.sample_width_bytes = 2
        self.n_sources = 4
        self.source_index = 0  # source index to extract [0 or 1 or 2 or 3]

        self.separated_path = '/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/separated.raw'
        self.postfiltered_path = '/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/postfiltered.raw'

        self.output_dir = "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.first_speaker_active = False
        self.first_speaker_azimuth = None
        self.first_speaker_position = None

        self.ch0_mic_audio_path = ''


        self.get_logger().info("Source Extractor Node Started")

    def ch0_mic_audio_callback(self, msg):
        self.ch0_mic_audio_path = msg.data

    def cartesian_to_azimuth(self, x, y):
        angle = math.atan2(y, x)
        degrees = math.degrees(angle)
        return round(degrees)

    def run_odas_on_raw(self):
        self.get_logger().info("Starting ODASLive sound tracker...")

        az = None

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
            self.single_source = True
            # self.previous_source_id = 0
            # start_time = time.time()
            # timeout = 2  # seconds

            while True:
                # if time.time() - start_time > timeout:
                #     process.terminate()
                #     break

                # time.sleep(0.0001)
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

                            # if timestamp < 216:
                            #     continue
                            # if timestamp > 225:
                            #     exit()
                            
                            valid_sources = 0  
                            max_activity = 0
                            chosen_source_index = None
                            chosen_source_id = None
                            
                            id_array = []
                            id_row = []
                            id_angles = []
                            
                            for i, src in enumerate(sources):
                                #  print("i ", i)
                                # print("src ", src)
                                if "id" in src and src["id"] != 0: # Exclude ID 0 sources
                                    # print(f"time stamp : {timestamp}")
                                    # print("src ", src)
                                    x, y = src["x"], src["y"]
                                    az = self.cartesian_to_azimuth(x, y)
                                    az =((az + 45) % 360)  - 180

                                    if not (-70 < az < 70):
                                        continue 
                                    valid_sources += 1

                                    id_array.append(src["id"])
                                    id_row.append(i)

                                    id_angles.append(az)
                                    activity = src.get("activity", 0)
                                    # print(f"Time: {timestamp}")
                                    self.get_logger().info(f"Source {valid_sources} ID: {src['id']}, Azimuth: {az}°, Activity: {activity}")
                                    
                                    if hasattr(self, 'first_speaker_active') and self.first_speaker_active:
                                        az_diff = abs(az - self.first_speaker_azimuth)
                                        if az_diff < 20:
                                            self.get_logger().info(f"Detected a previous source with ID {src['id']} at azimuth {az}° close to the first speaker's azimuth {self.first_speaker_azimuth}°")
                                            self.get_logger().info(f"Considering as the source with ID {src['id']} is the same source with previous ID {self.previous_source_id}")
                                            chosen_source_index = i
                                            chosen_source_id = src["id"]
                                            self.first_speaker_azimuth = az
                                            # break
                                        else:
                                            self.get_logger().info(f"Detected another source with id {src['id']} at azimuth {az} in the index(row) {i}")
                                            pass
                                           
                                    
                                    else:
                                        if activity > max_activity:
                                            max_activity = activity
                                            chosen_source_index = i
                                            chosen_source_id = src["id"]
                                            self.get_logger().info(f"Detected a new source with ID {src['id']} at azimuth {az}° with activity {activity}")
                                            
                                            self.first_speaker_azimuth = az
                                            self.first_speaker_position = (x, y)
                                            self.first_speaker_active = True
                                # print()
                            if len(id_array) > 1:
                                self.single_source = False  
                            # else:
                            #     self.single_source = False
                                            
                            if chosen_source_index is not None:
                                self.source_index = chosen_source_index
                                self.previous_source_id = chosen_source_id
                                self.get_logger().info(f"Tracking source with ID {chosen_source_id} in row {chosen_source_index} with azimuth {self.first_speaker_azimuth}°")
                            else:
                                # self.get_logger().info("No valid sources detected.")
                                pass
                            # print()
                                
                                
                            # if valid_sources == 1:
                            #     self.get_logger().info(f"Detected a single source with ID {id_array[0]} is spotted in row {id_row[0]} with azimuth {id_angles[0]}°")
                            #     self.get_logger().info(f"Giving priority to the source with ID {id_array[0]}")
                            #     self.source_index = id_row
                            #     self.previous_source_id = id_array[0]
                            # elif valid_sources > 1:
                            #     if self.previous_source_id in id_array:
                            #         index = id_array.index(self.previous_source_id)
                            #         self.source_index = id_row[index]
                            #         self.get_logger().info(f"Detected multiple sources with IDs {id_array} in rows {id_row} with azimuth {id_angles}°")
                            #         self.get_logger().info(f"Giving priority to the source with ID {self.previous_source_id} in row {self.source_index} with azimuth {id_angles[index]}°")
                            #     else:
                            #         self.get_logger().info(f"Giving priority to the source with ID {self.previous_source_id}")
                                
                            # print()
                            # if valid_sources == 0:
                            #     print("⚠️ No valid sources with non-zero IDs detected.")
                            
                    # If we didn't have a valid JSON, just continue accumulating
                except json.JSONDecodeError:
                    # Skip lines that are not JSON or can't be parsed
                    continue
                except Exception as e:
                    # Handle any other exceptions, e.g., in case of malformed data
                    print(f"Error processing line: {e}")
                    continue
        
        except Exception as e:
            self.get_logger().error(f'ODAS tracker error: {e}')
        finally:
            process.terminate()
        print(f"az : {az} and self.first_speaker {self.first_speaker_azimuth}")
        return self.first_speaker_azimuth

    def extract_sources_fast(self, raw_path, n_channels):
        if not os.path.exists(raw_path):
            self.get_logger().error(f"File not found: {raw_path}")
            return None

        with open(raw_path, 'rb') as f:
            raw_data = f.read()

        self.get_logger().info("Read the audio file")

        data = np.frombuffer(raw_data, dtype=np.int16)

        if len(data) % n_channels != 0:
            self.get_logger().warn("Incomplete frames in raw file")
            data = data[:len(data) - len(data) % n_channels]

        data = data.reshape(-1, n_channels)
        sources = data.T  # shape: (n_channels, n_frames)

        return sources

    def save_single_source_to_wav(self, source_data, output_wav_path):
        with wave.open(output_wav_path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(self.sample_width_bytes)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(source_data.tobytes())
        self.get_logger().info(f"Saved WAV: {output_wav_path}")

    def speech_pause_callback(self, msg):
        pause_detection = msg.data
        if pause_detection == "pause":
            self.get_logger().info(f" Detection of a pause in the speech is : {pause_detection}°")
            start_time = time.time()

            # for raw_file, label in [(self.separated_path, "separated"), (self.postfiltered_path, "postfiltered")]:
            #     sources = self.extract_sources_fast(raw_file, self.n_sources)
            #     if sources is None:
            #         self.get_logger().warn(f"Could not process {raw_file}")
            #         continue

            #     if not (0 <= self.source_index < self.n_sources):
            #         self.get_logger().error(f"Invalid source index: {self.source_index}")
            #         continue

            #     output_filename = f"{label}_source{self.source_index}.wav"
            #     output_path = os.path.join(self.output_dir, output_filename)
            #     self.save_single_source_to_wav(sources[self.source_index], output_path)

            #     msg = String()
            #     msg.data = output_path
            #     self.publisher_audio_path.publish(msg)
            #     self.get_logger().info(f"Published WAV Path: {output_path}")

            azimuth = self.run_odas_on_raw()

            if azimuth is not None:
                # self.get_logger().info(f'Detected Direction: {azimuth}°')
                # doa = ((azimuth + 315) % 360)  - 180
                self.get_logger().info(f"Motor direction: {azimuth}")
                self.publish_active_speaker(azimuth)

                # msg = Int32()
                # msg.data = doa
                # self.publisher_doa.publish(msg)
                # self.get_logger().info(f"doa: {doa}")
            else:
                self.get_logger().info('Direction not detected.')

            odas_time = time.time()
            # self.get_logger().info(f"time taken to run the ODAS and output direction {odas_time - start_time}")

            sources = self.extract_sources_fast(self.postfiltered_path , self.n_sources)
            if sources is None:
                self.get_logger().warn(f"Could not process {self.postfiltered_path}")

            if not (0 <= self.source_index < self.n_sources):
                self.get_logger().error(f"Invalid source index: {self.source_index}")

            if self.single_source == False:
                output_filename = f"separated_source{self.source_index}.wav"
                output_path = os.path.join(self.output_dir, output_filename)
                self.save_single_source_to_wav(sources[self.source_index], output_path)
            else:
                self.get_logger().info(f"detected only one speaker")
                output_path = self.ch0_mic_audio_path
            

            # self.get_logger().info(f" time taken to separate selected source and generate audio wav file {time.time() - odas_time}")

            msg = String()
            msg.data = output_path
            self.publisher_audio_path.publish(msg)
            self.get_logger().info(f"Published WAV Path: {output_path}")

            # self.get_logger().info(f"full time taken to run the speech separation node {time.time() - start_time}")
        
        elif pause_detection == "end":
            self.get_logger().info(f"End of the sentence is detected")
            msg = String()
            msg.data = 'end'
            self.publisher_audio_path.publish(msg)


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

def main(args=None):
    rclpy.init(args=args)
    node = SourceExtractorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
