import numpy as np

class Track:
    def __init__(self, tlwh, track_id):
        self.tlwh = tlwh  # format: top-left x, y, width, height
        self.track_id = track_id
        self.lost_frames = 0

class IoUTracker:
    def __init__(self, iou_threshold=0.4, max_lost=30):
        self.iou_threshold = iou_threshold
        self.max_lost = max_lost
        self.tracks = {}
        self.next_id = 1

    def update(self, detections):
        updated_tracks = {}

        det_boxes = [det[:4] for det in detections]  # detections: [x1, y1, x2, y2, conf]

        # Mark all existing tracks as lost
        for track_id, track in self.tracks.items():
            track.lost_frames += 1

        # Match detections to existing tracks by IoU
        for det in det_boxes:
            best_iou = 0
            best_track_id = None
            for track_id, track in self.tracks.items():
                iou = self.compute_iou(det, track.tlwh)
                if iou > best_iou and iou >= self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id

            if best_track_id is not None:
                self.tracks[best_track_id].tlwh = det
                self.tracks[best_track_id].lost_frames = 0
                updated_tracks[best_track_id] = self.tracks[best_track_id]
            else:
                new_id = self.next_id
                self.next_id += 1
                new_track = Track(det, new_id)
                updated_tracks[new_id] = new_track

        # Remove lost tracks
        self.tracks = {
            track_id: track
            for track_id, track in updated_tracks.items()
        }

        return list(self.tracks.values())

    def compute_iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]

        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
        return iou
