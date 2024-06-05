import cv2
import numpy as np

# Global variables to store coordinates of lights detected in the first and second images
lights_detected_first_image = []
lights_detected_second_image = []

# Function to handle mouse events for drawing a polygon on the image
def draw_polygon(event, x, y, flags, param):
    global lights_detected_first_image

    if event == cv2.EVENT_LBUTTONDOWN:
        lights_detected_first_image.append((x, y))  # Append clicked coordinates to the list
        cv2.circle(param, (x, y), 2, (0, 0, 255), -1)  # Draw a circle at the clicked point

        if len(lights_detected_first_image) > 1:
            cv2.line(param, lights_detected_first_image[-2], lights_detected_first_image[-1], (0, 0, 255), 2)  # Connect the last two clicked points with a line

# Function to interactively draw a polygon on the image
def draw_polygon_interaction(frame):
    global lights_detected_first_image
    clone = frame.copy()
    cv2.namedWindow('Draw Polygon')
    cv2.setMouseCallback('Draw Polygon', draw_polygon, param=clone)

    while True:
        cv2.imshow('Draw Polygon', clone)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('e'):  # Press 'e' to close the polygon drawing
            if len(lights_detected_first_image) > 2:
                # Draw the final line connecting the last and first points to close the polygon
                cv2.line(clone, lights_detected_first_image[-1], lights_detected_first_image[0], (255, 0, 255), 2)
                break

    cv2.destroyWindow('Draw Polygon')

# Function to detect lights within the polygon of the image
def detect_lights(image, threshold_value=150):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to detect bright areas
    _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

    # Find contours of bright areas
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Extract coordinates of the contours (lights) within the polygon
    light_coordinates = []
    for contour in contours:
        # Calculate the centroid of the contour
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])  # Centroid x-coordinate
            cY = int(M["m01"] / M["m00"])  # Centroid y-coordinate
            point_inside_polygon = cv2.pointPolygonTest(np.array(lights_detected_first_image), (cX, cY), False)
            if point_inside_polygon >= 0:
                light_coordinates.append((cX, cY))  # Append centroid coordinates to the list

    return light_coordinates

# Function to mark lights on the image, with different colors for lights found in the second image
def mark_lights(image, light_coordinates, other_light_coordinates):
    marked_image = image.copy()
    for coord in light_coordinates:
        if coord in other_light_coordinates:
            cv2.circle(marked_image, coord, 5, (255, 0, 0), -1)  # Mark with blue if found in the second image
        else:
            cv2.circle(marked_image, coord, 5, (0, 255, 0), -1)  # Mark with green if not found in the second image
    return marked_image

# Main function
def main():
    global lights_detected_first_image

    # Load the first original image
    first_image_path = 'lights9.jpg'
    first_frame = cv2.imread(first_image_path)
    if first_frame is None:
        print(f"Error reading image from {first_image_path}")
        return

    # Draw the polygon on the first original image
    draw_polygon_interaction(first_frame)

    # Detect lights within the polygon of the first image
    threshold_value = 50  # Adjust the threshold as needed
    light_coordinates_first_image = detect_lights(first_frame, threshold_value)
    print(f'{len(light_coordinates_first_image)} lights detected in the first image')

    # Load the second image
    second_image_path = 'lights7.jpg'
    second_frame = cv2.imread(second_image_path)
    if second_frame is None:
        print(f"Error reading image from {second_image_path}")
        return

    # Detect lights in the second image (for comparison)
    light_coordinates_second_image = detect_lights(second_frame, threshold_value)
    print(f'{len(light_coordinates_second_image)} lights detected in the second image')

    # Mark lights on the first image, marking those also found in the second image with a different color
    marked_image = mark_lights(first_frame, light_coordinates_first_image, light_coordinates_second_image)

    # Display the result
    cv2.imshow('Marked Image', marked_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
