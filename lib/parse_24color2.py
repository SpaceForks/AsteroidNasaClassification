# import the necessary packages
import numpy as np
import argparse
import cv2
import math

# Define the list of boundaries in the form [R, G, B]
boundaries = [
	([17, 15, 100], [50, 56, 200]),		# Red
	([86, 31, 4], [220, 88, 50]),		# Blue
	([25, 146, 190], [62, 174, 250]),	# Yellow
	([103, 86, 65], [145, 133, 128])	# Grey
]

clean_bounds = [
        ([86, 31, 4], [220, 88, 50]),           # Blue
        ([25, 146, 190], [62, 174, 250]),       # Yellow
]

threshold = 189 #pixels
p_to_cm   = 0.0264583333333334

 
def get_colour():
# loop over the boundaries
	image = cv2.imread("asteroid.ping")
	for (lower, upper) in boundaries:
	# create NumPy arrays from the boundaries
		lower = np.array(lower, dtype = "uint8")
		upper = np.array(upper, dtype = "uint8")
	# find the colors within the specified boundaries and apply
	# the mask
		mask = cv2.inRange(image, lower, upper)
		output = cv2.bitwise_and(image, image, mask = mask)
	# show the images
		cv2.imshow("images", np.hstack([image, output]))
		cv2.waitKey(0)
	checker(output)	

# Check to see that yellow and blue colourings are close to one another
# Pass in a 2D array of the pixel RGB values
def checker(image):
	for row in range(0, len(image)):
		for col in range(0, len(image[rows]):
			if not is_b(pixel, row, col, image):
				for degrees in range(0, 360):
					[x, y] = x_and_y(degrees)
					if is_b([x,y], image):
						return true
	return false
				
def is_b(pixel, pixelx, pixely, image):
	if [86, 31, 4] <= pixel and pixel <= [220, 88, 50]:
		return true

def distance(x, y, x1, y1):
	return math.sqrt((x-x1)**2 + (y-y1)**2)

def p_cm(pixel_distance):
	return pixel_distance * p_to_cmi

def x_and_y(degrees):
	x = threshold*math.cos(degrees)
	y = threshold*math.sin(degrees)
	return x, y
