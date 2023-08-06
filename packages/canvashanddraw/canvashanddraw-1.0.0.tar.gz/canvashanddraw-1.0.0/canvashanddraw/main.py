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
from .points import Points, Point
from .drawhelper import DrawHelper, Options
from .color import parse_color
from .version import VERSION
import argparse
import sys
import json

def main():
    """This application draws a set of points and generates an image with it
    """
    args = argparse.ArgumentParser(description=main.__doc__, formatter_class=argparse.RawTextHelpFormatter)
    args.add_argument("-i", "--input-file", help="the file to read the points from", type=str, default=None)
    args.add_argument("-o", "--output", help="the file to write the image to. The format will be detected by the suffix. If usign \"GIF\", it will create an animation as if it was hand drawn.", type=str, default=None)
    args.add_argument("-w", "--width", help="the width of the image (default: 128)", type=int, default=128)
    args.add_argument("-H", "--height", help="the height of the image (default: same as width)", type=int, default=None)
    args.add_argument("-c", "--color", help="the color of the pencil (default: #000)", type=str, default="#000")
    args.add_argument("-l", "--line-width", help="the width of the line (default: 4)", type=int, default=4)
    args.add_argument("-a", "--anti-aliasing", help="enable anti-aliasing (default: disabled)", action="store_true")
    args.add_argument("-d", "--dynamics", help="enable dynamics (default: disabled)", action="store_true")
    args.add_argument("-r", "--reduce-points", help="minimize the number of points (default: disabled)", action="store_true")
    args.add_argument("-m", "--margin", help="the margin of the image (default: 4)", type=int, default=4)
    args.add_argument('--version', action='version', version=VERSION)

    args = args.parse_args()
    if args.input_file is None:
        print("No file specified. Use -h for help.")
        sys.exit(1)
    if args.input_file == "-":
        infile = sys.stdin
    else:
        try:
            infile = open(args.input_file, "r")
        except:
            print("Error: Could not open file \"{}\"".format(args.input_file))
            sys.exit(1)

    try:
        jsondata = infile.read()
        infile.close()
    except:
        print("Error: Could not read file \"{}\"".format(args.input_file))
        sys.exit(1)

    try:
        points = json.loads(jsondata)
    except:
        print("Error: invalid JSON data")
        return 1

    if args.output is None:
        print("Error: no output file specified")
        return 1

    animation = False
    if args.output.lower().endswith(".gif"):
        animation = True

    points = Points(points)
    if args.reduce_points:
        l = len(points)
        points.reduce_points()
        l2 = len(points)
        print(f"Reduced from {l} to {l2} points {l2/l*100:.2f}%")

    if args.height is None:
        args.height = args.width

    if parse_color(args.color) is None:
        print("Error: invalid color")
        return 1

    helper = DrawHelper(points, Options(canvasSize = min(args.width, args.height), canvasMargin = args.margin, lineWidth = args.line_width, lineColor = args.color, antiAliasing = args.anti_aliasing, drawDynamics = args.dynamics))
    if animation:
        images = helper.animate()
        images[0].save(args.output, save_all=True, append_images=images[1:], fps=50, loop=0)

        # This is a second bullet to increase the speed of the animation
        import imageio
        finalimage = imageio.mimread(args.output)
        imageio.mimsave(args.output, finalimage, fps = min(len(images) / 5, 60))
    else:
        helper.draw().save(args.output)