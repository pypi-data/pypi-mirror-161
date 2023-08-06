#
#    Copyright 2022 - Carlos A. <https://github.com/dealfonso>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
import math
class Point:
    """ A simple class to represent a point in 2D space """
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return f"({self.x}, {self.y})"

class Points:
    """A class to represent a set of 2D points"""

    def add(self, p) -> bool:
        """Adds a point to the list of points

        Args:
            p (list | dict | Point): a point to be added

        Returns:
            bool: True if the point was added successfully, False otherwise
        """
        if p is None:
            self._points.append(None)
            return True
        if type(p) == list or type(p) == tuple:
            try:
                x = p[0]
                y = p[1]
                self._points.append([x, y])
            except:
                self._points.append(None)
            return True
        if type(p) == dict:
            try:
                x = p['x']
                y = p['y']
                self._points.append([x, y])
            except:
                self._points.append(None)
            return True
        if type(p) == Point:
            self._points.append([p.x, p.y])
            return True
        return False

    def __init__(self, p_list = None):
        """Constructs the object, given a list of points

        Args:
            p_list (_type_, optional): List of points to be used. Defaults to None.
                * the elements of the list may be 
                    - tuples of two elements: (x,y)
                        * an empty tuple or list means the same as None
                    - dicts with the keys 'x' and 'y': { 'x': x, 'y': y }
                        * an empty dict or without x and y keys means the same as None
                    - Point objects
                    - None (means that there is an interruption in the drawing: a set of points means a polygon and None means
                      the end of the polygon and the start of a new one)
        """
        self._points = []
        if p_list == None:
            p_list = []
        for p in p_list:
            if not self.add(p):
                print("Error: Invalid point type")
        self._filter_out_multiple_nones()

    def _filter_out_multiple_nones(self) -> None:
        """Removes consecutive Nones from the list of points"""
        points = []
        prev = None
        for p in self._points:
            if p is None and prev is None:
                continue
            prev = p
            points.append(p)
        self._points = points

    def __iter__(self):
        """Iterates over the points

        Returns:
            iter: the iterator
        """
        for p in self._points:
            if p is None:
                yield None
            else:
                yield Point(p[0], p[1])
    def __len__(self):
        """Returns the number of points in the list

        Returns:
            int: number of points
        """
        return len(self._points)
    def __getitem__(self, index) -> Point:
        """Retrieves one single point from the list of points as a Point object

        Args:
            index (_type_): _description_

        Returns:
            _type_: _description_
        """
        p = self._points[index]
        if p is None:
            return None
        return Point(p[0], p[1])
    def normalize(self, width: int, height: int = None, keepAspectRatio: bool = True):
        """Normalizes the points to a given width and height. The idea is to make that the whole area covered by the points
             is contained by the given width and height. If keepAspectRatio is True, the ration between max width and height
             of the points in maintained when the points are normalize. If it is false, the points are contained in the with
             and height, but they will occupy as much space as possible (the smaller side will be stretched to the max size)

        Args:
            width (int): The with of the normalized points
            height (int, optional): The height of the normalized points (if None, take the same than width). Defaults to None.
            keepAspectRatio (bool, optional): Whether to keep or not the aspect ratio of the points. Defaults to True.
        """

        # Remove the multiple Nones
        self._filter_out_multiple_nones()

        # If the height is not given, take the same than width
        if (height == None):
            height = width

        # Get the max and min x and y values
        x = [ p[0] for p in self._points if p is not None ]
        y = [ p[1] for p in self._points if p is not None ]
        min_x = min(x)
        min_y = min(y)
        max_x = max(x)
        max_y = max(y)

        # Calculate the scale factor
        dx = max_x - min_x
        dy = max_y - min_y
        scaleX = width / dx
        scaleY = height / dy
        if keepAspectRatio:
            scaleX = min(scaleX, scaleY)
            scaleY = scaleX
        
        # Now calculate the offset to center the points
        offset_x = (width - dx * scaleX) / 2
        offset_y = (height - dy * scaleY) / 2

        # Finally, normalize the points
        for i in range(len(self._points)):
            if self._points[i] is None:
                continue
            self._points[i][0] = (self._points[i][0] - min_x) * scaleX + offset_x
            self._points[i][1] = (self._points[i][1] - min_y) * scaleY + offset_y

    def reduce_points(self):
        """Reduces the number of points in the list by removing the points that are too close to the line between the prior and the next one"""
        if len(self._points) < 2:
            return
        p0 = self._points[0]
        p1 = self._points[1]
        points = []
        for i in range(2, len(self._points)):
            advance = True
            p2 = self._points[i]

            if p0 is not None and p1 is not None:
                if p2 is None:
                    # End of path; need to add the points
                    points.append(p1)
                    points.append(p2)
                    p0 = None
                    p1 = None
                else:
                    P1 = Point(p0[0], p0[1])
                    P2 = Point(p2[0], p2[1])
                    p = Point(p1[0], p1[1])

                    # Calculate the distance of point p to line P1P2
                    den = math.sqrt((P2.x - P1.x) ** 2 + (P2.y - P1.y) ** 2)
                    if den == 0:
                        # The line is a point; we can discard it
                        advance = True
                    else:
                        d = abs((P2.x - P1.x) * (P1.y - p.y) - (P2.y - P1.y) * (P1.x - p.x)) / den
                        if d > 0.1:
                            points.append(p1)
                        else:
                            advance = False
            else:
                if p1 is not None:
                    points.append(p1)
            if advance:
                p0 = p1
            p1 = p2

        # Add the last point
        points.append(p2)
        self._points = points