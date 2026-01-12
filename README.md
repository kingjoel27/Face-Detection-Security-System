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
- BeagleBone Black
- Linux (Debian)
- Matrix Keypad
- Logitech C270 USB camera

---

## How It Works
- A USB camera is used to check if a face has been detected 
- The system activates a matrix keypad for passcode entry only when a detected face is present within the camera’s field of view.
- Access is granted or denied based on correct passcode entry.
- User is alerted if passcode is valid by using red/green LED's
- System captures picture of user after many failed attempts, which can then be accessed within the device.

---
