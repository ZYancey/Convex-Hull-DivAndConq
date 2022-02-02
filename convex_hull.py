import time

from PyQt6.QtCore import QLineF, QPointF, QObject

# Some global color constants that might be useful
RED = (255, 105, 65)  # REDDISH ORANGE THAT LOOKS BETTER ON DARK SCREEN
GREEN = (0, 255, 0)
BLUE = (65, 201, 255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.005


class ConvexHullSolver(QObject):

    # CLASS CONSTRUCTOR
    def __init__(self):
        super().__init__()
        self.view = None
        self.pause = False

    # GUI FUNCTIONS ----------------------------------------------------------------------------------------------------

    def show_tangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def erase_tangent(self, line):
        self.view.clear_lines(line)

    def blink_tangent(self, line, color):
        self.show_tangent(line, color)
        self.erase_tangent(line)

    def show_hull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def erase_hull(self, polygon):
        self.view.clear_lines(polygon)

    def show_text(self, text):
        self.view.displayStatusText(text)

    def show_recursive_hull(self, leftHull, rightHull, upper, lower):
        left_drawn = [QLineF(leftHull[i], leftHull[(i + 1) % len(leftHull)]) for i in range(len(leftHull))]
        right_drawn = [QLineF(rightHull[i], rightHull[(i + 1) % len(rightHull)]) for i in range(len(rightHull))]
        upper_tangent = QLineF(leftHull[upper[0]], rightHull[upper[1]])
        lower_tangent = QLineF(leftHull[lower[0]], rightHull[lower[1]])
        self.show_hull(left_drawn, GREEN)
        self.show_hull(right_drawn, GREEN)
        self.show_tangent([upper_tangent, lower_tangent], BLUE)

        self.erase_hull(left_drawn)

        if self.pause:
            time.sleep(PAUSE)
        self.erase_hull(right_drawn)
        self.erase_tangent([upper_tangent, lower_tangent])
        self.erase_tangent([upper_tangent, lower_tangent])

    # END OF GUI FUNCTIONS ---------------------------------------------------------------------------------------------

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    # WORST CASE: O(2nlog(n)) or O(nlog(n)
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()

        # SORT ALL POINTS ACCORDING TO X VALUE AND PASS THEM INTO FUNCTION ---------------------------------------------
        # USING PYTHON SORT
        # WORST CASE: O(nlog(n))
        sorted_points = sorted(points, key=lambda point: point.x())
        # --------------------------------------------------------------------------------------------------------------

        t2 = time.time()
        t3 = time.time()

        # PASS INTO DIV AND CONQUER CONVEX HULL FUNCTION ---------------------------------------------------------------
        # WORST CASE: O(nlog(n))
        polygon = self.div_and_conq(sorted_points, pause, view)
        # --------------------------------------------------------------------------------------------------------------

        t4 = time.time()

        # WHEN PASSING LINES TO THE DISPLAY, PASS A LIST OF QLineF OBJECTS.  EACH QLineF
        # OBJECT CAN BE CREATED WITH TWO QPointF OBJECTS CORRESPONDING TO THE ENDPOINTS
        fullHull = [QLineF(polygon[i], polygon[(i + 1) % len(polygon)])
                    for i in range(len(polygon))]
        self.show_hull(fullHull, RED)
        self.show_text('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

    def div_and_conq(self, points, pause, view):

        num_points = len(points)
        if num_points == 1:
            return points

        # CALL CONVEX HULL FOR EACH SUB-ARRAY UNTIL THERE’S ONLY 1-2 POINTS IN THE DATA
        left_hull = self.div_and_conq(points[:num_points // 2], pause, view)
        right_hull = self.div_and_conq(points[num_points // 2:], pause, view)

        # CONNECT THE EDGES IN THE LOWEST CASE
        if len(left_hull) == 1 and len(right_hull) == 1:
            left_hull.extend(right_hull)
            return left_hull

        # FIND THE RIGHT MOST POINT OF THE LEFT HULL AND THE LEFT MOST POINT OF THE RIGHT HULL
        # WORST CASE O(n)
        left_initial = left_hull.index(
            max(left_hull, key=lambda left_point: left_point.x()))
        right_initial = right_hull.index(
            min(right_hull, key=lambda right_point: right_point.x()))

        # FIND THE UPPER TANGENT ---------------------------------------------------------------------------------------
        # WORST CASE O(n)
        i = left_initial
        j = right_initial
        left = True
        right = True
        slope = (right_hull[j].y() - left_hull[i].y()) / (right_hull[j].x() - left_hull[i].x())

        # CLIMB UP ALL THE POINTS IN THE HULL UNTIL YOU REACH THE TOP AS DECIDED BY THE SLOPE
        while left or right:
            left = False
            right = False
            while True:
                temp_slope = (right_hull[j].y() - left_hull[(i - 1) % len(left_hull)].y()) / (
                        right_hull[j].x() - left_hull[(i - 1) % len(left_hull)].x())

                if temp_slope < slope:
                    left = True
                    slope = temp_slope
                    i = (i - 1) % len(left_hull)
                else:
                    break

            while True:
                temp_slope = (right_hull[(j + 1) % len(right_hull)].y() - left_hull[i].y()) / (
                        right_hull[(j + 1) % len(right_hull)].x() - left_hull[i].x())

                if temp_slope > slope:
                    right = True
                    slope = temp_slope
                    j = (j + 1) % len(right_hull)
                else:
                    break

        upper_tangent = (i, j)

        # FIND THE LOWER TANGENT ---------------------------------------------------------------------------------------
        # WORST CASE O(n)
        i = left_initial
        j = right_initial
        left = True
        right = True
        slope = (right_hull[j].y() - left_hull[i].y()) / (right_hull[j].x() - left_hull[i].x())

        # CLIMB UP ALL THE POINTS IN THE HULL UNTIL YOU REACH THE TOP AS DECIDED BY THE SLOPE
        while left or right:
            left = False
            right = False
            while True:
                temp_slope = (right_hull[j].y() - left_hull[(i + 1) % len(left_hull)].y()) / (
                        right_hull[j].x() - left_hull[(i + 1) % len(left_hull)].x())
                if temp_slope > slope:
                    left = True
                    slope = temp_slope
                    i = (i + 1) % len(left_hull)
                else:
                    break

            while True:
                temp_slope = (right_hull[(j - 1) % len(right_hull)].y() - left_hull[i].y()) / (
                        right_hull[(j - 1) % len(right_hull)].x() - left_hull[i].x())
                if temp_slope < slope:
                    right = True
                    slope = temp_slope
                    j = (j - 1) % len(right_hull)
                else:
                    break

        lower_tangent = (i, j)

        # SHOW RECURSION IF SELECTED
        # IGNORED FROM O(n) CALCULATION
        if pause:
            self.show_recursive_hull(left_hull, right_hull, upper_tangent, lower_tangent)

        # COMBINE THE TWO HULLS WITH UPPER AND LOWER TANGENT -----------------------------------------------------------
        # WORST CASE O(n)
        final_hull = []
        k = lower_tangent[0]
        final_hull.append(left_hull[k])

        while k != upper_tangent[0]:
            k = (k + 1) % len(left_hull)
            final_hull.append(left_hull[k])
        k = upper_tangent[1]
        final_hull.append(right_hull[k])

        while k != lower_tangent[1]:
            k = (k + 1) % len(right_hull)
            final_hull.append(right_hull[k])
        return final_hull
        # BUMP UP A LEVEL IN RECURSION HERE
