# -*- coding: utf-8 -*-
"""FINAL3_CIS581_proj2_cannyEdge_nicholas_gurnard_ankit_billa.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tZwOqsSGE9pnDM1DlLveid5xes9EX02h
"""

assignment_path_N = '/home/nicholas/Documents/UPenn/CIS581/Projects/Project2_edge_detection/github_folder'
  
# Setup assignment folder and switch
import os
os.makedirs(assignment_path_N, exist_ok=True)
os.chdir(assignment_path_N)

#os.makedirs(assignment_path_A, exist_ok=True)
#os.chdir(assignment_path_A)

import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from scipy import signal
from PIL import Image
import argparse

# Copy the path of the folder that contains this notebook using the file navigation on the left:
# Ex. /content/drive/My\ Drive/CIS 581-Online/Canny Edge Project/Learner Code and Images/Code
# sys.path.append('/content/drive/MyDrive/CIS581/Project2_edge_detection/Project 2 Canny Edge Learner_Code_and_Images/Code')
sys.path.append(assignment_path_N)
#sys.path.append(assignment_path_A)

# import functions
from helpers import interp2

"""# Tests and Visualization"""

def interp2(v, xq, yq):
	dim_input = 1
	if len(xq.shape) == 2 or len(yq.shape) == 2:
		dim_input = 2
		q_h = xq.shape[0]
		q_w = xq.shape[1]
		xq = xq.flatten()
		yq = yq.flatten()

	h = v.shape[0]
	w = v.shape[1]
	if xq.shape != yq.shape:
		raise 'query coordinates Xq Yq should have same shape'

	x_floor = np.floor(xq).astype(np.int32)
	y_floor = np.floor(yq).astype(np.int32)
	x_ceil = np.ceil(xq).astype(np.int32)
	y_ceil = np.ceil(yq).astype(np.int32)

	x_floor[x_floor < 0] = 0
	y_floor[y_floor < 0] = 0
	x_ceil[x_ceil < 0] = 0
	y_ceil[y_ceil < 0] = 0

	x_floor[x_floor >= w-1] = w-1
	y_floor[y_floor >= h-1] = h-1
	x_ceil[x_ceil >= w-1] = w-1
	y_ceil[y_ceil >= h-1] = h-1

	v1 = v[y_floor, x_floor]
	v2 = v[y_floor, x_ceil]
	v3 = v[y_ceil, x_floor]
	v4 = v[y_ceil, x_ceil]

	lh = yq - y_floor
	lw = xq - x_floor
	hh = 1 - lh
	hw = 1 - lw

	w1 = hh * hw
	w2 = hh * lw
	w3 = lh * hw
	w4 = lh * lw

	interp_val = v1 * w1 + w2 * v2 + w3 * v3 + w4 * v4

	if dim_input == 2:
		return interp_val.reshape(q_h, q_w)
	return interp_val

def Test_script(I, E):
    test_pass = True

    # E should be 2D matrix
    if E.ndim != 2:
      print('ERROR: Incorrect Edge map dimension! \n')
      print(E.ndim)
      test_pass = False
    # end if

    # E should have same size with original image
    nr_I, nc_I = I.shape[0], I.shape[1]
    nr_E, nc_E = E.shape[0], E.shape[1]

    if nr_I != nr_E or nc_I != nc_E:
      print('ERROR: Edge map size has changed during operations! \n')
      test_pass = False
    # end if

    # E should be a binary matrix so that element should be either 1 or 0
    numEle = E.size
    numOnes, numZeros = E[E == 1].size, E[E == 0].size

    if numEle != (numOnes + numZeros):
      print('ERROR: Edge map is not binary one! \n')
      test_pass = False
    # end if

    if test_pass:
      print('Shape Test Passed! \n')
    else:
      print('Shape Test Failed! \n')

    return test_pass

'''
  Derivatives visualzation function
'''
def visDerivatives(I_gray, Mag, Magx, Magy):
    fig, (Ax0, Ax1, Ax2, Ax3) = plt.subplots(1, 4, figsize = (20, 8))

    Ax0.imshow(Mag, cmap='gray', interpolation='nearest')
    Ax0.axis('off')
    Ax0.set_title('Gradient Magnitude')

    Ax1.imshow(Magx, cmap='gray', interpolation='nearest')
    Ax1.axis('off')
    Ax1.set_title('Gradient Magnitude (x axis)')
    
    Ax2.imshow(Magy, cmap='gray', interpolation='nearest')
    Ax2.axis('off')
    Ax2.set_title('Gradient Magnitude (y axis)')

    # plot gradient orientation
    Mag_vec = Mag.transpose().reshape(1, Mag.shape[0] * Mag.shape[1]) 
    hist, bin_edge = np.histogram(Mag_vec.transpose(), 100)

    ind_array = np.array(np.where( (np.cumsum(hist).astype(float) / hist.sum()) < 0.95))
    thr = bin_edge[ind_array[0, -1]]

    ind_remove = np.where(np.abs(Mag) < thr)
    Magx[ind_remove] = 0
    Magy[ind_remove] = 0

    X, Y = np.meshgrid(np.arange(0, Mag.shape[1], 1), np.arange(0, Mag.shape[0], 1))
    Ori = np.arctan2(Magy, Magx)
    ori = Ax3.imshow(Ori, cmap='hsv')
    Ax3.axis('off')
    Ax3.set_title('Gradient Orientation')
    fig.colorbar(ori, ax=Ax3, )
    


'''
  Edge detection result visualization function
'''
def visCannyEdge(Im_raw, M, E):
    # plot image
    fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize = (12, 12))

    # plot original image
    ax0.imshow(Im_raw)
    ax0.axis("off")
    ax0.set_title('Raw image')

    # plot edge detection result
    ax1.imshow(M, cmap='gray', interpolation='nearest')
    ax1.axis("off")
    ax1.set_title('Non-Max Suppression Result')

    # plot original image
    ax2.imshow(E, cmap='gray', interpolation='nearest')
    ax2.axis("off") 
    ax2.set_title('Canny Edge Detection')

"""# Functions"""

'''
  Convert RGB image to gray one manually
  - Input I_rgb: 3-dimensional rgb image
  - Output I_gray: 2-dimensional grayscale image
'''
def rgb2gray(I_rgb):
    r, g, b = I_rgb[:, :, 0], I_rgb[:, :, 1], I_rgb[:, :, 2]
    I_gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return I_gray

def findDerivatives(I_gray):
    '''
    File clarification:
        Compute gradient information of the input grayscale image
        - Input I_gray: H x W matrix as image
        - Output Mag: H x W matrix represents the magnitude of derivatives
        - Output Magx: H x W matrix represents the magnitude of derivatives along x-axis
        - Output Magy: H x W matrix represents the magnitude of derivatives along y-axis
        - Output Ori: H x W matrix represents the orientation of derivatives
    '''
    # TODO: complete function
    # G = ... # array / 159 insteas of 1/159 * array
    Gauss_array = np.array([[2,4,5,4,2],
                    [4,9,12,9,4],
                    [5,12,15,12,5],
                    [4,9,12,9,4],
                    [2,4,5,4,2]])
    G = Gauss_array/159

    # dx = ...
    dx = np.array([[1, 0, -1],
                  [2, 0, -2],
                  [1, 0, -1]])
    # dy = ...
    dy = np.array([[1, 2, 1],
                  [0, 0, 0],
                  [-1, -2, -1]])

    # Convolution of image with the Gaussian Kernel (Smoothing kernel)
    # Gx = G conv dx
    Gx = signal.convolve2d(G, dx, 'same')
    # Gy = G conv dy
    Gy = signal.convolve2d(G, dy, 'same')

    # Convolution of image with Gx and Gy
    Ix = signal.convolve2d(I_gray, Gx, 'same')
    Iy = signal.convolve2d(I_gray, Gy, 'same')

    # Magx = I_gray conv Gx # This is technically the same as I_gray conv G conv dx
    #Magx = np.absolute(Ix) # Takes the magnitude of the gradient in the x direction
    #Magy = np.absolute(Iy) # Takes the magnitude of the gradient in the y direction
    
    Magx = Ix
    Magy = Iy

    # Mag = f(Magx, Magy)
    Mag = np.sqrt(Ix**2 + Iy**2)
    #Mag = np.sqrt(Magx^2 + Magy^2)
    #Mag = np.absolute(Magx, Magy)
    
    # Find the orientation of the gradient vector
    Ori = np.arctan2(Iy, Ix) # Here the orientation is in RADIANS
    #print(Ori)


    return Mag, Magx, Magy, Ori

## Test ##

# you may need to change the path to I1.jpg under Images folder
I = plt.imread('Images/I1.jpg')
#plt.imshow(I)
Mag, Magx, Magy, Ori = findDerivatives(I)
assert np.allclose(Mag, np.load('Mag.npy'))
assert np.allclose(Magx, np.load('Magx.npy'))
assert np.allclose(Magy, np.load('Magy.npy'))
assert np.allclose(Ori, np.load('Ori.npy'))

def nonMaxSup(Mag, Ori):
    '''
    File clarification:
        Find local maximum edge pixel using NMS along the line of the gradient
        - Input Mag: H x W matrix represents the magnitude of derivatives
        - Input Ori: H x W matrix represents the orientation of derivatives
        - Output M: H x W binary matrix represents the edge map after non-maximum suppression
    '''

    nr, nc = Mag.shape[0] + 2, Mag.shape[1] + 2 # add +2 to account for the future padding that avoids issues with edge cases (pixels outside of the actual matrix)

    # Make the meshgrid
    xx, yy = np.meshgrid(np.arange(nc), np.arange(nr))

    # Get the shifted meshgrids to avoid looping (basically rearranges indices to do parallel computations)
    # This can also be thought of as a rotation of the meshgrid according to the gradient orientation
    # We must also clip to account for the border cases
    Mag_pad = np.pad(Mag, 1, mode='constant') # add padding to avoid edge cases
    Ori_pad = np.pad(Ori, 1, mode='constant') # add padding to avoid edge cases

    x_pos = (xx + np.cos(Ori_pad)).clip(0, nc - 1) # retrieves the neighbour to the right of the current pixel  
    y_pos = (yy + np.sin(Ori_pad)).clip(0, nr - 1) # retrieves the nieghbour below (positive direction of y) the current pixel

    x_neg = (xx - np.cos(Ori_pad)).clip(0, nc - 1) # retrieves the neighbour to the left of the current pixel
    y_neg = (yy - np.sin(Ori_pad)).clip(0, nr - 1) # retrieves the neighbour above (negative direction of y) the current pixel

    # Obtaining neighbours in the directions of the orientation

    neighbor1 = interp2(Mag_pad, x_pos, y_pos) # Positive Gradient Direction
    neighbor2 = interp2(Mag_pad, x_neg, y_neg) # Negative Gradient Direction

    out_x = (x_pos )

    # Computing binary edge map after non-maximum suppression
    M =  np.zeros((Mag_pad.shape[0], Mag_pad.shape[1]), dtype = bool) # set up initial binary edge map
    
    M[np.logical_and(Mag_pad >= neighbor1, Mag_pad >= neighbor2)] = True # Check if the neighbors are less than current pixel. If tru add to binary edge map

    M = M[1:-1, 1:-1] # We no longer care about the padding

    #plt.imsave("NMS_TEST.png", M)
    return M

## Test ##
Mag = np.array([[0, 2, 12, 16],
                [4, 9, 11, 8],
                [7, 17, 12, 9],
                [0, 19, 21, 17]])
Ori = np.array([[np.pi/2, np.pi/4, 0, np.pi/4],
                [np.pi/4, np.pi/4, np.pi/4, np.pi/2],
                [np.pi/4, 0, np.pi/2, np.pi/4],
                [np.pi/2, np.pi/4, np.pi/2, np.pi/4]])
res = np.array([[False, False, False,  True],
       [False, False,  True, False],
       [False,  True, False, False],
       [False,  True,  True,  True]])
M = nonMaxSup(Mag, Ori)
assert M.dtype == bool
assert M.shape == Mag.shape
assert np.allclose(M, res)

def edgeLink(M, Mag, Ori, low, high):
    '''
    File clarification:
        Use hysteresis to link edges based on high and low magnitude thresholds
        - Input M: H x W logical map after non-max suppression
        - Input Mag: H x W matrix represents the magnitude of gradient
        - Input Ori: H x W matrix represents the orientation of gradient
        - Input low, high: low and high thresholds 
        - Output E: H x W binary matrix represents the final canny edge detection map
    '''

    # Pad all inputs with 0's to avoid border values having nonsensical results
    M = np.pad(M, 1, constant_values=False, mode='constant')
    Mag = np.pad(Mag, 1, constant_values=0, mode='constant')
    Mag[M == False] = 0 # Set supressed cells to magnitude 0
    Ori = np.pad(Ori, 1, constant_values=0, mode='constant')

    # Generate Strong Edge Map & Weak Edge Map based on low & high threshold values
    M[Mag < low] = False  # Edges below low threshold are removed
    M_strong = np.logical_and(M, Mag >= high) # Strong map is where pixels exceed high threshold
    M_diff = np.logical_and(M, np.logical_and(Mag >= low, np.logical_not(M_strong))) # The difference map: where pixels exceed the low threshold but are less than the high
    E = M_strong  # Initializing the final edge map with the strong edge map

    # Make the meshgrid
    x, y = np.meshgrid(np.arange(E.shape[1]), np.arange(E.shape[0]))
    Edge_Ori = Ori + np.pi/2
    x_pos = (x + np.cos(Edge_Ori))  # Neighbor x in the positive edge direction (pi/2 difference from gradient, AKA Ori)
    x_neg = (x - np.cos(Edge_Ori))  # Neighbor x in the negative edge direction (pi/2 difference from gradient, AKA Ori)
    y_pos = (y + np.sin(Edge_Ori))  # Neighbor y in the positive edge direction (pi/2 difference from gradient, AKA Ori)
    y_neg = (y - np.sin(Edge_Ori))  # Neighbor y in the negative edge direction (pi/2 difference from gradient, AKA Ori)


    while 1:    # An infinite while loop is used to perform multiple iterations of hysteresis
                # Runs while there are still weak edges connected to strong edges and are not yet converted to final map
        
        # Find out if your neighbor is in the strong edge map when the current pixel is uncertain
        neighbor1 = interp2(Mag, x_pos, y_pos) # Find the magnitude of neighbor pixel #1
        neighbor2 = interp2(Mag, x_neg, y_neg) # Find the magnitude of neighbor pixel #2
        neighbor_mapA = np.logical_or(neighbor1 >= high, neighbor2 >= high) # Check where either pixel is greater than the high threshold
        neighbor_map = np.logical_and(neighbor_mapA, M_diff) # check if the pixel with neighbors is also in the uncertain map. These are pixels that are connected to strong edges

        # Update the magnitude map so the future interpolations don't result in a broken edge
        Mag[neighbor_map] = np.maximum(neighbor1, neighbor2)[neighbor_map]# Have to update the magnitude of the pixel added to the edge map to the value of its highest neighbor

        # If a weak edge has a neighbor in the strong edge map (whether initially strong or weak), then add it to the new map. Keep existing map
        E_next = np.logical_or(E, neighbor_map)

        if np.all(E == E_next): # If there are no additions to the new edge map, there never will be
            E = E[1:-1, 1:-1] # Don't forget to take off the padding
            break

        E = E_next # update the existing final edge map

    return E

## Test ##
M = np.array([[True, False, True,  True],
              [False, True,  True, True],
              [True,  True, False, False],
              [False,  True,  True,  True]])
Mag = np.array([[12, 9, 14, 16],
                [4, 11, 40, 18],
                [13, 12, 30, 15],
                [28, 15, 21, 8]])
Ori = np.array([[np.pi/2, np.pi/4, 0, np.pi/4],
                [np.pi/4, np.pi/4, np.pi/4, np.pi/2],
                [np.pi/4, 0, np.pi/2, np.pi/4],
                [np.pi/2, np.pi/4, np.pi/2, np.pi/4]])
res = np.array([[False, False,  True,  True],
       [False,  True,  True,  True],
       [ True,  True, False, False],
       [False, False,  True, False]])
low, high = 10, 20
E = edgeLink(M, Mag, Ori, low, high)
assert E.dtype == bool
assert E.shape == Mag.shape
assert np.allclose(E, res)

def cannyEdge(I, low, high):
    # convert RGB image to gray color space
    im_gray = rgb2gray(I)

    Mag, Magx, Magy, Ori = findDerivatives(im_gray)
    M = nonMaxSup(Mag, Ori)
    E = edgeLink(M, Mag, Ori, low, high)

    # only when test passed that can show all results
    if Test_script(im_gray, E):
        # visualization results
        visDerivatives(im_gray, Mag, Magx, Magy)
        visCannyEdge(I, M, E)

        plt.show()

    return E

"""## Simple image test cases
First, let's try to detect edges in two simple images.

![checkerboard.jpg](Test_Images/rotated_checkerboard.jpg)

For the rotated checkerboard, We should be able to get edges in both directions.

![checkerboard_res.jpg](Test_Images/rotated_checkerboard_Result.png)

![coins.png](Test_Images/coins.png) 

For coins, we should be able to detect circles.

![coins.png](Test_Images/coins_Result.png) 
"""

# tuning threshold for simple test images
image_folder = "Test_Images"
save_folder = "Results" # need to create this folder in the drive
filename='coins.png' # TODO: change image name 
I = np.array(Image.open(os.path.join(image_folder, filename)).convert('RGB'))
low, high = 28, 70
E = cannyEdge(I, low, high)
pil_image = Image.fromarray(E.astype(np.uint8) * 255).convert('L')
# check the result in the folder
pil_image.save(os.path.join(save_folder, str(low) + "_" + str(high) + "_" + "{}_Result.png".format(filename.split(".")[0])))

"""## Tune the threshold for each images under "Image" folder"""

# list all image names
os.listdir('Images')

# tuning threshold for a single image
image_folder = "Images"
save_folder = "Results" # need to create this folder in the drive
filename='118035.jpg' # TODO: change image name 
I = np.array(Image.open(os.path.join(image_folder, filename)).convert('RGB'))
for x in range(0, 100, 5):
  high = x
  low = int(0.4 * high)
  E = cannyEdge(I, low, high)
  pil_image = Image.fromarray(E.astype(np.uint8) * 255).convert('L')
  # check the result in the folder
  pil_image.save(os.path.join(save_folder, str(low) + "_" + str(high) + "_" + "{}_Result.png".format(filename.split(".")[0])))

"""# Fill in all tuned threshold to generate edge detection results

"""

# keep results for all images
image_folder = "Images"
save_folder = "Results/optimal"

# fill in the threshold (low, high) you have tuned in the cell above 
thresh_dict = {'118035.jpg': (2, 5),
                '135069.jpg': (10, 25),
                '16068.jpg': (20, 50),
                '189080.jpg': (12, 30),
                '201080.jpg': (16, 40),
                '21077.jpg': (20, 50),
                '22013.jpg': (22, 55),
                '3096.jpg': (16, 40),
                '48017.jpg': (12, 30),
                '55067.jpg': (4, 10),
                '86000.jpg': (16, 40),
                'I1.jpg': (8, 20)}
# generate results one by one
for filename in os.listdir(image_folder):
    # read in image 
    im_path = os.path.join(image_folder, filename)
    I = np.array(Image.open(im_path).convert('RGB'))

    low, high = thresh_dict[filename]
    E = cannyEdge(I, low, high)

    pil_image = Image.fromarray(E.astype(np.uint8) * 255).convert('L')

    pil_image.save(os.path.join(save_folder, "{}_Result.png".format(filename.split(".")[0])))

