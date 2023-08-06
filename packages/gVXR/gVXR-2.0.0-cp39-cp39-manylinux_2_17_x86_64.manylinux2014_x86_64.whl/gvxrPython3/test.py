#!/usr/bin/env python3

# Import packages
import os
import numpy as np # Who does not use Numpy?

import matplotlib # To plot images
import matplotlib.pyplot as plt # Plotting
from matplotlib.colors import LogNorm # Look up table
from matplotlib.colors import PowerNorm # Look up table

font = {'family' : 'serif',
         'size'   : 15
       }
matplotlib.rc('font', **font)

# Uncomment the line below to use LaTeX fonts
# matplotlib.rc('text', usetex=True)

from tifffile import imwrite # Write TIFF files

from gvxrPython3 import gvxr # Simulate X-ray images

# Create an OpenGL context
print("Create an OpenGL context")
gvxr.createOpenGLContext();

# Set up a monochromatic source
print("Set up the beam")
gvxr.setSourcePosition(-40.0,  0.0, 0.0, "cm");
gvxr.usePointSource();
#  For a parallel source, use gvxr.useParallelBeam();

# 1000 phothons of 80 keV (i.e. 0.08 MeV) per ray
gvxr.setMonoChromatic(0.08, "MeV", 1000);
# The following is equivalent: gvxr.setMonoChromatic(80, "keV", 1000);

# Set up the detector
print("Set up the detector");
gvxr.setDetectorPosition(10.0, 0.0, 0.0, "cm");
gvxr.setDetectorUpVector(0, 0, -1);
gvxr.setDetectorNumberOfPixels(640, 320);
gvxr.setDetectorPixelSize(0.5, 0.5, "mm");

# Locate the sample STL file from the package directory
path = os.path.dirname(gvxr.__file__)
fname = path + "/welsh-dragon-small.stl"

# Load the sample data
if not os.path.exists(fname):
    raise IOError(fname)

print("Load the mesh data from", fname);
gvxr.loadMeshFile("Dragon", fname, "mm")

print("Move ", "Dragon", " to the centre");
gvxr.moveToCentre("Dragon");

# Material properties
print("Set ", "Dragon", "'s material");

# Iron (Z number: 26, symbol: Fe)
gvxr.setElement("Dragon", 26)
gvxr.setElement("Dragon", "Fe")

# Liquid water
gvxr.setCompound("Dragon", "H2O")
gvxr.setDensity("Dragon", 1.0, "g/cm3")
gvxr.setDensity("Dragon", 1.0, "g.cm-3")

# Titanium Aluminum Vanadium Alloy
gvxr.setMixture("Dragon", "Ti90Al6V4")
gvxr.setMixture("Dragon", [22, 13, 23], [0.9, 0.06, 0.04])
# gvxr.setMixture("Dragon", ["Ti", "Al", "V"], [0.9, 0.06, 0.04]) # Not yet implemented
gvxr.setDensity("Dragon", 4.43, "g/cm3")
gvxr.setDensity("Dragon", 4.43, "g.cm-3")

# Compute an X-ray image
# We convert the array in a Numpy structure and store the data using single-precision floating-point numbers.
print("Compute an X-ray image");
x_ray_image = np.array(gvxr.computeXRayImage()).astype(np.single)

# Update the visualisation window
gvxr.displayScene()

# Create the output directory if needed
if not os.path.exists("output_data"):
    os.mkdir("output_data")

# Save the X-ray image in a TIFF file and store the data using single-precision floating-point numbers.
gvxr.saveLastXRayImage('output_data/raw_x-ray_image-02.tif')

# The line below will also works
# imwrite('output_data/raw_x-ray_image-02.tif', x_ray_image)

# Save the L-buffer
gvxr.saveLastLBuffer('output_data/lbuffer-02.tif');

# Display the X-ray image
# using a linear colour scale
plt.figure(figsize=(10, 5))
plt.title("Image simulated using gVirtualXray\nusing a linear colour scale")
plt.imshow(x_ray_image, cmap="gray")
plt.colorbar(orientation='vertical');
plt.show()

# using a logarithmic colour scale
plt.figure(figsize=(10, 5))
plt.title("Image simulated using gVirtualXray\nusing a logarithmic colour scale")
plt.imshow(x_ray_image, cmap="gray", norm=LogNorm(vmin=x_ray_image.min(), vmax=x_ray_image.max()))
plt.colorbar(orientation='vertical');
plt.show()

# using a Power-law colour scale (gamma=0.5)
plt.figure(figsize=(10, 5))
plt.title("Image simulated using gVirtualXray\nusing a Power-law colour scale ($\gamma=0.5$)")
plt.imshow(x_ray_image, cmap="gray", norm=PowerNorm(gamma=1./2.))
plt.colorbar(orientation='vertical');
plt.show()

# Display the X-ray image and compare three different lookup tables
plt.figure(figsize=(17, 7.5))

plt.suptitle("Image simulated with gVirtualXray visualised", y=0.75)

plt.subplot(131)
plt.imshow(x_ray_image, cmap="gray")
plt.colorbar(orientation='horizontal')
plt.title("using a linear colour scale")

plt.subplot(132)
plt.imshow(x_ray_image, norm=LogNorm(), cmap="gray")
plt.colorbar(orientation='horizontal')
plt.title("using a logarithmic colour scale")

plt.subplot(133)
plt.imshow(x_ray_image, norm=PowerNorm(gamma=1./2.), cmap="gray")
plt.colorbar(orientation='horizontal');
plt.title("using a Power-law colour scale ($\gamma=0.5$)")

plt.tight_layout()

plt.savefig("output_data/projection-02.pdf", dpi=600);

# Change the sample's colour
# By default the object is white, which is not always pretty. Let's change it to purple.
red = 102 / 255
green = 51 / 255
blue = 153 / 255
gvxr.setColour("Dragon", red, green, blue, 1.0)

# This image can be used in a research paper to illustrate the simulation environment, in which case you may want to change the background colour to white with:
gvxr.setWindowBackGroundColour(1.0, 1.0, 1.0)

# Update the visualisation window
gvxr.displayScene()

# Take the screenshot and save it in a file
screenshot = gvxr.takeScreenshot()
plt.imsave("output_data/screenshot-02.png", np.array(screenshot))

# or display it using Matplotlib
plt.figure(figsize=(10, 10))
plt.imshow(screenshot)
plt.title("Screenshot of the X-ray simulation environment")
plt.axis('off');
plt.show()


# Interactive visualisation
# The user can rotate the 3D scene and zoom-in and -out in the visualisation window.

# - Keys are:
#     - Q/Escape: to quit the event loop (does not close the window)
#     - B: display/hide the X-ray beam
#     - W: display the polygon meshes in solid or wireframe
#     - N: display the X-ray image in negative or positive
#     - H: display/hide the X-ray detector
# - Mouse interactions:
#     - Zoom in/out: mouse wheel
#     - Rotation: Right mouse button down + move cursor```
gvxr.renderLoop()
