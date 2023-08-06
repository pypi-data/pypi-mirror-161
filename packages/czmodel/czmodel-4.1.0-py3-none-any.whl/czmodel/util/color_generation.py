# CZModel provides simple-to-use conversion tools to generate a CZANN to be used in ZEISS ZEN Intellesis Portfolio
# Copyright 2022 Carl Zeiss Microscopy GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# To obtain a commercial version please contact Carl Zeiss Microscopy GmbH.
"""Provides a color generator class that creates an infinite sequence of colors."""
import colorsys
from enum import Enum
from typing import Tuple, List, Optional


class Hue(Enum):
    """Container for basic colors."""

    RED = 0
    YELLOW = 1
    GREEN = 2
    CYAN = 3
    BLUE = 4
    MAGENTA = 5


HUE_LUT = {
    Hue.RED: Hue.GREEN,
    Hue.YELLOW: Hue.MAGENTA,
    Hue.GREEN: Hue.BLUE,
    Hue.CYAN: Hue.RED,
    Hue.BLUE: Hue.YELLOW,
    Hue.MAGENTA: Hue.CYAN,
}


class ColorGenerator:
    """Class providing functionality for generating an infinite sequence of colors."""

    def __init__(self, initial_color: Tuple[int, int, int] = (255, 0, 0)) -> None:
        """Initializes a color generator instance.

        Args:
            initial_color: The color to start with.
        """
        self.initial_color = colorsys.rgb_to_hls(
            *(initial_color_channel / 255.0 for initial_color_channel in initial_color)
        )
        self.current_color: Optional[List[float]] = None
        self.current_iteration = 0

    def __iter__(self) -> "ColorGenerator":
        """Creates an iterator from the color generator class."""
        return self

    def __next__(self) -> Tuple[int, int, int]:
        """Yields the next color."""
        if self.current_color is None:
            self.current_color = list(self.initial_color)
        else:
            # Make sure that the hue influences the color perceivably
            if self.current_color[2] < 0.5:
                self.current_color[2] = 0.5
            if self.current_color[1] < 0.3:
                self.current_color[1] = 0.3
            elif self.current_color[1] > 0.7:
                self.current_color[1] = 0.7
            # To prevent pink directly after red
            if self.current_iteration == 1:
                self.current_iteration += 1
            next_hue = float(HUE_LUT[Hue(self.current_iteration % len(Hue))].value)
            iteration = int(self.current_iteration / len(Hue))
            next_hue += iteration / (iteration + 1.0)
            self.current_color[0] = ((next_hue * (1.0 / len(Hue))) + 1.0) % 1.0
            self.current_iteration += 1
        color_rgb = colorsys.hls_to_rgb(*self.current_color)
        return int(color_rgb[0] * 255), int(color_rgb[1] * 255), int(color_rgb[2] * 255)
