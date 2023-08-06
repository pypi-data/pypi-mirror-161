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
def parse_color(color: str) -> str:
    """Parses a string to indentify whether it is a valid color expression or not (using the HTML color notation)

    Args:
        color (str): The color (#fff or #ffffff) to be parsed

    Returns:
        str: the color in full hexadecimal notation (i.e. #ffffff) or None if it is not a valid color
    """
    if not color.startswith('#'):
        return None
    if len(color) == 4:
        return f"#{color[1]}{color[1]}{color[2]}{color[2]}{color[3]}{color[3]}"
    elif len(color) == 7:
        return color
    return None
def _color_to_rgb(color: str) -> list:
    """Splits a valid color expression into its RGB components

    Args:
        color (str): a color expression (i.e. #ffffff)

    Returns:
        list[3]: the components of the color in the form of a list (i.e. [255, 255, 255]) or [None, None, None] if the color is not valid
    """
    color = parse_color(color)
    if color is None:
        return None
    color = color[1:]
    return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
def color_mix(color1: str, color2: str, percentage: float) -> str:
    """Obtains the mix of two colors, given a percentage of the distance between them

    Args:
        color1 (str): the first color
        color2 (str): the second color
        percentage (float): the percentage of the distance between the two colors to get

    Returns:
        str: the color in html notation (i.e. #ffffff) or None if any of the colors is not valid
    """
    color1 = _color_to_rgb(color1)
    color2 = _color_to_rgb(color2)
    if color1 is None or color2 is None:
        return None
    mix = [
        int(color1[0] * (1 - percentage) + color2[0] * percentage),
        int(color1[1] * (1 - percentage) + color2[1] * percentage),
        int(color1[2] * (1 - percentage) + color2[2] * percentage)
    ]
    return f"#{mix[0]:02x}{mix[1]:02x}{mix[2]:02x}"
def color_lighten(color: str, percentage: float) -> str:
    """Obtains a lighter color of a given color

    Args:
        color (str): a color expression (i.e. #ffffff)
        percentage (float): the amount of light to be added to the color (0.0 to 1.0)

    Returns:
        str: the color in html notation (i.e. #ffffff) or None if the color is not valid
    """
    return color_mix(color, '#ffffff', percentage)
def color_darken(color, percentage):
    """Obtains a darker color of a given color

    Args:
        color (str): a color expression (i.e. #ffffff)
        percentage (float): the amount of dark to be added to the color (0.0 to 1.0)

    Returns:
        str: the color in html notation (i.e. #ffffff) or None if the color is not valid
    """
    return color_mix(color, '#000000', percentage)
