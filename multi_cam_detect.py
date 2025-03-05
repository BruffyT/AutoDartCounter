import cv2
import numpy as np
from ultralytics import YOLO

# Load trained YOLO model
model = YOLO('/home/pi/best.pt')

# Open all three USB cameras
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)
cap3 = cv2.VideoCapture(2)

def detect_darts(frame):
    """ Detect darts using YOLOv8. """
    results = model(frame)
    darts = []

    for r in results:
        for box in r.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box[:4])
            dart_x, dart_y = (x1 + x2) // 2, (y1 + y2) // 2
            darts.append((dart_x, dart_y))

    return darts

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    ret3, frame3 = cap3.read()

    if not ret1 or not ret2 or not ret3:
        print("Error: One or more cameras not detected.")
        break

    # Detect darts
    darts1 = detect_darts(frame1)
    darts2 = detect_darts(frame2)
    darts3 = detect_darts(frame3)

    # Draw detected darts
    for (x, y) in darts1:
        cv2.circle(frame1, (x, y), 10, (0, 255, 0), -1)
    for (x, y) in darts2:
        cv2.circle(frame2, (x, y), 10, (0, 255, 0), -1)
    for (x, y) in darts3:
        cv2.circle(frame3, (x, y), 10, (0, 255, 0), -1)

    cv2.imshow("Camera 1", frame1)
    cv2.imshow("Camera 2", frame2)
    cv2.imshow("Camera 3", frame3)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap1.release()
cap2.release()
cv2.destroyAllWindows()
