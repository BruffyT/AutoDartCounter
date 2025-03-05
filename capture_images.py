import cv2
import time

# Initialize cameras
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)
cap3 = cv2.VideoCapture(2)

frame_count = 0

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    ret3, frame3 = cap3.read()

    if not ret1 or not ret2 or not ret3:
        print("Camera error!")
        break

    # Save images
    cv2.imwrite(f"/home/pi/dart_images/cam1_{frame_count}.jpg", frame1)
    cv2.imwrite(f"/home/pi/dart_images/cam2_{frame_count}.jpg", frame2)
    cv2.imwrite(f"/home/pi/dart_images/cam3_{frame_count}.jpg", frame3)

    frame_count += 1
    time.sleep(1)  # Capture every second

    if frame_count >= 100:  # Stop after 100 images per camera
        break

cap1.release()
cap2.release()
cap3.release()
cv2.destroyAllWindows()
