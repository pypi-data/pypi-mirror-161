from scipy.spatial import distance
import re
import cv2
import numpy as np



def greet(name):
    """This function prints the string saying Hello to the name passed as argument.

    Args:
      name (str): The name of the person.

    Returns:
      None
    """
    print(f'Hello, {name}!')


def get_dist(pt1, pt2):
    """This function returns the distance between two points provided as argument.

    Args:
      pt1 (tuple): The tuple containing x, y coordinates of the first point.
      pt2 (tuple): The tuple containing x, y coordiantes of the second point.

    Returns:
      float: The distance between two points.
    """
    dist = distance.cdist((pt1,), (pt2,), 'euclidean')
    return dist[0][0]


class Rectangle:
    """This class contains the methods and attributes to get the information
    like area, perimeter etc from a rectangle which was created using the 
    height and width arguments passed to the constructor.

    Attributes:
      height (float): The height of the rectangle.
      width (float): The width of the rectangle.
    """
    def __init__(self, height, width):
        self.height = height
        self.width = width

    def area(self):
        """This function returns the area of the rectangle.

        Returns:
          float: The area of the rectangle.
        """
        return self.height*self.width

    def perimeter(self):
        """This function returns the perimeter of the rectangle.

        Returns:
          float: The perimeter of the rectangle.
        """
        return 2*(self.height+self.width)



# def get_arrow_coords(img):
#     _, img = cv2.threshold(img, 10, 255, cv2.THRESH_BINARY_INV)
#     labels, stats = cv2.connectedComponentsWithStats(img, 8)[1:3]

#     # for label in np.unique(labels)[1:]:
#     arrow = labels == np.unique(labels)[1:][0]
#     indices = np.transpose(np.nonzero(arrow))  # y,x
#     dist = distance.cdist(indices, indices, "euclidean")

#     far_points_index = np.unravel_index(np.argmax(dist), dist.shape)  # y,x

#     far_point_1 = indices[far_points_index[0], :]  # y,x
#     far_point_2 = indices[far_points_index[1], :]  # y,x

#     ### Slope
#     arrow_slope = (far_point_2[0] - far_point_1[0]) / (far_point_2[1] - far_point_1[1])
#     arrow_angle = math.degrees(math.atan(arrow_slope))

#     ### Length
#     arrow_length = distance.cdist(
#         far_point_1.reshape(1, 2),
#         far_point_2.reshape(1, 2),
#         "euclidean",
#     )[0][0]

#     ### Thickness
#     x = np.linspace(far_point_1[1], far_point_2[1], 20)
#     y = np.linspace(far_point_1[0], far_point_2[0], 20)
#     line = np.array([[yy, xx] for yy, xx in zip(y, x)])

#     x1, y1 = tuple(line[-1][::-1].astype(int))
#     x2, y2 = tuple(line[0][::-1].astype(int))

#     return x1, y1, x2, y2


def sort_by_num(list_of_strings):
    """This function sorts the list_of_strings based on the number.
    
    Args:
      list_of_strings (list): The list of strings each having a number as substring.
    
    Returns:
      list: The list of sorted strings based on number.
    """
    def comp(string):
        return int(re.findall('\d+', string)[0])
    
    return sorted(list_of_strings, key=comp)


def extract_red(image, save_to):
    """This function applies the upper and lower ranges to the image
    to extract the red color from it and saved the image with extracted
    text in the path specified.

    Args:
      image (numpy.ndarray): The image in the form of numpy array.
      save_to (str): The path where the output image will be saved.

    Returns:
      None
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    e = cv2.inRange(
        hsv, np.array([170, 50, 50]), np.array([180, 155, 150])
    )  ##Qualitive for newRed
    lower1 = np.array([0, 100, 20])
    upper1 = np.array([10, 255, 255])
    # upper boundary RED color range values; Hue (160 - 180)
    lower2 = np.array([160, 100, 20])
    upper2 = np.array([179, 255, 255])
    lower_mask = cv2.inRange(hsv, lower1, upper1)
    upper_mask = cv2.inRange(hsv, lower2, upper2)
    full_mask = lower_mask + upper_mask + e
    rmask = full_mask
    _, ir = cv2.threshold(rmask, 100, 220, cv2.THRESH_BINARY_INV)
    cv2.imwrite(save_to, ir)


class Point:
    """This is a class to create a point object.

    Attributes:
      x (float): The value of x coordinate.
      y (float): The value of y coordinate.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rectangles:
    """This is a class which contains methods to compare two rectangles.

    Attributes:
      l1 (Point object): The Point object that contains coordinates of top-left corner
        of the first rectangle.
      r1 (Point object): The Point object that contains coordinates of bottom-right corner
        of the first rectangle.
      l2 (Point object): The Point object that contains coordinates of top-left corner 
        of the second rectangle.
      r2 (Point object): The Point object that contains coordiantes of bottom-right corner
        of the second rectangle.
    """
    def __init__(self, l1, r1, l2, r2):
        self.l1 = l1
        self.r1 = r1
        self.l2 = l2
        self.r2 = r2

    # Returns true if two rectangles(l1, r1)
    # and (l2, r2) overlap
    def doOverlap(self):
        """This function checks whether two rectangles overlap or not.

        Returns:
          bool: The boolean value to determine whether rectangles overlap or not.
        """
        # To check if either rectangle is actually a line
        # For example : l1 ={-1,0} r1={1,1} l2={0,-1} r2={0,1}

        if (
            self.l1.x == self.r1.x
            or self.l1.y == self.r1.y
            or self.l2.x == self.r2.x
            or self.l2.y == self.r2.y
        ):
            # the line cannot have positive overlap
            return False

        # If one rectangle is on left side of other
        if self.l1.x >= self.r2.x or self.l2.x >= self.r1.x:
            return False

        # If one rectangle is above other
        if self.r1.y >= self.l2.y or self.r2.y >= self.l1.y:
            return False

        return True

    def common_area(self):
        """This function returns the common area shared by the two rectangles.

        Returns:
          float: The common area shared by the two rectangles.
        """
        if not self.doOverlap():
            return 0
        # find max distance of left side of rectangles from origin on x-axis
        top_left_x_of_common_rectangle = max(self.l1.x, self.l2.x)
        # find min distance of top side of rectangles from origin on y-axis
        top_left_y_of_common_rectangle = min(self.l1.y, self.l2.y)
        # find min distance of right side of rectangles from origin on x-axis
        bottom_right_x_of_common_rectangle = min(self.r1.x, self.r2.x)
        # find max distance of bottom side of rectangles from origin on y-axis
        bottom_right_y_of_common_rectangle = max(self.r1.y, self.r2.y)

        width_of_common_rectangle = (
            bottom_right_x_of_common_rectangle - top_left_x_of_common_rectangle
        )
        height_of_common_rectangle = (
            top_left_y_of_common_rectangle - bottom_right_y_of_common_rectangle
        )

        area_of_common_rectangle = (
            width_of_common_rectangle * height_of_common_rectangle
        )

        return area_of_common_rectangle
    
    def doCompleteOverlap(self):
        """This function check whether the two rectangles completely overlap
        or not.

        Returns:
          bool: The boolean value to determine whether the two rectangles completely
          overlap or not.
        """
        # To check if either rectangle is actually a line
        # For example : l1 ={-1,0} r1={1,1} l2={0,-1} r2={0,1}

        if (
            self.l1.x == self.r1.x
            or self.l1.y == self.r1.y
            or self.l2.x == self.r2.x
            or self.l2.y == self.r2.y
        ):
            # the line cannot have positive overlap
            return False

#         # If one rectangle is on left side of other
#         if self.l1.x >= self.r2.x or self.l2.x >= self.r1.x:
#             return False

#         # If one rectangle is above other
#         if self.r1.y >= self.l2.y or self.r2.y >= self.l1.y:
#             return False
        if self.l1.x < self.l2.x and self.l1.y > self.l2.y and self.r1.x > self.r2.x and self.r1.y < self.r2.y:
            # second rectangel completely lies inside the first one
            return True

        return False
