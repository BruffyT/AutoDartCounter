import cv2
import numpy as np
import time
from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO
import threading

# Initialize Flask app
app = Flask(__name__)

# YOLO model for dart detection (Make sure to train your own YOLO model for dart detection)
model = YOLO('yolov8n.pt')  # Path to your YOLO model (make sure it's properly trained)

# Initialize variables
score1 = 501
score2 = 501
current_player = 1
game_mode = 2  # Default to 2-player mode
lock = threading.Lock()

# Initialize the camera (Adjust camera index as needed)
cap = cv2.VideoCapture(0)  # 0 for the first camera, change if using another one

# Dartboard parameters (you can tune this based on your setup)
dartboard_center = (320, 240)  # Assuming a 640x480 resolution for simplicity
dartboard_radius = 200


def detect_darts(frame):
    """ Detect darts using YOLO model and return their coordinates """
    results = model(frame)
    detections = results.pandas().xywh[results.pandas().confidence > 0.5]

    darts = []
    for index, row in detections.iterrows():
        if row['class'] == 0:  # Assuming 'dart' is class 0 in your YOLO model
            dart_x, dart_y = int(row['xmin'] + (row['xmax'] - row['xmin']) / 2), int(
                row['ymin'] + (row['ymax'] - row['ymin']) / 2)
            darts.append((dart_x, dart_y))

    return darts


def update_score(darts, current_player):
    """ Update the score based on dartboard hit detection """
    global score1, score2
    for dart in darts:
        distance = np.linalg.norm(np.array(dart) - np.array(dartboard_center))
        if distance <= dartboard_radius:
            if current_player == 1:
                score1 -= 10  # Deduct 10 points for each hit (this is just an example)
            else:
                score2 -= 10
    return score1, score2


def best_checkout(score):
    """ Given a score, find the best checkout combination """
    combinations = []
    # Add single and double scores
    for i in range(1, 21):
        combinations.append(i)  # Single i
        combinations.append(i * 2)  # Double i
        combinations.append(i * 3)  # Triple i
    combinations.append(25)  # Bullseye for 50 points
    combinations.append(50)  # Bullseye

    # Try to find the best possible checkout combination
    for i in range(len(combinations)):
        for j in range(i, len(combinations)):
            for k in range(j, len(combinations)):
                total = combinations[i] + combinations[j] + combinations[k]
                if total == score:
                    return [combinations[i], combinations[j], combinations[k]]

    return None


def video_stream():
    """ Generate video stream for Flask web interface """
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect darts
        darts = detect_darts(frame)

        # Update the score
        global score1, score2
        with lock:
            score1, score2 = update_score(darts, current_player)

        # Get best checkout suggestion for the current score
        checkout = best_checkout(score1 if current_player == 1 else score2)

        # Show the dartboard, score, and checkout on the frame
        cv2.putText(frame, f"Player 1: {score1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Player 2: {score2}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        if checkout:
            cv2.putText(frame, f"Best Checkout: {checkout}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                        cv2.LINE_AA)

        # Encode the frame for streaming
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/')
def index():
    """ Home route to display the UI """
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """ Route for video feed to the web page """
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/next_turn')
def next_turn():
    """ Switch turns between players if 2-player mode is selected """
    global current_player
    if game_mode == 2:
        with lock:
            current_player = 2 if current_player == 1 else 1
    return jsonify({"current_player": current_player})


@app.route('/get_scores')
def get_scores():
    """ Get current scores for both players """
    return jsonify({"player1_score": score1, "player2_score": score2})


@app.route('/reset_game')
def reset_game():
    """ Reset the game to initial state """
    global score1, score2, current_player
    with lock:
        score1 = 501
        score2 = 501
        current_player = 1
    return jsonify({"player1_score": score1, "player2_score": score2})


@app.route('/set_player_mode/<int:mode>')
def set_player_mode(mode):
    """ Set the player mode (1-player or 2-player) """
    global game_mode
    with lock:
        game_mode = mode
        # Reset scores when switching game modes
        global score1, score2, current_player
        score1 = 501
        score2 = 501
        current_player = 1
    return jsonify({"game_mode": game_mode, "player1_score": score1, "player2_score": score2})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
