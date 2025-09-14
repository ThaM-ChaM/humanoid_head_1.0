# with open("/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/conda_packages.txt", "r") as f:
#     lines = f.readlines()
# print(lines)
# with open("/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/requirements.txt", "w") as f_out:
#     for line in lines:
#         if not line.startswith("#") and '=' in line:
#             print(f"Processing: {line.strip()}")  # <-- This will show what gets processed
#             pkg = line.strip().split('=')[0]
#             f_out.write(f"{pkg}\n")


# pip install --target=/home/kuweni/ssd/python_packages <pakage_name>

# import math

# def cartesian_to_azimuth(x, y):
#     angle = math.atan2(y, x)
#     degrees = math.degrees(angle)
#     return round(degrees)

# print(cartesian_to_azimuth(0.786,-0.616))
# print(cartesian_to_azimuth(0.785, -0.616))
# print(cartesian_to_azimuth(0.5, 0.162))
# print(cartesian_to_azimuth(-0.626, 0.197))
import sys
sys.path.append('/home/kuweni/ssd/python')

from langdetect import detect, detect_langs

text = "do you know Dr. Peshalai"
lang = detect(text)
langs = detect_langs(text)

print(f"Language: {lang}")
print(f"Probabilities: {langs[0].prob:.2f}")

# arecord -l    check the sound card of the mic array it should be on card 2 or 3 to be detected by pyaudio. conect the mic some time after the jetson is on.

# kuweni@ubuntu:~/ssd/ros2_ws$ arecord -D plughw:2,0 -f cd test.wav
# arecord: main:852: audio open error: Device or resource busy
# kuweni@ubuntu:~/ssd/ros2_ws$ fuser -v /dev/snd/*
#                      USER        PID ACCESS COMMAND
# /dev/snd/controlC0:  kuweni     2737 F.... pulseaudio
# /dev/snd/controlC1:  kuweni     2737 F.... pulseaudio
# /dev/snd/controlC2:  kuweni     2737 F.... pulseaudio
# /dev/snd/pcmC2D0c:   kuweni     2737 F...m pulseaudio
# kuweni@ubuntu:~/ssd/ros2_ws$ ps -p <PID> -o comm=
# bash: PID: No such file or directory
# kuweni@ubuntu:~/ssd/ros2_ws$ pulseaudio --kill
# kuweni@ubuntu:~/ssd/ros2_ws$ fuser -v /dev/snd/*
#                      USER        PID ACCESS COMMAND
# /dev/snd/controlC0:  kuweni     9147 F.... pulseaudio
# /dev/snd/controlC1:  kuweni     9147 F.... pulseaudio
# /dev/snd/controlC2:  kuweni     9147 F.... pulseaudio
# /dev/snd/pcmC0D8p:   kuweni     9147 F...m pulseaudio
# /dev/snd/pcmC1D0c:   kuweni     9147 F...m pulseaudio
# /dev/snd/pcmC1D0p:   kuweni     9147 F...m pulseaudio
# /dev/snd/pcmC2D0c:   kuweni     9147 F...m pulseaudio
# /dev/snd/pcmC2D0p:   kuweni     9147 F...m pulseaudio
# kuweni@ubuntu:~/ssd/ros2_ws$ arecord -D plughw:2,0 -f cd test.wav
# arecord: main:852: audio open error: Device or resource busy
# kuweni@ubuntu:~/ssd/ros2_ws$ pasuspender -- arecord -D plughw:2,0 -f cd test.wav
# Recording WAVE 'test.wav' : Signed 16 bit Little Endian, Rate 44100 Hz, Stereo
# ^CAborted by signal Interrupt...
# arecord: pcm_read:2178: Got SIGINT, exiting.
# read error: Interrupted system call
# Failure to resume: Invalid argument
# kuweni@ubuntu:~/ssd/ros2_ws$ echo "autospawn = no" > ~/.config/pulse/client.conf
# kuweni@ubuntu:~/ssd/ros2_ws$ pulseaudio --kill
# kuweni@ubuntu:~/ssd/ros2_ws$ fuser -v /dev/snd/*
#                      USER        PID ACCESS COMMAND
# /dev/snd/controlC0:  kuweni     9259 F.... pulseaudio
# /dev/snd/controlC1:  kuweni     9259 F.... pulseaudio
# /dev/snd/controlC2:  kuweni     9259 F.... pulseaudio
# kuweni@ubuntu:~/ssd/ros2_ws$ fuser -v /dev/snd/*
#                      USER        PID ACCESS COMMAND
# /dev/snd/controlC0:  kuweni     9259 F.... pulseaudio
# /dev/snd/controlC1:  kuweni     9259 F.... pulseaudio
# /dev/snd/controlC2:  kuweni     9259 F.... pulseaudio
