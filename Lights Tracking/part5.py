import cv2
import numpy as np

def find_light_coordinates(image_path, threshold_value=150):
    # Read the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to detect bright areas
    _, thresh = cv2.threshold(gray, threshold_value, 150, cv2.THRESH_BINARY)

    # Find contours of bright areas
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Extract coordinates of the contours (lights)
    light_coordinates = []
    for contour in contours:
        # Calculate the centroid of the contour
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            light_coordinates.append((cX, cY))

    return light_coordinates

def find_delta(lights1, lights2):
    # Determine the length of the shorter list
    min_length = min(len(lights1), len(lights2))

    total_distance = 0
    for light1, light2 in zip(lights1[:min_length], lights2[:min_length]):
        # Calculate the vertical distance between corresponding lights
        delta_y = light1[1] - light2[1]
        total_distance += delta_y

    # Calculate the average y-distance
    average_delta_y = total_distance / min_length
    return average_delta_y

def rescale_lights(lights, delta):
    # Rescale the y-coordinates of lights by adding the calculated delta
    return [(tup[0], tup[1]+delta) for tup in lights]

def label_and_save(image, light_coordinates, output_path):
    # Draw circles and labels on the image for each light coordinate, then save the image
    labeled_image = image.copy()
    for i, coord in enumerate(light_coordinates):
        cv2.circle(labeled_image, coord, 5, (0, 255, 0), -1)
        cv2.putText(labeled_image, str(i+1), (coord[0] - 10, coord[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.imwrite(output_path, labeled_image)

if __name__ == "__main__":
    # Example usage:
    image_path1 = 'leftTree2.jpg'
    image_path2 = 'rightTree2.jpg'

    threshold_value = 90  # Adjust the threshold as needed

    # Find light coordinates in both images
    light_coordinates1 = find_light_coordinates(image_path1, threshold_value)
    light_coordinates2 = find_light_coordinates(image_path2, threshold_value)

    # Find the average vertical shift between lights in the two images
    delta_y = find_delta(light_coordinates1, light_coordinates2)

    # Rescale the y-coordinates of lights in the second image based on the calculated delta
    calibrated_lights = rescale_lights(light_coordinates2, delta_y)

    # Sort light coordinates by y-values
    sorted_light_coordinates1 = sorted(light_coordinates1, key=lambda x: x[1])
    sorted_light_coordinates2 = sorted(light_coordinates2, key=lambda x: x[1])
    calibrated_lights = sorted(calibrated_lights, key=lambda x: x[1])

    # Print the number of lights detected in each image
    print("Number of lights in image 1:", len(sorted_light_coordinates1))
    print("Number of lights in image 2:", len(sorted_light_coordinates2))

    # Known distance between camera and illuminated object
    distance = 1  # distance in feet

    # Calibration factor to convert pixel shifts to real-world coordinates
    calibration = distance / 1310

    # Calculate the real-world coordinates of each light in the first image
    all_positions = [(0, (light_coordinates1[i][0]-calibrated_lights[i][0])*calibration, (light_coordinates1[i][1]-calibrated_lights[i][1])*calibration) for i in range(len(light_coordinates1))]
    print(all_positions)
    # Label lights on image1 and save
    image1 = cv2.imread(image_path1)
    label_and_save(image1, sorted_light_coordinates1, 'labeled_leftTree2.jpg')

    # Label lights on image2 and save
    image2 = cv2.imread(image_path2)
    label_and_save(image2, sorted_light_coordinates2, 'labeled_rightTree2.jpg')
