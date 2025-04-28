import image_processing  # type: ignore
import cv2  # type: ignore

while True:
    image_processing.test_velocity()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
