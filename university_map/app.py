import cv2
import numpy as np
import heapq
import sys
import subprocess

# Load the map image
map_img = cv2.imread('university_map.png')
map_img_copy = map_img.copy()

restart_button = (10, 600, 130, 50)  # x, y, width, height

points = [[996, 310], [996, 330], [996, 348], [996, 366], [996, 383],
          [996, 401], [996, 418], [996, 435], [996, 454], [996, 505],
          [996, 522], [996, 552], [996, 584], [363, 391], [363, 425],
          [360, 478], [360, 494], [360, 579], [360, 615]]

# Convert the map to a weighted map
# Assuming the path is white (255, 255, 255) and obstacles are black (0, 0, 0)
gray_map = cv2.cvtColor(map_img, cv2.COLOR_BGR2GRAY)
weighted_map = np.where(gray_map > 240, 1, 10)  # Paths are weighted 1, obstacles are weighted 10

# Variables to store the coordinates of start and end points
start_point = None
end_point = None

# Mouse callback function to select points
def select_points(event, x, y, flags, param):
    global start_point, end_point, map_img_copy, restart_button_clicked

    if event == cv2.EVENT_LBUTTONDOWN:
        if restart_button[0] < x < restart_button[0] + restart_button[2] and restart_button[1] < y < restart_button[1] + restart_button[3]:
            subprocess.Popen([sys.executable] + sys.argv)
            cv2.destroyAllWindows()
            sys.exit()
        else:
            selected_point = None
            n = 0 
            for point in points:
                
                if abs(point[0] - x) < 10 and abs(point[1] - y) < 10:  # Check if click is near a red point
                    if n == 0:
                        selected_point = (78, 65)
                    elif n == 1:
                        selected_point = (339, 138)
                    elif n == 2:
                        selected_point = (140, 246)
                    elif n == 3:
                        selected_point = (534, 226)
                    elif n == 4:
                        selected_point = (121, 336)
                    elif n == 5:
                        selected_point = (237, 105)
                    elif n == 6:
                        selected_point = (258, 255)
                    elif n == 7:
                        selected_point = (432, 209)
                    elif n == 8:
                        selected_point = (696, 247)
                    elif n == 9:
                        selected_point = (202, 141)
                    elif n == 10:
                        selected_point = (150, 161)
                    elif n == 11:
                        selected_point = (265, 304)
                    elif n == 12:
                        selected_point = (164, 100)
                    elif n == 13:
                        selected_point = (434, 59)
                    elif n == 14:
                        selected_point = (216, 247)
                    elif n == 15:
                        selected_point = (42, 127)
                    elif n == 16:
                        selected_point = (363, 311)
                    elif n == 17:
                        selected_point = (227, 265)
                    elif n == 18:
                        selected_point = (348, 257)    
                    break
                n += 1

            if selected_point is not None:
                if start_point is None:
                    start_point = selected_point
                    cv2.circle(map_img_copy, start_point, 5, (0, 255, 0), -1)
                    cv2.putText(map_img, 'Start', start_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                elif end_point is None:
                    end_point = selected_point
                    cv2.circle(map_img_copy, end_point, 5, (0, 0, 255), -1)
                    cv2.putText(map_img_copy, 'End', end_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.imshow('Map', map_img_copy)

restart_button_clicked = False

# Function to find the shortest path using A* algorithm
def a_star_search(start, end, weighted_map):
    rows, cols = weighted_map.shape
    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    while open_list:
        current = heapq.heappop(open_list)[1]

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])

            if 0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows:
                tentative_g_score = g_score[current] + weighted_map[neighbor[1], neighbor[0]]

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return []

# Heuristic function for A* (Euclidean distance)
def heuristic(a, b):
    return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

# Function to draw the path on the map
def draw_path(path, img):
    for i in range(len(path) - 1):
        start = path[i]
        end = path[i + 1]
        cv2.line(img, start, end, (255, 0, 0), 2)
    
    cv2.imshow('Map with Path', img)
    cv2.setMouseCallback('Map with Path', select_points)
    cv2.waitKey(0)
    # cv2.destroyAllWindows()



# Display the map and set the mouse callback function
cv2.imshow('Map', map_img)
cv2.setMouseCallback('Map', select_points)

# Wait until both points are selected
while True:
    map_img_copy = map_img.copy()  # Reset the image
    for point in points:
        cv2.circle(map_img_copy, point, 7, (0, 0, 255), -1)

    cv2.rectangle(map_img_copy, (restart_button[0], restart_button[1]), 
                  (restart_button[0] + restart_button[2], restart_button[1] + restart_button[3]), 
                  (255, 0, 0), -1)
    cv2.putText(map_img_copy, "Restart", (restart_button[0] + 10, restart_button[1] + 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow('Map', map_img_copy)
    

    

    
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or (start_point is not None and end_point is not None):  # Press 'ESC' to exit or when both points are selected
        break
    

cv2.destroyAllWindows()

# If both points are selected, find the path and draw it
if start_point is not None and end_point is not None:
    path = a_star_search(start_point, end_point, weighted_map)
    if path:
        draw_path(path, map_img_copy)
    else:
        print("No path found.")
else:
    print("Points not selected.")