import cv2
import apriltag
import numpy as np

LINE_LENGTH = 50
CENTER_COLOR = (0, 255, 0)
CORNER_COLOR = (255, 0, 255)
ANGLE_COLOR = (0, 0, 255)  # Red color for the angle line


def plotPoint(image, center, color):
    center = (int(center[0]), int(center[1]))
    image = cv2.line(image,
                     (center[0] - LINE_LENGTH, center[1]),
                     (center[0] + LINE_LENGTH, center[1]),
                     color,
                     3)
    image = cv2.line(image,
                     (center[0], center[1] - LINE_LENGTH),
                     (center[0], center[1] + LINE_LENGTH),
                     color,
                     3)
    return image


def plotText(image, center, color, text):
    center = (int(center[0]) + 4, int(center[1]) - 4)
    return cv2.putText(image, str(text), center, cv2.FONT_HERSHEY_SIMPLEX,
                       1, color, 3)


def calculate_angle(corners):
    top_left = corners[0]
    bottom_left = corners[3]

    dy = top_left[1] - bottom_left[1]
    dx = top_left[0] - bottom_left[0]
    angle_radians = np.arctan2(dy, dx)

    angle_degrees = np.degrees(angle_radians)
    angle_degrees = (angle_degrees + 360) % 360

    return angle_degrees


def draw_angle_line(image, center, angle_degrees, color):
    angle_radians = np.radians(angle_degrees)
    x1 = int(center[0])
    y1 = int(center[1])
    x2 = int(center[0] + LINE_LENGTH * np.cos(angle_radians))
    y2 = int(center[1] - LINE_LENGTH * np.sin(angle_radians))
    cv2.line(image, (x1, y1), (x2, y2), color, 2)
    return image


def calculate_distance(focal_length, actual_tag_size, perceived_tag_size):
    distance = (actual_tag_size * focal_length) / perceived_tag_size
    return distance


detector = apriltag.Detector()
cam = cv2.VideoCapture(0)

looping = True

focal_length = 1000  # Focal length in pixels
actual_tag_size = 16  # Actual AprilTag size in millimeters

while looping:
    result, color_image = cam.read()
    gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
    detections = detector.detect(gray_image)

    if not detections:
        print("Nothing")
    else:
        for detect in detections:
            print("tag_id: %s, center: %s" % (detect.tag_id, detect.center))
            angle_horizontal_degrees = calculate_angle(detect.corners)
            angle_vertical_degrees = 0  # Change this if you have a different setup for vertical angle
            print("Horizontal Angle: %.2f degrees, Vertical Angle: %.2f degrees" % (
            angle_horizontal_degrees, angle_vertical_degrees))
            color_image = plotPoint(color_image, detect.center, CENTER_COLOR)
            color_image = plotText(color_image, detect.center, CENTER_COLOR, detect.tag_id)
            for corner in detect.corners:
                color_image = plotPoint(color_image, corner, CORNER_COLOR)
            color_image = plotPoint(color_image, detect.center, CENTER_COLOR)
            color_image = draw_angle_line(color_image, detect.center, angle_horizontal_degrees, ANGLE_COLOR)
            perceived_tag_size = max(np.linalg.norm(detect.corners[0] - detect.corners[1]),
                                     np.linalg.norm(detect.corners[0] - detect.corners[3]))
            distance = calculate_distance(focal_length, actual_tag_size, perceived_tag_size)
            print("Distance: %.2f millimeters" % distance)

    cv2.imshow('Result', color_image)
    key = cv2.waitKey(1)

    if key == 13:
        looping = False

cv2.destroyAllWindows()
cv2.imwrite("final.png", color_image)
