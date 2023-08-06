#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import numpy as np

from gvxrPython3 import gvxr
import argparse


parser = argparse.ArgumentParser(description='Compute the L-buffer of a colygon mesh.')

parser.add_argument('--plot',    dest='plot', action='store_true',  help='Turn on the display fo the L-buffer image (default: False)')
parser.add_argument('--no-plot', dest='plot', action='store_false', help='Turn off the display of the L-buffer image  (default: True)')
parser.add_argument('--vis',     dest='vis',  action='store_true',  help='Turn on the 3-D interactive visualisatin of the simulation (default: False)')
parser.add_argument('--no-vis',  dest='vis',  action='store_false', help='Turn off the 3-D interactive visualisatin of the simulation (default: True)')

parser.add_argument('--gpu_artefact_filtering',    dest="gpu_artefact_filtering", action='store_true',  help='Turn on artefact filtering on GPU (default: False)')
parser.add_argument('--no-gpu_artefact_filtering', dest="gpu_artefact_filtering", action='store_false', help='Turn off artefact filtering on GPU (default: True)')
parser.add_argument('--cpu_artefact_filtering',    dest="cpu_artefact_filtering", action='store_true',  help='Turn on artefact filtering on CPU (default: False)')
parser.add_argument('--no-cpu_artefact_filtering', dest="cpu_artefact_filtering", action='store_false', help='Turn off artefact filtering on CPU (default: True)')

parser.add_argument('--input_mesh',   type=str, help='Name of the file containing the polygon mesh')
parser.add_argument('--mesh_unit',    type=str, help='Unit of length (for the polygon mesh): um, mm, cm, dm, m, dam, hm, or km (default: mm)')
parser.add_argument('--output_image', type=str, help='Name of the file where the L-buffer will be saved')
parser.add_argument('--center',       dest='center', action='store_true',  help='Center the polygon mesh on (0.0, 0.0, 0.0) (default: False)')
parser.add_argument('--centre',       dest='center', action='store_true',  help='Centre the polygon mesh on (0.0, 0.0, 0.0) (default: False)')
parser.add_argument('--no-center',    dest='center', action='store_false', help='Do not center the polygon mesh on (0.0, 0.0, 0.0) (default: True)')
parser.add_argument('--no-centre',    dest='center', action='store_false', help='Do not centre the polygon mesh on (0.0, 0.0, 0.0) (default: True)')

parser.add_argument('--point_source',  dest='orthographic', action='store_false', help='Use a point source (perspective projection) (default: True)')
parser.add_argument('--parallel_beam', dest='orthographic', action='store_true',  help='Use a parallel beam (orthographic projection), i.e. mimics a source extremely far away from the detector, e.g. as with synchrotron radiation (default: False)')

parser.add_argument('--source_position',      type=float, nargs=3, help='Source position')
parser.add_argument('--source_position_unit', type=str,            help='Unit of length (for the source position): um, mm, cm, dm, m, dam, hm, or km (default: mm)')

parser.add_argument('--detector_position',      type=float, nargs=3, help='Source position')
parser.add_argument('--detector_position_unit', type=str,          help='Unit of length (for the detector position): um, mm, cm, dm, m, dam, hm, or km (default: mm)')
parser.add_argument('--detector_up_vector',     type=float, nargs=3, help='Up vector of the detector')

parser.add_argument('--nb_of_pixels',  type=int, nargs=2, help='Number of pixels in the detector')
parser.add_argument('--pixel_size',    type=float, nargs=2, help='Pixel size')
parser.add_argument('--pixel_unit',    metavar='P', type=str, help='Unit of length (for a pixel): um, mm, cm, dm, m, dam, hm, or km')

parser.set_defaults(gpu_artefact_filtering=False)
parser.set_defaults(cpu_artefact_filtering=False)
parser.set_defaults(plot=False)
parser.set_defaults(vis=False)
parser.set_defaults(center=False)
parser.set_defaults(orthographic=False)
parser.set_defaults(mesh_unit="mm")
parser.set_defaults(detector_position_unit="mm")
parser.set_defaults(source_position_unit="mm")

args = parser.parse_args()    

if args.gpu_artefact_filtering and args.cpu_artefact_filtering:
	print("Can't use artefact filtering on both GPU and CPU");
	exit();
	
if not args.input_mesh:
	print("No input polygon mesh file name given");
	exit();
	
if not args.mesh_unit:
	print("No unit of length given for the polygon mesh");
	exit();
	
if not args.detector_position_unit:
	print("No unit of length given for the detector position");
	exit();
	
if not args.source_position_unit:
	print("No unit of length given for the source position");
	exit();
	
if not args.output_image:
	print("No output image file name given");
	exit();

if not args.source_position:
	print("No source position given");
	exit();

if not args.detector_position:
	print("No detector position given");
	exit();	
	
if not args.detector_up_vector:
	print("No up vector of the detector given");
	exit();	
	
if not args.nb_of_pixels:
	print("No number of pixels of the detector given");
	exit();

if not args.pixel_size:
	print("No pixel size given");
	exit();

if not args.pixel_unit:
	print("No unit of length given for a pixel of the detector");
	exit();

print("Use artefact filtering on GPU:\n", gvxr.enableArtefactFilteringOnGPU);
print("Use artefact filtering on CPU:\n", gvxr.enableArtefactFilteringOnCPU);
print("Input polygon mesh file name given:\t", args.input_mesh);
print("Unit for the polygon mesh given:\t", args.mesh_unit);
print("Centre the polygon mesh:\t", args.center);
print("Output image file name:\t", args.output_image);
print("Source position:\t", args.source_position, args.source_position_unit);
print("Detector position:\t", args.detector_position, args.detector_position_unit);
print("Detector up vector:\t", args.detector_up_vector);
print("Detector size (in pixels):\t", args.nb_of_pixels);
print("Pixel size given:\t", args.pixel_size);
print("Unit for a pixel of the detector given:\t", args.pixel_unit);

# Create an OpenGL context
#print("Create an OpenGL context")

if args.vis:
	gvxr.createWindow();
	gvxr.setWindowSize(512, 512);
else:
	gvxr.createOpenGLContext();
	gvxr.setWindowSize(1, 1);

# Set up the beam
#print("Set up the beam")
gvxr.setSourcePosition(args.source_position[0], args.source_position[1], args.source_position[2], args.source_position_unit);

if args.orthographic:
	gvxr.useParallelBeam();
else:
	gvxr.usePointSource();

gvxr.setMonoChromatic(0.08, "MeV", 1000);

# Set up the detector
#print("Set up the detector");
gvxr.setDetectorPosition(args.detector_position[0], args.detector_position[1], args.detector_position[2], args.detector_position_unit);
gvxr.setDetectorUpVector(args.detector_up_vector[0], args.detector_up_vector[1], args.detector_up_vector[2]);
gvxr.setDetectorNumberOfPixels(args.nb_of_pixels[0], args.nb_of_pixels[1]);
gvxr.setDetectorPixelSize(args.pixel_size[0], args.pixel_size[1], args.pixel_unit);

# Load the data
#print("Load the data");
gvxr.loadSceneGraph(args.input_mesh, args.mesh_unit);

for label in gvxr.getMeshLabelSet():
	if args.center:
		#print("Move ", label, " to the centre");
		gvxr.moveToCentre(label);

	#print("Set ", label, "'s Hounsfield unit");
	#gvxr.setHU(label, 1000)


# Compute an X-ray image
#print("Compute an X-ray image");
gvxr.disableArtefactFiltering();

if args.gpu_artefact_filtering:
	gvxr.enableArtefactFilteringOnGPU();

if args.cpu_artefact_filtering:
	gvxr.enableArtefactFilteringOnCPU();

x_ray_image = gvxr.computeXRayImage();
l_buffer = gvxr.getLastLBuffer();

# Save the last image into a file
#print("Save the last L-buffer into an image file");
gvxr.saveLastLBuffer(args.output_image);

if args.plot:
	# Retrieve the image in Numpy's 2D array format
	np_image = np.array(l_buffer);

	# Normalise the image between 0 and 255 (this is for PIL)
	#np_normalised_image = (255 * (np_image-np_image.min())/np_image.max()).astype(np.int8);

	# Convert the Numpy array into a PIL image
	#img = Image.fromarray(np_normalised_image.astype(np.ubyte));

	# Save the PIL image
	#img.save('my.png')

	# Show the image
	#img.show()

	# Display the image with Matplotlib
	fig = plt.figure(0);
	ax = plt.imshow(np_image, cmap="gray");
	cbar = fig.colorbar(ax, orientation='horizontal')
	plt.title("L-buffer of " + args.input_mesh);

	plt.show();

# Display the 3D scene (no event loop)
gvxr.displayScene();

if args.vis:


	# Display the 3D scene (no event loop)
	# Run an interactive loop 
	# (can rotate the 3D scene and zoom-in)
	# Keys are:
	# Q/Escape: to quit the event loop (does not close the window)
	# B: display/hide the X-ray beam
	# W: display the polygon meshes in solid or wireframe
	# N: display the X-ray image in negative or positive
	# H: display/hide the X-ray detector
	gvxr.renderLoop();

exit();





