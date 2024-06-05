import cv2
import numpy as np

def find_light_coordinates(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to detect bright areas
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    # Find contours of bright areas
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Extract coordinates of the contours (lights)
    light_coordinates = []
    for contour in contours:
        # Calculate the centroid of the contour
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])  # Centroid x-coordinate
            cY = int(M["m01"] / M["m00"])  # Centroid y-coordinate
            light_coordinates.append((cX, cY))  # Append centroid coordinates to the list

    return light_coordinates

if __name__ == "__main__":
    # Example usage:
    image_path1 = 'center.jpg'
    image_path2 = 'shifted.jpg'

    # Find light coordinates in both images
    light_coordinates1, light_coordinates2 = find_light_coordinates(image_path1), find_light_coordinates(image_path2)

    # Calculate pixel shifts between the two images
    y_change = light_coordinates1[0][0] - light_coordinates2[0][0]  # Horizontal shift
    z_change = light_coordinates1[0][1] - light_coordinates2[0][1]  # Vertical shift

    # Known distance between camera and illuminated object
    distance = 1  # distance in feet

    # Calibration factor to convert pixel shifts to real-world coordinates for my iphone
    calibration = distance / 1310

    # Print the calculated pixel coordinates of the light
    print(f'Pixel coordinates of lights: {0}, {y_change * calibration}, {z_change * calibration}')
