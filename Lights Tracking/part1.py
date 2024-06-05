import cv2
import numpy as np

def detect_lights(image_path, threshold_value=150):
    # Read the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to detect bright areas
    _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

    # Find contours of bright areas
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Extract coordinates of the contours (lights)
    light_coordinates = []
    for contour in contours:
        # Calculate the area of the contour
        area = cv2.contourArea(contour)
        if area < 1600:  # Maximum area equivalent to a circle with diameter of 40 pixels
            # Calculate the centroid of the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])  # Centroid x-coordinate
                cY = int(M["m01"] / M["m00"])  # Centroid y-coordinate
                light_coordinates.append((cX, cY))  # Append centroid coordinates to the list

    return light_coordinates

def mark_lights(image, light_coordinates):
    marked_image = image.copy()
    for coord in light_coordinates:
        cv2.circle(marked_image, coord, 5, (0, 255, 0), -1)  # Draw a filled circle at each light coordinate
    return marked_image

if __name__ == "__main__":
    # Example usage:
    image_path = 'first.jpg'
    threshold_value = 50  # Adjust the threshold as needed

    light_coordinates = detect_lights(image_path, threshold_value)
    print(f'{len(light_coordinates)} lights detected')
    # Mark lights on the image
    image = cv2.imread(image_path)
    marked_image = mark_lights(image, light_coordinates)
    cv2.imwrite('marked_leftTree2.jpg', marked_image)
