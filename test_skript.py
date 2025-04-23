import Bildverarbeitung_V2  # type: ignore
import cv2  # type: ignore

while True:
    Bildverarbeitung_V2.test_velocity()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
