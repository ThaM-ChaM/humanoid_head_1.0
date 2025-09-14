import subprocess
import json
import math
import time
# Function to convert Cartesian coordinates (x, y) to azimuth angle (degrees)
def cartesian_to_azimuth(x, y):
    angle = math.atan2(y, x)
    degrees = math.degrees(angle)
    return round(degrees)

# Function to process ODAS live feed and print sound sources with azimuth and energy
def run_odas_tracker():
    print("Starting ODASLive sound tracker...")

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

        while True:
            #sleep 0.5 seconds
            time.sleep(0.0001)
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

                        # if 500 > timestamp > 450:
                        #     print(data)
                        #     print()
                        

                        # Iterate over the sound sources and calculate azimuth for sources with non-zero ID
                        valid_sources = 0  # Counter for valid sources
                        # if 1000 > timestamp > 0:
                            # print(data)
                        for i, src in enumerate(sources):
                            #  print("i ", i)
                            #  print("src ", src)
                            if "id" in src and src["id"] != 0: # Exclude ID 0 sources
                                valid_sources += 1
                                # print("i ", i)
                                # print(data)
                                # print("src ", src)
                                x, y = src["x"], src["y"]
                                print(f"x : {x} and y : {y}")
                                az = cartesian_to_azimuth(x, y)
                                az =((az + 315) % 360)  - 180
                                # # print(f"\n🎯 Time: {timestamp}")
                                print(f"Source {valid_sources}: Azimuth = {az}°")
                                print()
                                
                        # if valid_sources>=2:
                            # exit()
                        # if timestamp > 300:
                        #     exit()
                        # print()
                        # if valid_sources == 0:
                        #     print("⚠️ No valid sources with non-zero IDs detected.")
                        
                # If we didn't have a valid JSON, just continue accumulating
            except json.JSONDecodeError:
                # Skip lines that are not JSON or can't be parsed
                continue
            except Exception as e:
                # Handle any other exceptions, e.g., in case of malformed data
                print(f"⚠️ Error processing line: {e}")
                continue

    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        print("\nStopping ODASLive...")
        process.terminate()
        process.wait()
        print("ODASLive stopped.")

# Main entry point for the script
if __name__ == "__main__":
    run_odas_tracker()