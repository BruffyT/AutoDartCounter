import cv2
import numpy as np
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO

# Load YOLO model (Ensure you have a trained model for darts detection)
model = YOLO('yolov8n.pt')  # Replace with your trained model

# Initialize game variables
score1, score2 = 501, 501
current_player = 1
game_mode = 2  # Default is 2-player mode
lock = threading.Lock()

# Initialize camera (Modify index if using multiple cameras)
cap = cv2.VideoCapture(0)

# Dartboard reference (Modify based on real-world calibration)
dartboard_center = (320, 240)
dartboard_radius = 200


def detect_darts(frame):
    """ Detect darts using YOLO and return their positions. """
    results = model(frame)
    darts = []

    for r in results:
        for box in r.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box[:4])
            dart_x, dart_y = (x1 + x2) // 2, (y1 + y2) // 2
            darts.append((dart_x, dart_y))

    return darts


def update_score(darts):
    """ Update score based on detected darts. """
    global score1, score2

    for dart in darts:
        distance = np.linalg.norm(np.array(dart) - np.array(dartboard_center))
        if distance <= dartboard_radius:
            if current_player == 1:
                score1 = max(0, score1 - 10)  # Example: Deduct 10 points per dart
            else:
                score2 = max(0, score2 - 10)

    return score1, score2


def best_checkout(score):
    """ Compute best checkout strategy. """
    checkout = [50, 25] + [i for i in range(1, 21)] + [i * 2 for i in range(1, 21)] + [i * 3 for i in range(1, 21)]
    for i in checkout:
        for j in checkout:
            for k in checkout:
                if i + j + k == score:
                    return [i, j, k]
    return None


def switch_turn():
    """ Switch players in 2-player mode. """
    global current_player
    if game_mode == 2:
        current_player = 2 if current_player == 1 else 1
        update_ui()


def reset_game():
    """ Reset scores and player turns. """
    global score1, score2, current_player
    score1, score2 = 501, 501
    current_player = 1
    update_ui()


def update_ui():
    """ Refresh UI elements with latest scores and checkout suggestions. """
    player1_label.config(text=f"Player 1: {score1}")
    player2_label.config(text=f"Player 2: {score2}")
    player_turn_label.config(text=f"Current Player: {current_player}")

    checkout = best_checkout(score1 if current_player == 1 else score2)
    checkout_label.config(text=f"Best Checkout: {checkout if checkout else 'None'}")


def video_stream():
    """ Capture video, process frames, and update GUI. """
    ret, frame = cap.read()
    if not ret:
        return

    darts = detect_darts(frame)

    with lock:
        global score1, score2
        score1, score2 = update_score(darts)

    # Display updated scores
    update_ui()

    # Draw detected darts
    for (x, y) in darts:
        cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)

    # Convert frame to Tkinter-compatible format
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    img = img.resize((640, 480))
    imgtk = ImageTk.PhotoImage(image=img)

    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    video_label.after(10, video_stream)


def select_game_mode():
    """ Popup to select between 1-player and 2-player mode. """
    global game_mode
    response = messagebox.askquestion("Select Game Mode", "Do you want to play 2-player mode? (Yes for 2-player, No for 1-player)")
    game_mode = 2 if response == "yes" else 1


# Initialize Tkinter Window
root = tk.Tk()
root.title("Dart Scoring System")

# Player Score Labels
player1_label = tk.Label(root, text=f"Player 1: {score1}", font=("Arial", 14))
player1_label.pack()

player2_label = tk.Label(root, text=f"Player 2: {score2}", font=("Arial", 14))
player2_label.pack()

player_turn_label = tk.Label(root, text=f"Current Player: {current_player}", font=("Arial", 14))
player_turn_label.pack()

checkout_label = tk.Label(root, text="Best Checkout: None", font=("Arial", 12))
checkout_label.pack()

# Video Feed Display
video_label = tk.Label(root)
video_label.pack()

# Buttons for game control
button_frame = tk.Frame(root)
button_frame.pack()

switch_button = tk.Button(button_frame, text="Next Turn", command=switch_turn, font=("Arial", 12))
switch_button.grid(row=0, column=0, padx=10, pady=10)

reset_button = tk.Button(button_frame, text="Reset Game", command=reset_game, font=("Arial", 12))
reset_button.grid(row=0, column=1, padx=10, pady=10)

# Start Video Stream
select_game_mode()
video_stream()

# Run the Tkinter GUI
root.mainloop()

# Release Camera on Close
cap.release()
cv2.destroyAllWindows()
