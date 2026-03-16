# Gesture-Controlled Robot Simulation 🤖✋

A real-time hand-controlled robot simulation that lets you drive a virtual robot using your hand as a **joystick**. The system uses computer vision to detect your hand position from a webcam and converts it into motion commands for a robot running in a physics simulator.

---

## Overview

This project combines **computer vision**, **hand tracking**, and **robot simulation** to create an intuitive control interface.

Instead of traditional gestures (fist, peace, etc.), the system uses **hand position as a joystick**:

* Move hand **up** → robot moves forward
* Move hand **down** → robot reverses
* Move hand **left** → robot turns left
* Move hand **right** → robot turns right

This produces smoother and more natural control than discrete gestures.

---

## Features

* Real-time **hand tracking** using MediaPipe
* **Joystick-style robot control** using hand position
* **Physics-based robot simulation** using PyBullet
* **Multithreaded architecture** for smooth vision + simulation
* On-screen **control feedback**
* Simple **exit controls (Q / ESC)**

---

## System Architecture

```
Webcam
   ↓
Hand Detection (MediaPipe)
   ↓
Hand Position → Joystick Mapping
   ↓
Velocity Command (forward + turn)
   ↓
Robot Simulation (PyBullet)
```

---

## Project Structure

```
GestureControlSystem/
│
├── main.py                # Main application entry point
├── robot_sim.py           # PyBullet robot simulator
├── gesture_recognizer.py  # (optional) gesture-based control
├── gesture_to_command.py  # gesture → robot command mapping
├── hand_joystick.py       # joystick-style hand control
│
├── hand_landmarker.task   # MediaPipe hand model
│
└── README.md
```

---

## Requirements

* Python 3.9+
* Webcam
* GPU not required

### Python Libraries

Install dependencies:

```bash
pip install opencv-python mediapipe pybullet numpy
```

Libraries used:

* OpenCV – camera capture and visualization
* MediaPipe – hand landmark detection
* PyBullet – robot physics simulation
* NumPy – numeric operations

---

## Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/GestureControlSystem.git
cd GestureControlSystem
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Download the MediaPipe hand model

Place `hand_landmarker.task` in the project directory.

---

## Running the Application

Start the program:

```bash
python main.py
```

This launches:

* a **camera window** showing hand tracking
* a **PyBullet simulation window** showing the robot

---

## Controls

### Hand Joystick Control

| Hand Movement | Robot Action |
| ------------- | ------------ |
| Hand Up       | Move Forward |
| Hand Down     | Reverse      |
| Hand Left     | Turn Left    |
| Hand Right    | Turn Right   |
| Hand Center   | Stop         |

The farther your hand moves from the center, the **faster the robot moves**.

---

## Exit Controls

You can exit the program using:

| Key        | Action                   |
| ---------- | ------------------------ |
| **Q**      | Quit program             |
| **ESC**    | Quit program             |
| **Ctrl+C** | Force exit from terminal |

Both the simulation and camera will shut down cleanly.

---

## How It Works

### 1. Hand Detection

MediaPipe detects **21 landmarks** on the hand from the webcam stream.

### 2. Hand Position Extraction

A stable landmark (middle finger base) is used as the **control point**.

### 3. Joystick Mapping

The position relative to the screen center is converted to:

```
forward velocity
turn velocity
```

### 4. Robot Simulation

These velocities control the wheels of a Husky robot inside a PyBullet physics simulation.

---

## Future Improvements

Possible extensions:

* Gesture-based commands (stop, reset, speed boost)
* Multiple robot support
* Depth camera integration
* Hand pose smoothing
* ROS integration
* Real robot hardware control

---

## Demo Idea

This project works great as a demo for:

* Human–Robot Interaction
* Computer Vision interfaces
* AI + Robotics integration
* Gesture-based control systems

---

## License

MIT License

---

## Acknowledgements

* MediaPipe team for the hand tracking model
* PyBullet for the robotics physics simulator
* OpenCV community for computer vision tools
