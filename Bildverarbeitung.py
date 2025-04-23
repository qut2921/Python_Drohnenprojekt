import cv2 #type:ignore
import numpy as np #type:ignore
import os

def colorProfiles(n): 
    if n == 0: 
        name = "Blau" 
        hsv_lower = (90,50,50) 
        hsv_upper = (130,255,255) 
        return (name,hsv_lower,hsv_upper) 
    if n == 1: 
        name = "Rot" 
        hsv_lower = (160,100,100) 
        hsv_upper = (180,255,255) 
        return (name,hsv_lower,hsv_upper) 
    if n == 2: 
        name = "Gelb" 
        hsv_lower = (15, 100, 100) 
        hsv_upper = (35, 255, 255) 
        return (name,hsv_lower,hsv_upper) 
    if n == 3: 
        name = "Rot2" 
        hsv_lower = (0,100,100) 
        hsv_upper = (12,255,255) 
        return (name,hsv_lower,hsv_upper) 

def start_videoCapture():
    frame_width = 1280
    frame_height = 720
    vid = cv2.VideoCapture(1)
    vid.set(3, frame_width)  # set width
    vid.set(4, frame_height)  # set height
    return vid

def capture_and_convert(vid):
    success, frame = vid.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if not success:
        return None, None, None
    else:
        return success, hsv, frame

def calculate_GPS(pixel_x,pixel_y,pitch_telem,roll_telem,altitude_telem,gps_position,frame):
     pitch = pitch_telem
     roll = roll_telem #dummy variable
     altitude = altitude_telem #dummy variable [m]
     
     FOV_horizontal = 66 # [degrees]
     FOV_vertical = 41 # [degrees]
     
     # get frame dimensions
     frame_height,frame_width = frame.shape[:2]
     
     # angle for x-axis distance calculation in body coordinate system
     delta = FOV_horizontal * ((pixel_x / frame_width) - 0.5) + pitch # [degrees]
     # angle for y-axis distance calculation in body coordinate system
     epsilon = FOV_vertical * ((pixel_y / frame_height) - 0.5) + roll # [degrees]

     # x-axis distance calculation
     x_distance = altitude * np.tan(np.radians(delta)) # [m]
     # y-axis distance calculation
     y_distance = altitude * np.tan(np.radians(epsilon)) # [m]
     
     return x_distance, y_distance

     # GPS coordinates calculation

def locate_object(colorProfile,hsv,frame,min_area,pitch,roll,altitude,gps_position,detectedObject):
    name, hsv_lower, hsv_upper = colorProfiles(colorProfile)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper) 
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
    if contours: 
        # Sortieren der Konturen nach Flächengröße (absteigend) 
        biggest = sorted(contours, key=cv2.contourArea, reverse=True)[0] 
        area = cv2.contourArea(biggest)
                
                # Überprüfen ob die Fläche der vorgegebenen Mindestgröße entspricht 
        if area >= min_area: 
            x, y, w, h = cv2.boundingRect(biggest) 
                        
                    # Einrahmen der erkannten Kontur 
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)

                    # calculate GPS coordinates
            x_distance,y_distance = calculate_GPS(x,y,pitch,roll,altitude,gps_position,frame) 
                        
            # Label mit Namen und Koordinaten im OpenCV Vorschaufenster 
            text = f"{name} ({x}, {y}) ({x_distance:.2f} m, {y_distance:.2f} m)" 
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
            if  detectedObject == False: 
                        detectedObject = True 
                        print(f"Object detected") 
            else: 
                    # Zurücksetzen der Flag bei zu kleiner Fläche 
                    detectedObject = False
        else: 
            # Zurücksetzen der Flag falls keine Kontur gefunden worden ist 
            detectedObject = False
    return mask, hsv, frame

def capture_image(frame):
    frame

def module_main(vid,colorProfile,min_area,pitch,roll,altitude,speed,gps_position):
    detectedObject = False
    
    while True:
        # capture frame and convert to HSV
        success, hsv, frame = capture_and_convert(vid)
        if not success:
            break
        
        mask,hsv,frame = locate_object(colorProfile,hsv,frame,min_area,pitch,roll,altitude,gps_position,detectedObject)
        
     # Display the original frame and the grayscale frame
        cv2.putText(frame, f"Berechnung Distanz", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow('Mask', mask)
        cv2.imshow('HSV',hsv)
        cv2.imshow('Original Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    vid.release()
    cv2.destroyAllWindows()
    

    frame


    # Hallo wie gehts dir?

