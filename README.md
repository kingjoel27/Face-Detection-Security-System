# Face and Object Detection Security System (OpenCV)

This project implements a basic security system that combines real-time face and object detection with keypad-based passcode entry, running on a BeagleBone Black.

---

## Features
- Real-time face detection using OpenCV Haar Cascade classifiers
- Keypad-based passcode entry for user authentication
- Live video processing from a USB camera
- Embedded execution on BeagleBone Black

---

## Technologies Used
- Python 3
- OpenCV
- NumPy
- BeagleBone Black
- Linux (Debian)
- Matrix Keypad

---

## How It Works
- A USB camera captures live video frames.
- OpenCV processes each frame to detect faces and objects.
- A matrix keypad allows the user to enter a passcode.
- Access is granted or denied based on correct passcode entry.
- The entire system runs on a BeagleBone Black.

---
