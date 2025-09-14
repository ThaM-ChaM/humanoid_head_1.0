import numpy as np

# Load the original .npz file
data = np.load("ros2_ws/src/face_recognition_pkg/face_recognition_pkg/datasets/face_features/feature.npz", allow_pickle=True)
names = data['images_name.npy']
embs = data['images_emb.npy']

# Convert to list for filtering
names = names.tolist()
embs = embs.tolist()

# Filter out 'person_1'
filtered = [(name, emb) for name, emb in zip(names, embs) if name != 'person_1']
filtered_names = [n for n, _ in filtered]
filtered_embs = [e for _, e in filtered]

# Convert back to numpy arrays
filtered_names = np.array(filtered_names)
filtered_embs = np.array(filtered_embs)

# Overwrite the original file
np.savez("ros2_ws/src/face_recognition_pkg/face_recognition_pkg/datasets/face_features/feature.npz", images_name=filtered_names, images_emb=filtered_embs)
