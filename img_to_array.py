from __future__ import print_function
from PIL import Image
import math
import sys #Command Line arguments
import colorsys

def is_white(r, g, b):
	return (r == 255 and g == 255 and b == 255)

class img_to_array:
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

	# Line in an image -> distance from the bottom of the image
	def array_extract(self, im_rgb, line_r, line_g, line_b):
		width, height = im_rgb.size
		array = []
		for x in range (width):
			for y in range (height):
				r, g, b = im_rgb.getpixel((x,y))
				if (line_r == r and line_g == g and line_b == b):
					array.append(256 - y)
					break
		return array

	# Values which depend on image size -> percentage [0 - 100]
	def scale_8bit_to_percentage(self, array, height):
		for x in range (len(array)):
			array[x] = array[x] / (height / 100)
		return array

	# Scale brigthness percentage [0 - 100] logarithmically into [0 - 255]
	def scale_percentage_to_log(self, array):
		a = 0.977584631663603   # I found these terms on the internet and have no idea about
		b = 0.055498961535023   # the theory behind them
		for x in range (len(array)):
			array[x] = math.floor(a * math.exp((b * array[x])) - 1)
		return array

	# Make sure there's background and a signle line of color
	def im_prepare(self, im_rgb):
		width, height = im_rgb.size
		bg_found = False
		line_found = False
		told_about_colors = False
		line_r = 0
		line_g = 0
		line_b = 0
		for x in range (width):
			for y in range (height):
				r, g, b = im_rgb.getpixel((x,y))
				if (is_white(r, g, b)):
					if (bg_found == False):
						print('BG found')
						bg_found = True
				else:
					if (line_found == False):
						line_r = r
						line_g = g
						line_b = b
						print('Found line of color (%d, %d, %d)' % (line_r, line_g, line_b))
						line_found = True
					else:
						if (r != line_r or g != line_g or b != line_b):
							if (told_about_colors == False):
								print('Found another line of color (%d, %d, %d)' % (r, g, b))
								told_about_colors = True
		return (line_r, line_g, line_b)

def main():
	i2a = img_to_array()

	input_img_dir = 'input/'
	debug_data_dir = 'debug/'
	output_dir = 'output/'

	print ('Number of arguments:', len(sys.argv))
	print ('Argument list:', str(sys.argv))

	# Oopen the image:
	im = Image.open(input_img_dir + 'in.png')
	im_rgb = im.convert('RGB')
	(im_width, im_height) = im.size

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

if __name__ == '__main__':
	main()
