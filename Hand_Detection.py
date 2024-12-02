import cv2
import mediapipe as mp

class HandDetection:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1)
        self.mp_drawing = mp.solutions.drawing_utils

    def detect_hands(self, frame):
        """Detect hands in the given frame and return the landmark list and bounding box."""
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        lmlist = []
        bbox = []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                h, w, _ = frame.shape
                lmlist = [(int(landmark.x * w), int(landmark.y * h)) for landmark in hand_landmarks.landmark]
                bbox = self.get_bounding_box(lmlist)
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        return lmlist, bbox

    def get_bounding_box(self, lmlist):
        """Calculate the bounding box from the landmark list."""
        x_coords = [lm[0] for lm in lmlist]
        y_coords = [lm[1] for lm in lmlist]
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
