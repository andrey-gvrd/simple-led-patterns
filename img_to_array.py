from __future__ import print_function
from PIL import Image
import math
import sys      # Command Line arguments
import colorsys # HSL <-> RGB conversion
import copy

# Algorithm:
# 1. Make sure supplied image has:
#   1.1. Black/white background
#   1.2. Line (any object really) of a single color <- not necessary?
# 2. Get the color of the line in RGB
# 3. Get an array of brightness values from line's y (height) value - [0 .. 1]
# 4. Correct the brightness array with log function to account for how eye perceives brightness. See more at:
#    http://what-when-how.com/display-interfaces/the-human-visual-system-display-interfaces-part-2
# 5. Based on extracted line's color and image's height create a pallet in HLS
# 6. Create an array of RGB colors based on the pallet and corrected brightness array

# Notes:
# - Top-left pixel must be a part of the background

class Color:

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __eq__(self, other):
        return (self.r == other.r and
                self.g == other.g and
                self.b == other.b)

    def is_white(self):
        return (self.r == 255 and 
                self.g == 255 and 
                self.b == 255)

    def is_black(self):
        return (self.r == 0 and 
                self.g == 0 and 
                self.b == 0)

class img_to_array:

    def __init__(self, im_rgb):
        self.im_rgb = im_rgb
        self.width, self.height = im_rgb.size

    line_color = Color(0, 0, 0)
    bg_color   = Color(0, 0, 0)
    hls_palette = {}

    # Base colors for hls_palette. Would have used Color class, but it works with integers only for now.
    base_h = 0.0
    base_l = 0.0
    base_s = 0.0

    def image_check(self):
        bg_found = False
        line_found = False
        for hor in range(self.width):
            for ver in range(self.height):
                current_pixel = Color(*self.im_rgb.getpixel((hor, ver)))
                if (current_pixel.is_white() or current_pixel.is_black()):
                    if (bg_found == False):
                        bg_found = True
                        self.bg_color = copy.copy(current_pixel)
                else:
                    if (line_found == False):
                        line_found = True
                        self.line_color = copy.copy(current_pixel)
        return (bg_found, line_found)

    # Line in an image -> brightness [1.0] as distance from the bottom of the image
    def brightness_extract(self):
        brightness_array = []
        for hor in range(self.width):
            for ver in range(self.height):
                current_pixel = Color(*self.im_rgb.getpixel((hor, ver)))
                if (current_pixel == self.line_color):
                    brightness_array.append((self.height - ver) / self.height)
                    break
        return brightness_array

    # Creates a static table for color reference (not used in the algorithm).
    def hls_palette_create(self):
        self.base_h, self.base_l, self.base_s = colorsys.rgb_to_hls(self.line_color.r / 255.0, 
                                                                    self.line_color.g / 255.0, 
                                                                    self.line_color.b / 255.0)
        l_step = self.base_l / self.height
        l = self.base_l
        for x in range(0, self.height):
            self.hls_palette = {x / self.height: (self.base_h, l, self.base_s)} # Index is [0 - 1.0]
            l -= l_step

    # Reaturs an (h, l, s) value for any float value on the input. Basically [0.0 - 1.0] -> [0.0 - base_l]
    def lightness_get(self, brightness):
        return  self.base_l * brightness

    def create_color_array(self, corrected_brightness_array):
        color_array = []
        for x in range(self.width):
            r, g, b = colorsys.hls_to_rgb(self.base_h, self.lightness_get(corrected_brightness_array[x]), self.base_s)
            color_array.extend((int(r * 256), int(g * 256), int(b * 256)))
        return color_array

    def c_array(self, full_path, array):
        length_str = '#define PATTER_LENGTH ' + str(len(array)) + '\n'
        declaration_start = 'const uint8_t pattern[] = {\n\t'
        declaration_end   = '\n};\n'
        c_arr = open(full_path, 'w')
        c_arr.write(length_str + declaration_start)
        for x in range(len(array)):
            c_arr.write(str(array[x]) + ', ')
            if (x % 15 == 0 and x > 0):
                c_arr.write('\n\t')
        c_arr.write(declaration_end)

def gamma_correction(array):
    power = 1 / 2.2
    for x in range(len(array)):
        array[x] **= power
    return array

def main():

    # Directories:
    input_img_dir = 'input/'
    debug_data_dir = 'debug/'
    output_dir = 'output/'

    # Open the image:
    im_rgb = Image.open(input_img_dir + 'in.png').convert('RGB')
    i2a = img_to_array(im_rgb)

    # 1. and 2. (oops)
    bg_found, line_found = i2a.image_check()

    # 3.
    brightness_array = i2a.brightness_extract()

    # 4.
    corrected_brightness_array = gamma_correction(brightness_array)

    # 5.
    i2a.hls_palette_create()

    # 6.
    color_array = i2a.create_color_array(corrected_brightness_array)

    # Debug output:
    color_array_file = open(debug_data_dir + 'color_array.txt', 'w')
    for x in range(3):
        for y in range(x, len(color_array), 3):
            color_array_file.write(str(color_array[y]) + '\t')
        color_array_file.write('\n')

    # 7.
    i2a.c_array(output_dir + 'out.h', color_array)

if __name__ == '__main__':
    main()
