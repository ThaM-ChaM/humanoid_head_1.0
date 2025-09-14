with open("/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/conda_packages.txt", "r") as f:
    lines = f.readlines()
print(lines)
with open("/home/kuweni/ssd/ros2_ws/src/robot_speech_recognition/robot_speech_recognition/requirements.txt", "w") as f_out:
    for line in lines:
        if not line.startswith("#") and '=' in line:
            print(f"Processing: {line.strip()}")  # <-- This will show what gets processed
            pkg = line.strip().split('=')[0]
            f_out.write(f"{pkg}\n")


