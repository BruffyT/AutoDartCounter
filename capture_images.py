import cv2

# Open all three USB cameras
cap1 = cv2.VideoCapture(0)  # First camera
cap2 = cv2.VideoCapture(1)  # Second camera
cap3 = cv2.VideoCapture(2)  # Third camera

image_count = 0

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    ret3, frame3 = cap3.read()

    if not ret1 or not ret2 or not ret3:
        print("Error: One or more cameras not detected.")
        break

    cv2.imshow("Camera 1", frame1)
    cv2.imshow("Camera 2", frame2)
    cv2.imshow("Camera 3", frame3)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):  # Save images when 's' is pressed
        cv2.imwrite(f"dataset/cam1_{image_count}.jpg", frame1)
        cv2.imwrite(f"dataset/cam2_{image_count}.jpg", frame2)
        cv2.imwrite(f"dataset/cam3_{image_count}.jpg", frame3)
        print(f"Saved images {image_count}")
        image_count += 1

    elif key == ord('q'):  # Quit with 'q'
        break

cap1.release()
cap2.release()
cap3.release()
cv2.destroyAllWindows()
