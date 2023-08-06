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
from .points import Points
from PIL import Image
import aggdraw
import math
from .color import color_lighten
import sys

try:
    aggdraw.Pen(color_lighten("#000", 0.5), linecap = 2)
except:
    sys.stderr.write("WARNING: The installed version of aggdraw does not support the linecap and linejoin options. Refer to the installation instructions to upgrade to a newer version to get better joins.\n\n")

class Options:
    """A class to represent the options for drawing"""
    canvasSize = 64
    canvasMargin = 4
    lineWidth = 4
    lineColor = '#000000'
    drawDynamics = True
    antiAliasing = True
    keepAspectRatio = True

    def __init__(self, **kwargs):
        """Constructs the object

        Args:
            **kwargs (dict): a dictionary with the options to be used
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.lineColor1 = color_lighten(self.lineColor, 0.6)
        self.lineColor2 = color_lighten(self.lineColor, 0.8)

class DrawHelper:
    """A class to draw a set of points"""
    def __init__(self, points: Points, options: Options) -> None:
        self._points = Points(points)
        options.canvasMargin = options.canvasMargin + options.lineWidth / 2

        self._points.normalize(options.canvasSize - options.canvasMargin * 2, options.canvasSize - options.canvasMargin * 2, options.keepAspectRatio)
        self._options = options

    def draw(self):
        canvas = Image.new('RGB', (self._options.canvasSize, self._options.canvasSize), '#FFFFFF')
        if (self._options.drawDynamics and self._options.antiAliasing):
            self._draw_points(canvas, self._options.lineColor2, self._options.canvasMargin, self._options.canvasMargin, None, True, 0.8)
            self._draw_points(canvas, self._options.lineColor1, self._options.canvasMargin, self._options.canvasMargin, None, True, 0.4)
        self._draw_points(canvas, self._options.lineColor, self._options.canvasMargin, self._options.canvasMargin, None, self._options.drawDynamics)
        return canvas

    def animate(self):
        image_collection = []
        for i in range(len(self._points)):
            canvas = Image.new('RGB', (self._options.canvasSize, self._options.canvasSize), '#FFFFFF')
            if (self._options.drawDynamics and self._options.antiAliasing):
                self._draw_points(canvas, self._options.lineColor2, self._options.canvasMargin, self._options.canvasMargin, i, True, 0.8)
                self._draw_points(canvas, self._options.lineColor1, self._options.canvasMargin, self._options.canvasMargin, i, True, 0.4)
            self._draw_points(canvas, self._options.lineColor, self._options.canvasMargin, self._options.canvasMargin, i, self._options.drawDynamics)
            image_collection.append(canvas)
        return image_collection

    def _draw_points(self, canvas, color, dx, dy, count = None, variableLineWidth = True, smoothWidth = 0):
        draw = aggdraw.Draw(canvas)
        points = self._points

        if (smoothWidth <= 0):
            smoothWidth = 0

        if count is None or count <=0:
            count = len(points)

        count = min(count, len(points))

        p0 = None
        p1 = None
        p2 = None
        p3 = None

        # This is the size of the line to be considered as the "quickest drawing"
        fQuick = math.sqrt(min(canvas.width, canvas.height))
        # When considered a quick line, this is the size of the line
        fQuickSize = 0.5

        moveto = True
        for i in range(count):
            p2 = points[i]
            p3 = None
            if (p2 is None):
                moveto = True
                continue

            if (i < count - 1):
                p3 = points[i + 1]

            if moveto:
                # Not needed, because we are drawing by segments
                # ctx.moveTo(p2.x + dx, p2.y + dy);
                p0 = None
                p1 = None
                moveto = False
            else:
                actualLineWidth = self._options.lineWidth
                if variableLineWidth:
                    # We need to calculate the actual line width. To do so, we need to calculate what means a "quick" line, to 
                    #   be drawin in a smaller size.
                    # The quick line is a line that is drawn between two points that are far apart. We consider that a line is
                    #   "quick" if is is longer than the square root of the size of the canvas (fQuick). And such line is drawn
                    #   in a size which is a percentage (fQuickSize) of the size of the line. The variations in the size of the
                    #   line will be applied as proportional to the difference between the smallest and biggest line size.
                    mX = p2.x - p1.x
                    mY = p2.y - p1.y
                    m = math.sqrt(mX * mX + mY * mY)
                    relLength = min(1, m/fQuick)
                    relSize = round((1 - relLength * (1 - fQuickSize)) * self._options.lineWidth)
                    actualLineWidth = relSize

                # If not smoothing the line, the line will be always drawn, and we'll also draw if the lineWidth is smaller
                #   this is because, when not smoothing the line, it will mean that we are drawing the front color. And if 
                #   the lineWidth is smaller, it will mean that we want to either draw the front color with a smaller sized
                #   line or we are drawing the shadow color to antialiase the line.
                # If smooting the line (i.e., antialiasing), but the actualLineWidth is the same, we do not have the need of
                #   antialiasing in this stroke. This is why we are not drawing in this case.
                if ((smoothWidth == 0) or (actualLineWidth < self._options.lineWidth)):
                    path = aggdraw.Path()
                    try:
                        pen = aggdraw.Pen(color, ((1.0 - float(smoothWidth)) * float(actualLineWidth)) + (float(self._options.lineWidth) * float(smoothWidth)), linecap = 2, linejoin = 2)
                    except:
                        pen = aggdraw.Pen(color, ((1.0 - float(smoothWidth)) * float(actualLineWidth)) + (float(self._options.lineWidth) * float(smoothWidth)))
                    path.moveto(p1.x + dx, p1.y + dy)
                    path.lineto(p2.x + dx, p2.y + dy)
                    draw.line(path, pen)

            p0 = p1
            p1 = p2
        draw.flush()