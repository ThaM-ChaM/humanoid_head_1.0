from jiwer import wer

# Reference text
reference = """Hello how are you? Welcome to the department of electronics and telecommunication engineering of university of Moratuwa. We are a final year undergraduate team building a humanoid head for a robot receptionist, capable of natural human interaction. Our Robot is able to Interact with the visitors using facial expressions and conversation abilities. It also has a human re-identification system to identify whether that person has previously Interacted with the robot."""

# Clean reference text (flatten and lowercase)
reference = reference.replace('\n', ' ').lower().strip()

# STT outputs from the 4 participants (replace these with actual outputs)
stt_outputs = [
    "Hello, how are you? Welcome to the Department of Electronics and Telecommunication Engineering of University  of monitor. We are finally an undergraduate team built in a humanoid head for a robot receptionist  capable of natural human interaction. Our robot is able to interact with the visitors using facial expressions and conversational  abilities. It also has a human re-identification system to identify whether that person has previously  interacted with the robot.",
    "Hello, how are you? Welcome to the Department of Electronics and Telecommunication Engineering of University  of Moratoga. We are a final year undergraduate team building a humanoid head for a robot receptionist capable  of natural human interaction. Our robot is able to interact with the visitors using facial expressions and conversational  abilities. It also has a human re-identification system to identify whether the person has previously  interacted with the robot.",
    "Hello, how are you? Welcome to the Department of Electronic and Telecommunication Engineering  of the University of Moscow. We are finally undergraduate team budding a humanoid head for robot receptionist capable of natural human interaction. Our robot is able to interact with visitors using facial expressions and conversation  abilities. It also has a human re-identification system to identify whether that person has previously  interacted with the robot.",
    ] #    "Hello, How Are You? Welcome to the Department of Electronic Technology and Antennas Communication Engineering of  University of Mural. Kami agar for robot receptionist capable of natural human interaction. Our robot is able to interact with visitors using facial expressions and conversational  abilities. It also has a human re-identification system to identify whether that person has previously  interacted with the robot."
#]

# Calculate and print WER for each speaker
wer_scores = []
for i, hypothesis in enumerate(stt_outputs, 1):
    error = wer(reference, hypothesis.lower().strip())
    wer_scores.append(error)
    print(f"Speaker {i}: WER = {error:.2%}")

# Calculate and print average WER
average = sum(wer_scores) / len(wer_scores)
print(f"\nAverage WER: {average:.2%}")
