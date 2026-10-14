
import os
import time
import threading
import tkinter as tk
from tkinter import messagebox
from io import BytesIO

import serial
from PIL import Image, ImageTk

PORT = "COM7"
BAUD = 115200
SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

esp = None
busy = False
photo = None
closing = False

root = tk.Tk()
root.title("OV7670 SNAP Camera")
root.geometry("800x600")

status = tk.StringVar(value="Connecting to ESP32...")
preview = tk.Label(
    root,
    text="Waiting for camera...",
    bg="black",
    fg="white",
    font=("Arial", 16)
)
preview.pack(fill="both", expand=True, padx=10, pady=10)

tk.Label(root, textvariable=status).pack(pady=5)

snap_button = tk.Button(
    root, text="SNAP", font=("Arial", 14),
    state="disabled"
)
snap_button.pack(pady=5)


def set_status(message):
    if not closing:
        status.set(message)


def next_filename():
    number = 1
    while os.path.exists(
        os.path.join(SAVE_DIR, f"snapshot_{number:03d}.bmp")
    ):
        number += 1
    return f"snapshot_{number:03d}.bmp"


def read_line_until(deadline):
    """Read serial lines until a deadline."""
    while time.time() < deadline:
        line = esp.readline()
        if line:
            return line.decode("ascii", errors="ignore").strip()
    return None


def connect_camera():
    global esp

    try:
        set_status("Opening COM7...")
        esp = serial.Serial(
            PORT,
            BAUD,
            timeout=0.25,
            write_timeout=5
        )

        # Opening the port may reset the ESP32.
        # Wait for its actual READY message, not a fixed delay.
        set_status("Waiting for ESP32 camera READY...")
        deadline = time.time() + 40

        while time.time() < deadline and not closing:
            line = read_line_until(deadline)

            if line:
                print("ESP32:", line)

            if line == "READY":
                root.after(0, camera_ready)
                return

        root.after(
            0,
            lambda: set_status(
                "Timed out waiting for READY. Check ESP32 and COM port."
            )
        )

    except Exception as error:
        root.after(
            0,
            lambda msg=str(error): set_status(f"Connection error: {msg}")
        )


def camera_ready():
    set_status("Camera READY — press S or click SNAP.")
    snap_button.config(state="normal")


def snap():
    global busy

    if busy or closing or esp is None or not esp.is_open:
        return

    busy = True
    snap_button.config(state="disabled")
    set_status("Capturing image...")
    threading.Thread(target=capture_image, daemon=True).start()


def capture_image():
    global busy

    try:
        # Ask the existing ESP32 sketch for a frame.
        esp.write(b"C")
        esp.flush()

        deadline = time.time() + 20
        total_size = None

        while time.time() < deadline:
            line = read_line_until(deadline)

            if not line:
                continue

            print("ESP32:", line)

            if line.startswith("IMG:"):
                total_size = int(line.split(":", 1)[1])
                break

        if total_size is None:
            raise TimeoutError("No IMG size received from ESP32.")

        # Read exactly the announced number of binary bytes.
        data = bytearray()
        deadline = time.time() + 30

        while len(data) < total_size and time.time() < deadline:
            chunk = esp.read(min(4096, total_size - len(data)))
            if chunk:
                data.extend(chunk)

        if len(data) != total_size:
            raise TimeoutError(
                f"Incomplete image: {len(data)}/{total_size} bytes"
            )

        # Verify that the bytes form a readable image.
        Image.open(BytesIO(data)).verify()

        filename = next_filename()
        filepath = os.path.join(SAVE_DIR, filename)

        with open(filepath, "wb") as file:
            file.write(data)

        root.after(0, lambda d=bytes(data), p=filepath: display_image(d, p))

    except Exception as error:
        root.after(
            0,
            lambda msg=str(error): finish_error(msg)
        )


def display_image(data, filepath):
    global photo, busy

    try:
        image = Image.open(BytesIO(data)).convert("RGB")
        image.thumbnail((760, 460))

        photo = ImageTk.PhotoImage(image)
        preview.config(image=photo, text="")
        set_status(f"Saved {os.path.basename(filepath)}")

    except Exception as error:
        set_status(f"Display error: {error}")

    finally:
        busy = False
        if not closing:
            snap_button.config(state="normal")


def finish_error(message):
    global busy
    busy = False
    set_status(f"Capture failed: {message}")
    if not closing:
        snap_button.config(state="normal")


def on_key(event):
    key = event.keysym.lower()

    if key == "s":
        snap()
    elif key == "q":
        close_app()


def close_app():
    global closing

    closing = True

    try:
        if esp is not None and esp.is_open:
            esp.close()
    except Exception:
        pass

    root.destroy()


snap_button.config(command=snap)
root.bind("<KeyPress>", on_key)
root.protocol("WM_DELETE_WINDOW", close_app)

threading.Thread(target=connect_camera, daemon=True).start()
root.mainloop()
