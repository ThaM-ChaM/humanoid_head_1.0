import pyaudio

# Initialize PyAudio
p = pyaudio.PyAudio()

# Print a success message
print("PyAudio installed successfully\n")

# Get the number of available audio devices
num_devices = p.get_device_count()

# Iterate over all the devices
for i in range(0, num_devices):
    # Get device info for the current device
    device_info = p.get_device_info_by_index(i)
    
    # Check if the device has input channels (i.e., it's a microphone)
    if device_info.get('maxInputChannels') > 0:
        print(f"Input Device id {i} - {device_info.get('name')}")

# PYTHONPATH=$PYTHONPATH:/home/kuweni/ssd/python_packages python3 dfu.py --download 6_channels_firmware.bin

# [INFO] [1747419818.577285261] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.166
# [INFO] [1747419818.578551592] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.579849765] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.581393684] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.003
# [INFO] [1747419818.582666800] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.583965805] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.585211943] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.003
# [INFO] [1747419818.586459105] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.587789344] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.589220999] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.590457568] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.591782847] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.593120288] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.006
# [INFO] [1747419818.594496515] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.595817090] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.597769614] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.599091629] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.600324134] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.601625123] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.0
# [INFO] [1747419818.602899231] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.604178427] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.605624451] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.606897950] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.608165529] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.609407955] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.001
# [INFO] [1747419818.610657741] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.611973419] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.613346702] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.083
# [INFO] [1747419818.614575622] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.615865411] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.617110141] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.004
# [INFO] [1747419818.618333973] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.619610704] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.621140638] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.622391640] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.623659732] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.624904109] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.171
# [INFO] [1747419818.626200874] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.627514953] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.628900845] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.630139046] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.631446660] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.632696381] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.321
# [INFO] [1747419818.633920853] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.635187377] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.636646554] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.637869777] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.639235924] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.640504495] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.162
# [INFO] [1747419818.641763017] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.643027044] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.644493710] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.645733383] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.647051238] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.648281694] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.017
# [INFO] [1747419818.649496822] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.650737935] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.652264125] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.653497909] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.654730734] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.656073358] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.001
# [INFO] [1747419818.657349514] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.658607237] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.660069806] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.661352810] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.662623269] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.663931780] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.076
# [INFO] [1747419818.665178493] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.666431031] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.667874015] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.669101495] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.670335184] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.671642766] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.008
# [INFO] [1747419818.672865030] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.674095966] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.675640654] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.676955724] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.678233096] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.679586377] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.29
# [INFO] [1747419818.680854308] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.682106975] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.683695921] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.684932106] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.686189092] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.687513987] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.002
# [INFO] [1747419818.688743132] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.689996726] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.691450974] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.692734523] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.693991189] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.695336886] [source_extractor_node]: Source 2 ID: 14, Azimuth: -31°, Activity: 0.001
# [INFO] [1747419818.696571919] [source_extractor_node]: Detected another source with id 14 at azimuth -31 in the index(row) 1
# [INFO] [1747419818.697831753] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.699539300] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.0
# [INFO] [1747419818.700799263] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.702036440] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.703354998] [source_extractor_node]: Source 2 ID: 14, Azimuth: -32°, Activity: 0.501
# [INFO] [1747419818.704635763] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.705893293] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.707455389] [source_extractor_node]: Source 1 ID: 13, Azimuth: 26°, Activity: 0.001
# [INFO] [1747419818.708748058] [source_extractor_node]: Detected a previous source with ID 13 at azimuth 26° close to the first speaker's azimuth 26°
# [INFO] [1747419818.710033079] [source_extractor_node]: Considering as the source with ID 13 is the same source with previous ID 13
# [INFO] [1747419818.711338741] [source_extractor_node]: Source 2 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.712579918] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.713851785] [source_extractor_node]: Tracking source with ID 13 in row 0 with azimuth 26°
# [INFO] [1747419818.715367830] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.716639986] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.718070361] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.719425882] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.720936583] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.722184672] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.723687469] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.724951975] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.726374542] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.006
# [INFO] [1747419818.727692653] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.729449643] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.006
# [INFO] [1747419818.730814605] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.732405695] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.302
# [INFO] [1747419818.733733183] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.735221802] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.736504742] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.737992113] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.739292591] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.740702356] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.005
# [INFO] [1747419818.741988753] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.743464251] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.744699859] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.746221025] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.007
# [INFO] [1747419818.747535199] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.749103408] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.002
# [INFO] [1747419818.750394573] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.751900857] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.148
# [INFO] [1747419818.753163060] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.754608380] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.755933083] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.757876551] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.004
# [INFO] [1747419818.759358898] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.761139186] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.613
# [INFO] [1747419818.762397932] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.764016705] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.765256122] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.766728548] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.768054979] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.769942667] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.017
# [INFO] [1747419818.771308109] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.772871869] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.144
# [INFO] [1747419818.774161658] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.775732555] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.049
# [INFO] [1747419818.777015975] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.778526644] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.001
# [INFO] [1747419818.779823537] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.781180115] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.341
# [INFO] [1747419818.782590648] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.784088260] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.163
# [INFO] [1747419818.785325277] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.786725410] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.788025759] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.789585199] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.645
# [INFO] [1747419818.790864555] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.792471231] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.0
# [INFO] [1747419818.793714040] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.795247526] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.006
# [INFO] [1747419818.796475071] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.797816415] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.009
# [INFO] [1747419818.799124893] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.800578310] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.017
# [INFO] [1747419818.801812510] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# [INFO] [1747419818.803444084] [source_extractor_node]: Source 1 ID: 14, Azimuth: -32°, Activity: 0.004
# [INFO] [1747419818.804687309] [source_extractor_node]: Detected another source with id 14 at azimuth -32 in the index(row) 1
# az : -32 and self.first_speaker 26
# [INFO] [1747419818.812007099] [source_extractor_node]: Motor direction: 26
# [INFO] [1747419818.813506087] [source_extractor_node]: No matching user
