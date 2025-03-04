from flask import Flask, jsonify, request
import cv2
from picamera2 import Picamera2
from ultralytics import YOLO
import os
import numpy as np

app = Flask(__name__)

# Load YOLO dart detection model
model = YOLO("dart_model.pt")

# Initialize three OV9732 cameras (index 0, 1, 2)
picam1 = Picamera2(0)  # First camera
picam2 = Picamera2(1)  # Second camera
picam3 = Picamera2(2)  # Third camera

# Set resolution to 1280x720 and limit FPS to 30
picam1.preview_configuration.main.size = (1280, 720)
picam1.preview_configuration.main.format = "RGB888"
picam1.preview_configuration.controls.FrameRate = 30
picam1.configure("preview")
picam1.start()

picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 30
picam2.configure("preview")
picam2.start()

picam3.preview_configuration.main.size = (1280, 720)
picam3.preview_configuration.main.format = "RGB888"
picam3.preview_configuration.controls.FrameRate = 30
picam3.configure("preview")
picam3.start()

# Default game settings
starting_score = 501
players = [{"name": "Player 1", "score": starting_score}, {"name": "Player 2", "score": starting_score}]
current_player = 0  # Index of active player

# Dart position to score (Example, replace with real mapping)
def get_score(x, y):
    return 50 if x < 100 and y < 100 else 20  # Example scoring logic

# Checkout combinations
checkout_options = {
    170: "T20, T20, Bull",
    167: "T20, T19, Bull",
    164: "T20, T18, Bull",
    161: "T20, T17, Bull",
    160: "T20, T20, D20",
    100: "T20, D20",
    40: "D20",
    32: "D16",
    24: "D12",
    2: "D1",
}

# Get best checkout options
def get_checkout_options(score):
    options = []
    for target in sorted(checkout_options.keys(), reverse=True):
        if score >= target:
            options.append(f"{target}: {checkout_options[target]}")
    return options if options else ["No checkout possible"]

# Capture images from all three cameras and run YOLO detection
def capture_images():
    frame1 = picam1.capture_array()
    frame2 = picam2.capture_array()
    frame3 = picam3.capture_array()

    # Resize frames for YOLO model input (640x640)
    resized_frame1 = cv2.resize(frame1, (640, 640))
    resized_frame2 = cv2.resize(frame2, (640, 640))
    resized_frame3 = cv2.resize(frame3, (640, 640))

    return resized_frame1, resized_frame2, resized_frame3

def detect_dart():
    """Captures an image from all cameras, resizes to 640x640, and runs dart detection"""
    frame1, frame2, frame3 = capture_images()

    # Run YOLO detection on each frame
    results1 = model(frame1)
    results2 = model(frame2)
    results3 = model(frame3)

    # Loop through each result and get dart scores
    for results in [results1, results2, results3]:
        for r in results:
            for box in r.boxes:
                x, y, w, h = map(int, box.xywh[0])
                return get_score(x, y)

    return None

# Handle dart throw
def throw_dart():
    global current_player
    score = detect_dart()

    if score:
        players[current_player]["score"] -= score
        if players[current_player]["score"] <= 0:
            players[current_player]["score"] = starting_score
            speak(f"{players[current_player]['name']} Bust! Restarting from {starting_score}")
        else:
            speak(f"{players[current_player]['name']} now has {players[current_player]['score']}")

    # Switch to next player
    current_player = (current_player + 1) % 2
    return {
        "players": players,
        "turn": players[current_player]["name"],
        "checkout": get_checkout_options(players[current_player]["score"]),
    }

# Set starting score (301, 501, 701)
@app.route("/set_score", methods=["POST"])
def set_score():
    global starting_score, players
    data = request.get_json()
    if "score" in data and data["score"] in [301, 501, 701]:
        starting_score = data["score"]
        players = [{"name": "Player 1", "score": starting_score}, {"name": "Player 2", "score": starting_score}]
        speak(f"Game set to {starting_score}")
        return jsonify({"message": "Game set", "players": players})
    return jsonify({"error": "Invalid score"}), 400

# Reset game
@app.route("/reset", methods=["GET"])
def reset():
    global players, current_player
    players = [{"name": "Player 1", "score": starting_score}, {"name": "Player 2", "score": starting_score}]
    current_player = 0
    speak("Game reset")
    return jsonify({"message": "Game reset", "players": players})

# Process dart throw
@app.route("/throw", methods=["GET"])
def throw():
    return jsonify(throw_dart())

# Voice output
def speak(text):
    os.system(f'espeak "{text}"')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
