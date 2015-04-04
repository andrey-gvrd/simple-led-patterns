from __future__ import print_function
from PIL import Image
import math
import sys 		# Command Line arguments
import colorsys	# HSL <-> RGB conversion
import copy

# Algorithm:
# 1. Make sure supplied image has:
# 	1.1. Black/white background
# 	1.2. Line (any object really) of a single color <- not necessary?
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

	# Creates a static table. Not very good when your indexes are floats.
	def hls_palette_create(self):
		self.base_h, self.base_l, self.base_s = colorsys.hls_to_rgb(self.line_color.r / 255.0, 
			                                                        self.line_color.g / 255.0, 
			                                                        self.line_color.b / 255.0)
		l_step = self.base_l / self.height
		l = self.base_l
		for x in range(0, self.height):
			self.hls_palette = {x / self.height: (self.h, l, self.s)} # Index is [0 - 1.0]
			l -= l_step

	# Reaturs an (h, l, s) value for any float value on the input. Basically [0.0 - 1.0] -> [0.0 - base_l]
	def hls_palette_get(self):
		return h, l, s = 

	def create_color_array(self, corrected_brightness_array):
		for x in range(self.width * 3):
			h, l, s = self.hls_palette[corrected_brightness_array[x]]

	def c_array(self, full_path, array):
		declaration_start = 'const uint8_t pattern[] = {\n'
		declaration_end   = '};\n'
		c_arr = open(full_path, 'w')
		c_arr.write(declaration_start)
		for x in range (len(array)):
			c_arr.write('\t')
			for y in range (16):
				c_arr.write(str(array[x]) + ', ')
			c_arr.write('\n')
		c_arr.write(declaration_end)

def correct_brightness_log(array):
	scale = 0.58   # To scale the logarithmic function to [0 - 1]
	for x in range(len(array)):
		array[x] = scale * (math.exp(array[x]) - 1)
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
	corrected_brightness_array = correct_brightness_log(brightness_array)

	# 5.
	i2a.hls_palette_create()

	# 6.
	color_array = i2a.create_color_array(corrected_brightness_array)

	'''
	# Get base color line:
	(line_r, line_g, line_b) = i2a.im_prepare(im_rgb)
	(line_h, line_l, line_s) = colorsys.rgb_to_hls(line_r/255.0, line_g/255.0, line_b/255.0)
	line_h *= 255.0
	line_l *= 255.0
	line_s *= 255.0

	# 
	new_width  = 1
	new_height = im_height
	im_hls = Image.new('RGB', (new_width, new_height), 'white')
	l = line_l
	l_start = l
	l_increment = l_start / new_height
	print('l_increment: %f' % l_increment)
	for y in range (new_height):
		l = l_start - y * l_increment
		print ('l: %f, y: %d' % (l, y))
		r, g, b = colorsys.hls_to_rgb(line_h/255.0, l/255.0, line_s/255.0)
		r *= 255
		g *= 255
		b *= 255
		print ('(%f, %f, %f)' % (r, g ,b))
		im_hls.putpixel((0, y), (int(r), int(g), int(b)))
	#im_hls.show()

	# Get line position into the array:
	array = i2a.array_extract(im_rgb, line_r, line_g, line_b)
	original = open(debug_data_dir + 'original.txt', 'w')
	for x in range (len(array)):
			original.write(str(array[x]) + '\t')

	# Put HLS data onto original line based on array data
	im_adj_array = Image.new('RGB', (im_width, im_height), 'white')
	for x in range (len(array)):
		im_adj_array.putpixel((x, 256 - array[x]), (im_hls.getpixel((0, 256 - array[x]))))
	#im_adj_array.show()

	# Put HLS data onto original line based on image data
	im_adj_image = im_rgb.copy()
	adj_array = []
	for x in range (im_width):
		for y in range (im_height):
			r_old, g_old, b_old = im_adj_image.getpixel((x, y))
			if (is_white(r_old, g_old, b_old) == False):
				adj_r, adj_g, adj_b = im_hls.getpixel((0, 256 - array[x]))
				adj_array.append(adj_r)
				adj_array.append(adj_g)
				adj_array.append(adj_b)
				im_adj_image.putpixel((x, y), (adj_r, adj_g, adj_b))
	im_adj_image.show()

	adj_array_file = open(debug_data_dir + 'adj_array.txt', 'w')
	for y in range (3):
		for x in range (y, len(adj_array), 3):
			print('x: %d' % x)
			adj_array_file.write(str(adj_array[x]) + '\t')
		adj_array_file.write('\n')	

	array = i2a.scale_8bit_to_percentage(array, im_height)

	percentage = open(debug_data_dir + 'percentage.txt', 'w')
	for x in range (len(array)):
			percentage.write(str(array[x]) + '\t')

	array = i2a.scale_percentage_to_log(array)

	out_array = open(debug_data_dir + 'out_array.txt', 'w')
	for x in range (len(array)):
			out_array.write(str(array[x]) + '\t')

	c_arr = i2a.c_array(output_dir + 'c_array.h', array)
	'''

if __name__ == '__main__':
	main()
