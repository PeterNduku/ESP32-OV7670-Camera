# SIGHTX — Camera Integration Milestone
### Eyes of the Blind | ESP32 + OV7670

This project documents an early hardware milestone in **SIGHTX**, an assistive technology initiative under the broader *Eyes of the Blind* mission.

The objective of this stage was to establish camera communication, capture an actual image, and transfer the image from an OV7670 camera module to a Windows laptop using an ESP32.

## Project Objective

Establish a working camera-capture pipeline as a foundation for future visual-perception experiments within SIGHTX.

## Hardware Used

- ESP32 development board
- OV7670 camera module
- USB cable
- Windows laptop

## Software and Tools

- Arduino IDE
- ESP32 Arduino framework
- C++
- Python
- PySerial for USB serial communication
- Pillow for Python image handling and preview development

## Milestone Achievements

- Established communication with the OV7670 camera sensor.
- Captured an actual image using the ESP32.
- Transferred image data to a Windows laptop over USB serial.
- Saved the captured frame as a BMP image.
- Began developing a Python-based SNAP interface for image capture and preview.

## Capture Specifications

| Specification | Value |
|---|---|
| Microcontroller | ESP32 |
| Camera module | OV7670 |
| Capture mode | QQVGA |
| Resolution | 160 × 120 pixels |
| Image format | BMP |
| Transfer interface | USB serial |
| Host system | Windows laptop |

## Evidence

Project evidence will include the actual captured image, photographs of the hardware setup, and a video demonstrating the camera operating and transferring image data.

## Next Steps

- Improve the Python capture and preview interface.
- Investigate higher camera resolutions and image quality.
- Explore image processing as a foundation for future computer-vision experiments.

## Connection to SIGHTX

Reliable camera capture is an early technical building block for SIGHTX. This milestone establishes image acquisition and transfer; object recognition and assistive visual perception remain future development goals.

## Project Status

**Milestone achieved:** Actual image capture and USB serial transfer demonstrated.

**Current scope:** Camera integration and image acquisition—not a completed smart-glasses or navigation system.

---

*Part of SIGHTX, developed under the Eyes of the Blind mission.*
