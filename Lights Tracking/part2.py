import cv2
import numpy as np

lights_detected = []

def draw_polygon(event, x, y, flags, param):
    global lights_detected

    if event == cv2.EVENT_LBUTTONDOWN:
        lights_detected.append((x, y))
        cv2.circle(param, (x, y), 2, (0, 0, 255), -1)

        if len(lights_detected) > 1:
            cv2.line(param, lights_detected[-2], lights_detected[-1], (0, 0, 255), 2)

def draw_polygon_interaction(frame):
    global lights_detected
    clone = frame.copy()
    cv2.namedWindow('Draw Polygon')
    cv2.setMouseCallback('Draw Polygon', draw_polygon, param=clone)

    while True:
        cv2.imshow('Draw Polygon', clone)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('e'):  # Press 'd' to close the polygon drawing
            if len(lights_detected) > 2:
                # Draw the final line connecting the last and first points to close the polygon
                cv2.line(clone, lights_detected[-1], lights_detected[0], (255, 0, 255), 2)
                break

    cv2.destroyWindow('Draw Polygon')

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
            point_inside_polygon = cv2.pointPolygonTest(np.array(lights_detected), (cX, cY), False)
            if point_inside_polygon >= 0:
                light_coordinates.append((cX, cY))  # Append centroid coordinates to the list

    return light_coordinates

def mark_lights(image, light_coordinates):
    marked_image = image.copy()
    for coord in light_coordinates:
        cv2.circle(marked_image, coord, 5, (0, 255, 0), -1)  # Draw a filled circle at each light coordinate
    return marked_image

def main():
    global lights_detected

    # Load the original image
    original_image_path = 'lights9.jpg'
    original_frame = cv2.imread(original_image_path)
    if original_frame is None:
        print(f"Error reading image from {original_image_path}")
        return

    # Draw the polygon on the original image
    draw_polygon_interaction(original_frame)

    # Detect lights within the polygon
    threshold_value = 50  # Adjust the threshold as needed
    light_coordinates = detect_lights(original_frame, threshold_value)
    print(f'{len(light_coordinates)} lights detected')

    # Mark lights on the image
    marked_image = mark_lights(original_frame, light_coordinates)

    # Display the result
    cv2.imshow('Marked Image', marked_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
