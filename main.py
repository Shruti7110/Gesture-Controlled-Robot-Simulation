import cv2
import mediapipe as mp
import threading
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from robot_sim import SimpleRobotSim
from hand_joystick import HandJoystick

from performance_monitor import PerformanceMonitor
from performance_logger import PerformanceLogger

class GestureControlSystem:

    def __init__(self):

        # MediaPipe Hand Landmarker
        base_options = python.BaseOptions(
            model_asset_path="hand_landmarker.task"
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1
        )

        self.detector = vision.HandLandmarker.create_from_options(options)

        # Game components
        self.robot_sim = SimpleRobotSim()
        self.running = True
        self.joystick = HandJoystick()

        self.current_command = {
            "forward": 0,
            "turn": 0
        }
        self.perf_monitor = PerformanceMonitor()
        self.perf_logger = PerformanceLogger()

    def run_vision(self):
        """Simple vision thread - minimal UI for performance"""
    
        # print("=" * 60)
        # print("WAREHOUSE NAVIGATOR")
        # print("=" * 60)
        # print("Move hand UP/DOWN/LEFT/RIGHT to control robot")
        # print("Navigate to GREEN zone, avoid BOXES")
        # print("Press 'Q' to quit, 'R' to restart")
        # print("=" * 60)

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Lower resolution
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Lower resolution
        cap.set(cv2.CAP_PROP_FPS, 30)            # Request 30 FPS

        frame_skip_counter = 0
        
        # Wait for camera
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
            
            frame_skip_counter += 1
            if frame_skip_counter % 2 != 0:
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            result = self.detector.detect(mp_image)
            

            forward = 0
            turn = 0
            hand_x = None
            hand_y = None

            if result.hand_landmarks:
                hand_landmarks = result.hand_landmarks[0]

                # Get control point
                hand_x = int(hand_landmarks[9].x * w)
                hand_y = int(hand_landmarks[9].y * h)

                # Get commands
                forward, turn = self.joystick.get_command(hand_landmarks)
                self.perf_monitor.record_vision_frame()

            # Update command
            self.current_command = {
                "forward": forward,
                "turn": turn
            }

            # Draw simple control zone
            cx = w // 2
            cy = h // 2
            
            # Control circle
            cv2.circle(frame, (cx, cy), 80, (255, 255, 255), 2)
            cv2.circle(frame, (cx, cy), 3, (255, 255, 255), -1)
            
            # Hand dot
            if hand_x is not None and hand_y is not None:
                cv2.circle(frame, (hand_x, hand_y), 10, (0, 255, 0), -1)
                cv2.line(frame, (cx, cy), (hand_x, hand_y), (0, 255, 0), 2)

            # Minimal text overlay (top-left corner only)
            game_state = self.robot_sim.get_game_state()
            
            cv2.putText(frame, f"Battery: {game_state['battery']}/{game_state['max_battery']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Time: {int(game_state['time_limit'] - game_state['elapsed_time'])}s", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Performance stats (vision FPS and control latency)
            # stats = self.perf_monitor.get_stats_summary()

            # cv2.putText(frame, f"FPS: {stats['vision_fps']}", 
            #         (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            # cv2.putText(frame, f"Latency: {stats['avg_latency_ms']}ms", 
            #         (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            # Color code latency (green <50ms, yellow <100ms, red >100ms)
            # if stats['avg_latency_ms'] < 50:
            #     color = (0, 255, 0)  # Green
            # elif stats['avg_latency_ms'] < 100:
            #     color = (0, 255, 255)  # Yellow
            # else:
            #     color = (0, 0, 255)  # Red
            # Game over message
            if not game_state["game_active"]:
                if game_state["game_won"]:
                    msg = "DELIVERY COMPLETE!"
                    color = (0, 255, 0)
                else:
                    msg = "MISSION FAILED"
                    color = (0, 0, 255)
                
                cv2.putText(frame, msg, (w//2 - 150, h//2), 
                           cv2.FONT_HERSHEY_DUPLEX, 1.2, color, 3)
                cv2.putText(frame, "Press R to Restart", (w//2 - 120, h//2 + 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # Resize frame to 320x240 for smaller window
            frame = cv2.resize(frame, (320, 240))

            cv2.imshow("Warehouse Navigator", frame)

            key = cv2.waitKey(5) & 0xFF

            if key == ord('q') or key == 27:
                print("Shutting down...")
                self.running = False
                break
            elif key == ord('r') or key == ord('R'):
                if not game_state["game_active"]:
                    print("Restarting...")
                    self.restart_game()

        cap.release()
        cv2.destroyAllWindows()


    def run_simulation(self):
        """Simulation thread"""
        
        frame_count = 0
        last_report_time = time.time()
        last_log_time = time.time()

        while self.running:
            
            command = self.current_command

            self.robot_sim.update_velocity(
                command["forward"],
                command["turn"]
            )

            self.robot_sim.step()
            
            # Record simulation performance
            self.perf_monitor.record_sim_step()
            
            #  Log every 10 frames
            frame_count += 1  # Increment counter each loop
            current_time = time.time()
            if current_time - last_log_time >= 1.0:
                game_state = self.robot_sim.get_game_state()
                self.perf_logger.log(self.perf_monitor, game_state)
                last_log_time = current_time
            
            # Print report every 5 seconds
            if current_time - last_report_time >= 5.0:
                # self.perf_monitor.print_report()
                last_report_time = current_time

            time.sleep(0.01)  # Sleep to reduce CPU usage

    def restart_game(self):
        """Restart the game"""
        self.robot_sim.close()
        time.sleep(0.5)
        self.robot_sim = SimpleRobotSim()
        self.current_command = {"forward": 0, "turn": 0}
        print("Game restarted!")


    def start(self):
        """Start the game"""

        vision_thread = threading.Thread(target=self.run_vision)
        sim_thread = threading.Thread(target=self.run_simulation)

        vision_thread.start()
        sim_thread.start()

        try:
            vision_thread.join()
            sim_thread.join()

        except KeyboardInterrupt:
            print("Stopping...")
            self.running = False

        finally:
            # Close logger before robot
            self.perf_logger.close()
            self.robot_sim.close()
            print("Thanks for playing!")


if __name__ == "__main__":
    system = GestureControlSystem()
    system.start()