import numpy as np
import wave
import os

def extract_sources_fast(raw_path, n_channels=4, sample_rate=16000, sample_width_bytes=2):
    if not os.path.exists(raw_path):
        print(f"File not found: {raw_path}")
        return None

    with open(raw_path, 'rb') as f:
        raw_data = f.read()

    data = np.frombuffer(raw_data, dtype=np.int16)

    if len(data) % n_channels != 0:
        print(f" Warning: Incomplete frames in {raw_path}")

    data = data[:len(data) - len(data) % n_channels]
    data = data.reshape(-1, n_channels)

    sources = data.T  # Transpose to (n_channels, num_frames)
    return sources

def save_single_source_to_wav(source_data, output_wav_path, sample_rate=16000, sample_width_bytes=2):
    with wave.open(output_wav_path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(sample_width_bytes)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(source_data.tobytes())
    print(f"Saved: {output_wav_path}")

# ---- USAGE ----
n_sources = 4
sample_rate = 16000
sample_width = 2

sources = extract_sources_fast("/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/separated.raw", n_channels=n_sources, sample_rate=sample_rate, sample_width_bytes=sample_width)

if sources is not None:
    # Example: Save Source 0 (first one)
    source_index = 0 # change 0 to 1, 2, 3 for other sources
    save_single_source_to_wav(
        sources[source_index],
        output_wav_path=f"/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/separated_{source_index}.wav",
        sample_rate=sample_rate,
        sample_width_bytes=sample_width
    )

# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import Int32, String
# import numpy as np
# import wave
# import os

# class SourceExtractorNode(Node):
#     def __init__(self):
#         super().__init__('source_extractor_node')

#         self.subscription_doa = self.create_subscription(Int32, 'doa', self.doa_callback, 10)

#         self.publisher_audio_path = self.create_publisher(String, 'selected_source_audio_path', 10)

#         # Constants
#         self.sample_rate = 16000
#         self.sample_width_bytes = 2
#         self.n_sources = 4
#         self.source_index = 0  # source index to extract [0 or 1 or 2 or 3]

#         self.separated_path = '/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/separated.raw'
#         self.postfiltered_path = '/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/postfiltered.raw'

#         self.output_dir = os.path.join(os.getcwd(), "audio")
#         os.makedirs(self.output_dir, exist_ok=True)

#         self.get_logger().info("Source Extractor Node Started")

#     def doa_callback(self, msg):
#         doa_angle = msg.data
#         self.get_logger().info(f"DOA angle received: {doa_angle}°")

#         # for raw_file, label in [(self.separated_path, "separated"), (self.postfiltered_path, "postfiltered")]:
#         #     sources = self.extract_sources_fast(raw_file, self.n_sources)
#         #     if sources is None:
#         #         self.get_logger().warn(f"Could not process {raw_file}")
#         #         continue

#         #     if not (0 <= self.source_index < self.n_sources):
#         #         self.get_logger().error(f"Invalid source index: {self.source_index}")
#         #         continue

#         #     output_filename = f"{label}_source{self.source_index}.wav"
#         #     output_path = os.path.join(self.output_dir, output_filename)
#         #     self.save_single_source_to_wav(sources[self.source_index], output_path)

#         #     msg = String()
#         #     msg.data = output_path
#         #     self.publisher_audio_path.publish(msg)
#         #     self.get_logger().info(f"Published WAV Path: {output_path}")


#         sources = self.extract_sources_fast(self.separated_path , self.n_sources)
#         if sources is None:
#             self.get_logger().warn(f"Could not process {self.separated_path}")

#         if not (0 <= self.source_index < self.n_sources):
#             self.get_logger().error(f"Invalid source index: {self.source_index}")

#         output_filename = f"separated_source{self.source_index}.wav"
#         output_path = os.path.join(self.output_dir, output_filename)
#         self.save_single_source_to_wav(sources[self.source_index], output_path)

#         msg = String()
#         msg.data = output_path
#         self.publisher_audio_path.publish(msg)
#         self.get_logger().info(f"Published WAV Path: {output_path}")

#     def extract_sources_fast(self, raw_path, n_channels):
#         if not os.path.exists(raw_path):
#             self.get_logger().error(f"File not found: {raw_path}")
#             return None

#         with open(raw_path, 'rb') as f:
#             raw_data = f.read()

#         data = np.frombuffer(raw_data, dtype=np.int16)

#         if len(data) % n_channels != 0:
#             self.get_logger().warn("Incomplete frames in raw file")
#             data = data[:len(data) - len(data) % n_channels]

#         data = data.reshape(-1, n_channels)
#         sources = data.T  # shape: (n_channels, n_frames)

#         return sources

#     def save_single_source_to_wav(self, source_data, output_wav_path):
#         with wave.open(output_wav_path, 'w') as wav_file:
#             wav_file.setnchannels(1)
#             wav_file.setsampwidth(self.sample_width_bytes)
#             wav_file.setframerate(self.sample_rate)
#             wav_file.writeframes(source_data.tobytes())
#         self.get_logger().info(f"Saved WAV: {output_wav_path}")


# def main(args=None):
#     rclpy.init(args=args)
#     node = SourceExtractorNode()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()

