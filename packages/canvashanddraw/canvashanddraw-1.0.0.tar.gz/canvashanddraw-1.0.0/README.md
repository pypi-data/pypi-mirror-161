# Canvas Hand Draw
This is a utility to draw a set of points and to generate an image as if it was hand drawn by a human.

The need of having this component comes from an IA application, where a drawing is captured from a hand device (i.e. tablet or smartphone), and then the image is classified using a Neural Network. The points are captured to show the drawing to a human, who makes the initial classification to train the NN.

The effect is shown in the next image:

![Osito](img/osito.gif)

And using the same input data, it is possible to obtain different resolutions, colors, etc. by varying the settings:

![Osito 128](img/osito.128.gif)
![Osito 128 pen size 4](img/osito.128.4.gif)

> Most of the code of this library is a port to python of library [canvashanddraw](https://github.com/dealfonso/canvashanddraw).

**Technical facts**
- Includes tools to optimize the number of points, by skipping those that are too near to the line described by the adjacents points.
- It is possible to simulate the drawing dynamics by considering that the distance between the points is related to the speed of drawing. In that case, the faster a line is, the thinner it will be drawn, to simulate a ball pen.

## Installing

### Using pip

The easier method to install `canvashanddraw` is using pip:

```console
pip install canvashanddraw
```

### From sources

The alternate method is to clone the repo, install the dependencies and install by hand

```console
$ git clone https://github.com/dealfonso/pycanvashanddraw
$ cd pycanvashanddraw
$ pip install pillow imageio aggdraw
$ python setup.py install
```

### Dependencies

The dependencies from `canvashanddraw` are installed when installing from pip, but you can also install them by hand:

```console
pip install pillow imageio aggdraw
```

**WARNING:** `canvashanddraw` depends on [`aggdraw`](https://github.com/pytroll/aggdraw) library, which is also in pip (so it is automatically installed when installing from pip). The problem is that at the time of writing this text, the current version of that library does not produce the best results. Instead, my advise is to remove the version installed using pip and to install the latest `aggdraw` by hand:

```console
$ pip uninstall aggdraw
...
$ mkdir -p ./tmp
$ cd ./tmp
$ git clone https://github.com/pytroll/aggdraw
$ cd aggdraw
$ python setup.py build_ext -i
$ python setup.py install
```

## Using

Canvas Hand Draw is conceived both as a command line utility and a library so that you can include it in your application.

### Command Line Utility

If you have a set of points in a json file (e.g. file "five.json")

**five.json**

```json
[{"x": 211.33, "y": 130}, {"x": 210, "y": 130}, {"x": 199.33, "y": 130}, {"x": 177.66, "y": 130}, {"x": 154.33, "y": 130}, {"x": 135.33, "y": 130.66}, {"x": 124.33, "y": 132.33}, {"x": 120, "y": 133}, {"x": 118.66, "y": 133.33}, {"x": 118.66, "y": 133.66}, {"x": 118.66, "y": 134}, {"x": 118.66, "y": 138.66}, {"x": 118.66, "y": 144.33}, {"x": 118.33, "y": 159.33}, {"x": 116.66, "y": 176.66}, {"x": 114.66, "y": 191.33}, {"x": 113.33, "y": 201.33}, {"x": 112.66, "y": 206.33}, {"x": 112.33, "y": 208.33}, {"x": 112.33, "y": 209.33}, {"x": 112.33, "y": 210}, {"x": 113, "y": 209.66}, {"x": 118, "y": 208.66}, {"x": 131.33, "y": 205.66}, {"x": 150.66, "y": 202.33}, {"x": 171, "y": 200.33}, {"x": 186.66, "y": 200}, {"x": 197.33, "y": 200.66}, {"x": 205.33, "y": 203.66}, {"x": 210.33, "y": 207.33}, {"x": 213, "y": 212}, {"x": 213.66, "y": 219.66}, {"x": 212, "y": 230.33}, {"x": 208.33, "y": 241}, {"x": 202.66, "y": 251}, {"x": 195.66, "y": 260.66}, {"x": 183.33, "y": 272.33}, {"x": 173, "y": 279.66}, {"x": 165.33, "y": 283.33}, {"x": 150, "y": 289}, {"x": 137, "y": 292.33}, {"x": 127.66, "y": 294.66}, {"x": 122, "y": 295.66}, {"x": 119.33, "y": 296}, {"x": 119, "y": 296}]
```

You can run the next command line:

```console
$ canvashanddraw -i five.json -o five.png -w 64
```

To get the next drawing:

![Five](img/five.png)

### In your application

Having the same file `five.json`, you can use the next piece of code

```python
from canvashanddraw.points import Points
from canvashanddraw.drawhelper import DrawHelper, Options
import json

points = json.load(open('five.json'))
points = Points(points)
helper = DrawHelper(points, Options(canvasSize = 64, canvasMargin = 4, lineWidth = 4, lineColor = "#f00"))
helper.draw().save('five-red.png')
```

To generate the next drawing:

![Five Red](img/five-red.png)

## Defining the points

The points used to draw are defined in user-scale and they are later scaled to the target output.

Moreover, a single draw may consist of multiple drawings. In such case, the array of points used to define the drawing should include a `null` or an empty point (e.g. `[]`) to separate the drawings:

```json
[{"x": 211.33, "y": 130}, {"x": 210, "y": 130}, {"x": 199.33, "y": 130}, {"x": 177.66, "y": 130}, null, {"x": 135.33, "y": 130.66}, {"x": 124.33, "y": 132.33}, {"x": 120, "y": 133}, {"x": 118.66, "y": 133.33}, {"x": 118.66, "y": 133.66}, [], {"x": 165.33, "y": 283.33}, {"x": 150, "y": 289}, {"x": 137, "y": 292.33}, {"x": 127.66, "y": 294.66}, {"x": 122, "y": 295.66}, {"x": 119.33, "y": 296}, {"x": 119, "y": 296}]
```

## Options

There are multiple options to customize your results: the line width, the target resolution, the color, etc.

If using the CLI app, you are invited to use option `--help` to get the information about the different options.

When using the library, please check class `canvashanddraw.drawhelper.Options`:

```python
class Options:
    """A class to represent the options for drawing"""
    canvasSize = 64
    canvasMargin = 4
    lineWidth = 4
    lineColor = '#000000'
    drawDynamics = True
    antiAliasing = True
    keepAspectRatio = True
```