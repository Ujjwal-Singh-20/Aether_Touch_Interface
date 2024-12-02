import cv2
import mediapipe as mp
import pyautogui

class VirtualCursor:
    def __init__(self):
        self.hand_detector = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils
        self.screen_width, self.screen_height = pyautogui.size()
        self.click_threshold = 0.06
        self.is_clicking = False
        self.is_scrolling = False
        self.reference_position = None

    def find_hand_landmarks(self, frame):
        """ Detects hand landmarks and updates cursor position based on index finger location. """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hand_detector.process(rgb_frame)
        landmarks = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger_pos = hand_landmarks.landmark[8]  
                thumb_tip_pos = hand_landmarks.landmark[4]  
                middle_finger_pos = hand_landmarks.landmark[12]
                ring_finger_pos = hand_landmarks.landmark[16]


                # Move the cursor
                x, y = int(index_finger_pos.x * self.screen_width), int(index_finger_pos.y * self.screen_height)
                pyautogui.moveTo(self.screen_width - x, y)


                # Detect left click (pinch gesture with thumb and middle finger)
                distance_left_click = ((middle_finger_pos.x - thumb_tip_pos.x) ** 2 + (middle_finger_pos.y - thumb_tip_pos.y) ** 2) ** 0.5

                if distance_left_click < self.click_threshold and not self.is_clicking:
                    self.is_clicking = True  # Register the click
                    pyautogui.click()
                elif distance_left_click >= self.click_threshold:
                    self.is_clicking = False  # Reset for the next pinch


                # Detect right click (pinch gesture with thumb and ring finger)
                distance_right_click = ((ring_finger_pos.x - thumb_tip_pos.x) ** 2 + (ring_finger_pos.y - thumb_tip_pos.y) ** 2) ** 0.5

                if distance_right_click < self.click_threshold and not self.is_clicking:
                    self.is_clicking = True
                    pyautogui.rightClick()
                elif distance_right_click >= self.click_threshold:
                    self.is_clicking = False


                # Detect scroll gesture (pinch gesture with thumb and index finger, hold and move up/down)
                distance_scroll_click = ((index_finger_pos.x - thumb_tip_pos.x) ** 2 + (index_finger_pos.y - thumb_tip_pos.y) ** 2) ** 0.5
                if distance_scroll_click < self.click_threshold and not self.is_scrolling:
                    self.is_scrolling = True
                    self.reference_position = y  # Store the initial position for scrolling, index finger y-coordinate

                elif distance_scroll_click >= self.click_threshold:
                    self.is_scrolling = False

                if self.is_scrolling:
                    pyautogui.scroll(y - self.reference_position)
                    self.reference_position = y  # Update the reference position



                # Draw landmarks on frame
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

                landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
        
        return frame, landmarks  # Return frame with annotations and landmarks
    

# if __name__ == "__main__":
#     vc = VirtualCursor()
#     cap = cv2.VideoCapture(0)
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame, landmarks = vc.find_hand_landmarks(frame)
#         cv2.imshow("Virtual Cursor", frame)

#         if cv2.waitKey(1) & 0xFF == 27:  # Exit on ESC
#             break

#     cap.release()
#     cv2.destroyAllWindows