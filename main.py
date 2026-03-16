import cv2
import mediapipe as mp
import threading
import time


from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gesture_recognizer import GestureRecognizer
from robot_sim import SimpleRobotSim

from hand_joystick import HandJoystick
# from gesture_to_command import GestureCommandMapper

class GestureControlSystem:

    def __init__(self):

        # -------------------------
        # MediaPipe Hand Landmarker
        # -------------------------

        base_options = python.BaseOptions(
            model_asset_path="hand_landmarker.task"
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1
        )

        self.detector = vision.HandLandmarker.create_from_options(options)

        # -------------------------
        # Other components
        # -------------------------

        #robot simulator
        self.robot_sim = SimpleRobotSim()
        self.running = True
        
        self.recognizer = GestureRecognizer()
        self.joystick = HandJoystick()
        # self.command_mapper = GestureCommandMapper()
        

        # self.current_gesture = "unknown"
        self.current_command = {
            "forward": 0,
            "turn": 0
        }
        


    def run_vision(self):

    
        print("Vision thread started")

        cap = cv2.VideoCapture(0)

        # wait for camera
        for _ in range(10):
            if cap.isOpened():
                break
            time.sleep(0.5)

        if not cap.isOpened():
            print("Camera failed to open")
            self.running = False
            return

        while self.running and cap.isOpened():

            success, frame = cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            result = self.detector.detect(mp_image)

            h, w, _ = frame.shape

            # joystick center
            cx = int(w * 0.5)
            cy = int(h * 0.5)

            forward = 0
            turn = 0

            if result.hand_landmarks:

                hand_landmarks = result.hand_landmarks[0]

                # use landmark 9 (middle finger base)
                x = int(hand_landmarks[9].x * w)
                y = int(hand_landmarks[9].y * h)

                # draw hand point
                cv2.circle(frame, (x, y), 10, (0,255,0), -1)

                dx = (x - cx) / w
                dy = (y - cy) / h

                forward = -dy * 3
                turn = dx * 3

                forward = max(min(forward, 1), -1)
                turn = max(min(turn, 1), -1)

            # update command for robot
            self.current_command = {
                "forward": forward,
                "turn": turn
            }

            # draw joystick circle
            cv2.circle(frame, (cx, cy), 100, (255,255,255), 2)

            # draw center
            cv2.circle(frame, (cx, cy), 5, (255,255,255), -1)

            # show command values
            cv2.putText(
                frame,
                f"Forward: {forward:.2f}",
                (10,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0,255,0),
                2
            )

            cv2.putText(
                frame,
                f"Turn: {turn:.2f}",
                (10,80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0,255,0),
                2
            )

            cv2.imshow("Gesture Robot Control", frame)

            key = cv2.waitKey(5) & 0xFF

            if key == ord('q') or key == 27:
                print("Shutting down...")
                self.running = False
                break

        cap.release()
        cv2.destroyAllWindows()


    def run_simulation(self):
        """Run robot simulation"""

        while self.running:
            
            command = self.current_command

            self.robot_sim.update_velocity(
                command["forward"],
                command["turn"]
            )

            self.robot_sim.step()

            time.sleep(0.01)


    def start(self):

        vision_thread = threading.Thread(target=self.run_vision)
        sim_thread = threading.Thread(target=self.run_simulation)

        vision_thread.start()
        sim_thread.start()

        try:
            vision_thread.join()
            sim_thread.join()

        except KeyboardInterrupt:
            print("Ctrl+C detected. Stopping...")
            self.running = False

        finally:
            self.robot_sim.close()


if __name__ == "__main__":

    system = GestureControlSystem()
    system.start()