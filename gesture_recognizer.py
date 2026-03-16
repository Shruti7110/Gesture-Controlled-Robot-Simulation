import math

class GestureRecognizer:
    def __init__(self):
        self.gesture_names = ['fist', 'open_hand', 'point', 'thumbs_up', 'peace']  

    def recognize(self, landmarks):

        fingers = []

        # Thumb
        if landmarks[4].x < landmarks[3].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # Index
        fingers.append(1 if landmarks[8].y < landmarks[6].y else 0)

        # Middle
        fingers.append(1 if landmarks[12].y < landmarks[10].y else 0)

        # Ring
        fingers.append(1 if landmarks[16].y < landmarks[14].y else 0)

        # Pinky
        fingers.append(1 if landmarks[20].y < landmarks[18].y else 0)

        count = sum(fingers)

        # Gesture classification
        if count == 0:
            gesture = "fist"

        elif count == 5:
            gesture = "open_hand"

        elif count == 2 and fingers[1] and fingers[2]:
            gesture = "peace"

        elif count == 1 and fingers[1]:
            gesture = "point"

        # 👍 thumbs up (only thumb raised)
        elif count == 1 and fingers[0]:
            gesture = "thumbs_up"

        else:
            gesture = "unknown"

        return gesture, count
    
    def _count_fingers_up(self, landmarks):
        """Count how many fingers are extended"""
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
        finger_pips = [6, 10, 14, 18]  # Joints below tips
        
        count = 0
        # ---- Thumb (use X direction) ----
        if landmarks[4].x < landmarks[3].x:
            count += 1

        for tip, pip in zip(finger_tips, finger_pips):
            # Finger is "up" if tip is above the joint
            if landmarks[tip].y < landmarks[pip].y:
                count += 1
        return count
    
    def _is_index_pointing(self, landmarks):
        """Check if index finger is extended and others are closed"""
        # Index tip (8) should be far from palm base (0)
        index_tip = landmarks[8]
        palm_base = landmarks[0]
        
        distance = math.sqrt(
            (index_tip.x - palm_base.x)**2 + 
            (index_tip.y - palm_base.y)**2
        )
        return distance > 0.2  # Threshold (tune this)