import cv2
import pyautogui as pag
import Hand_Tracking_Module as htm
import math
import time


class GestureVolumeControl:
    def __init__(self, gesture_threshold=20, detection_confidence=0.7):
        self.detector = htm.handDetector(detectionCon=detection_confidence)
        self.gesture_threshold = gesture_threshold
        self.reference_position = None
        self.active = False


    def start_control(self,window, cap):
        self.cap = cap
        self.active = True

        while self.active:
            success, img = self.cap.read()
            lmList, _ = self.detector.findPosition(img, draw=False)

            if len(lmList) >= 13:
                # Get coordinates for volume control
                x1, y1 = lmList[8][1], lmList[8][2]  # Index tip
                x2, y2 = lmList[12][1], lmList[12][2]  # Middle tip
                distance = math.hypot(x2 - x1, y2 - y1)

                if self.reference_position is None and distance < self.gesture_threshold:
                    self.reference_position = (y1 + y2) // 2

                if self.reference_position is not None and distance < 20 and not self.is_desired_shape(lmList):
                    if y1 < self.reference_position - self.gesture_threshold:
                        pag.press("volumeup", presses=3)
                        self.reference_position = (y1 + y2) // 2
                    elif y1 > self.reference_position + self.gesture_threshold:
                        pag.press("volumedown", presses=3)
                        self.reference_position = (y1 + y2) // 2

                # Display feedback
                cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # C-shape check to stop volume control
            if self.is_desired_shape(lmList):
                window.destroy()
                time.sleep(2)
                break

            # cv2.imshow("Volume Control", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                window.destroy()
                time.sleep(2)
                break

    def is_desired_shape(self, lmList):
        """check for touch of index,middle,ring finger"""
        if lmList:
            index_tip_x, index_tip_y = lmList[8][0], lmList[8][1]
            middle_tip_x, middle_tip_y = lmList[12][0], lmList[12][1]
            ring_tip_x, ring_tip_y = lmList[16][0], lmList[16][1]
            wrist = lmList[0]

            # Calculate the length from wrist to middle finger tip
            length = math.hypot(middle_tip_x - wrist[0], middle_tip_y - wrist[1])
            
            # Approximate the width as half of the length
            width = length / 2
            
            # Approximate the hand area as a rectangle
            area = length * width

            #calculate distance between index, middle and ring finger
            distance_index_middle = math.hypot(middle_tip_x - index_tip_x, middle_tip_y - index_tip_y)
            distance_middle_ring = math.hypot(ring_tip_x - middle_tip_x, ring_tip_y - middle_tip_y)

            #check if distance is less than threshold
            if distance_index_middle < 0.05 * area and distance_middle_ring < 0.05 * area:
                if not hasattr(self, 'desired_shape_start_time'):
                    self.desired_shape_start_time = None
                    self.desired_shape_start_time = time.time()
                elif time.time() - self.desired_shape_start_time > 1:  # Gesture held for 1 second
                    return True
            else:
                # Reset the timer if the condition is not met
                self.desired_shape_start_time = time.time()
                


# if __name__ == "__main__":
#     cap = cv2.VideoCapture(0)
#     gesture_volume_control = GestureVolumeControl()
#     gesture_volume_control.start_control(cap)
#     cap.release()
#     cv2.destroyAllWindows()