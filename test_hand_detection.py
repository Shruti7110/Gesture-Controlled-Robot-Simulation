import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gesture_recognizer import GestureRecognizer

# Create base options with the model
base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")

# Configure the hand landmarker
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
)

# Create the detector
detector = vision.HandLandmarker.create_from_options(options) # Use this line when using the actual MediaPipe hand landmarker

# initialize gesture recognizer
recognizer = GestureRecognizer()

# start webcam feed
cap = cv2.VideoCapture(0)

print("Press q to quit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert OpenCV image → MediaPipe image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # Run hand detection
    result = detector.detect(mp_image)

    # Draw landmarks
    if result.hand_landmarks:
        for hand_landmarks in result.hand_landmarks:
            # Recognize gesture
            gesture, count = recognizer.recognize(hand_landmarks)

            # Display gesture text
            cv2.putText(
                frame,
                f"Gesture: {gesture}",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            cv2.putText(
                frame,
                f"Fingers: {count}",
                (10,90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255,0,0),
                2
            )

            # Draw landmarks
            h, w, _ = frame.shape

            for landmark in hand_landmarks:

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (0, 255, 0),
                    -1
                )

    cv2.imshow("Hand Gesture Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

#cleanup
cap.release()
cv2.destroyAllWindows()