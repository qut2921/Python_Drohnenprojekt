import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cv2
import numpy as np
import utils.processor_ground as processor
import utils.colors as colors


def draw_rectangle_with_text(
        frame, x, y, w, h):
    """
    Draw a rectangle around the detected object and add text with its coordinates.
    If the text goes out of bounds, adjust its position and color.
    """

    # Set text properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    thickness = 1
    text_colour = (0, 0, 255)  # Red

    # Write text and get width and size
    text = f"({x}, {y})"
    (text_width, text_height), _ = cv2.getTextSize(text, font, scale, thickness)

    # Set default text position
    text_x = x
    text_y = y - 10

    # Adjust text position if it goes out of bounds
    if text_x + text_width > frame.shape[1]:
        text_x = frame.shape[1] - text_width - 10
        text_colour = (255, 0, 0)  # blue

    if text_y - text_height < 0:
        text_y = y + h + text_height + 5
        text_colour = (255, 0, 0)  # blue

    # Draw rectangle and text
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
    cv2.putText(
        frame, text, (text_x, text_y),
        font, scale, text_colour, thickness)

    return frame

def create_roi(image, x, y, w, h):
    """
    Create a Region of Interest (ROI) from the image.
    
    Args:
        image: The input image.
        x: The x-coordinate of the top-left corner of the ROI.
        y: The y-coordinate of the top-left corner of the ROI.
        w: The width of the ROI.
        h: The height of the ROI.
    
    Returns:
        The cropped image representing the ROI.
    """
    return image[y:y+h, x:x+w]

def detect_shape(roi_hsv, color,roi):
    
    l_thres = 109
    h_thres = 75
    
    edges = cv2.Canny(roi, l_thres, h_thres)
    contours_black, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    biggest = sorted(contours_black, key=cv2.contourArea, reverse=True)[0]
               

    if cv2.contourArea(biggest) >= 300:
        epsilon = 0.02*cv2.arcLength(biggest, True)
        approx = cv2.approxPolyDP(biggest, epsilon, True)
        cv2.drawContours(roi, [biggest], 0, (0, 255, 0), 2)

        x_black, y_black, w_black, h_black = cv2.boundingRect(approx)                        
        x_black_mid = int(x_black + w_black / 3)
        y_black_mid = int(y_black + h_black / 1.5)

        coords = (x_black_mid, y_black_mid)
        colour_text = (0, 0, 255)  # Red
        font = cv2.FONT_HERSHEY_DUPLEX

        if len(approx) == 3:
            cv2.putText(roi, "Dreieck", coords, font, 0.5, colour_text, 1)
            print("Dreieck erkannt")
        elif len(approx) == 4:
            cv2.putText(roi, "Rechteck", coords, font, 0.5, colour_text, 1)
            print("Rechteck erkannt")
        else:
            cv2.putText(roi, "Kreis", coords, font, 0.5, colour_text, 1)
            print("Kreis erkannt")
        
        return edges

def show_picture(image, hsv, color):
     
     cv2.startWindowThread()
     _, lower, upper = colors.set_colorProfiles(color)
     if color == 1:
        _, lower2, upper2 = colors.set_colorProfiles(3)
     
     if color == 1:
        mask1 = cv2.inRange(hsv, lower, upper)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]

     else:
        mask = cv2.inRange(hsv, lower, upper)


     contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

     if contours:
        for cnt in contours:
            area = cv2.contourArea(cnt)

                # Check if area is larger than minimum area
            if area >= 900:
                x, y, w, h = cv2.boundingRect(cnt)

                # draw rectangle and text
                image = draw_rectangle_with_text(
                        image,
                        x,
                        y,
                        w,
                        h)


                roi = create_roi(image, x, y, w, h)
                roi_hsv = create_roi(hsv, x, y, w, h)

                black_mask = detect_shape(roi_hsv, color, roi)
                        


                
                
     while True:
        cv2.imshow("Mask", mask)
        cv2.imshow("Frame", image)
        cv2.imshow("ROI", roi)
        cv2.imshow("Black Mask", black_mask)


         # Wait for 'q' key to exit
         # If 'q' is pressed, break the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

     cv2.destroyAllWindows()



if __name__ == "__main__":
    image_file = "BildsequenzTest_0/frame_0_2.jpg"
    color = 2  # Change to "blue" or "green" as needed

    image = cv2.imread(image_file)
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    show_picture(image, hsv, color)

