import argparse
import os

import cv2
import numpy
import PIL.ImageOps
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
tessdata_dir_config = r'--tessdata-dir "D:/proyectos/txt_img/tessdata-main"'
tess_config = r"-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMOPQRSTUVWXYZ"

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to input image to be OCR'd")
args = vars(ap.parse_args())

# load the example image and convert it to RGB, invert it and adjust brightness

image = Image.open(args["image"]).convert("RGB")
# image = PIL.ImageOps.invert(image)
# image = ImageEnhance.Brightness(image)
# image = image.enhance(10)
# image = image.filter(ImageFilter.MedianFilter()) # ReduceNoise()
# image = image.filter(ImageFilter.Kernel((3,3), (-1,-1,-1,-1,8,-1,-1,-1,-1))) # Morphology()
# image = ImageOps.invert(image) # Negate()

imageArray = numpy.array(image)
imageArray = imageArray[:, :, ::-1].copy()
imageArray = cv2.bitwise_not(imageArray)

# Redimensionar a 150%
scale_percent = 150  # porcentaje del tamaño original
width = int(imageArray.shape[1] * scale_percent / 100)
height = int(imageArray.shape[0] * scale_percent / 100)
dim = (width, height)
imageArray = cv2.resize(imageArray, dim, interpolation=cv2.INTER_AREA)

# Convertir a blanco y negro
imageArray = cv2.cvtColor(imageArray, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imageArray, 127, 255, cv2.THRESH_BINARY)

# image = ImageOps.posterize(image, 5) # Threshold()

text = pytesseract.image_to_string(thresh, config=tessdata_dir_config)
print(f"The text is: {text}")

# show the output images
cv2.imshow("Image", thresh)
cv2.waitKey(0)
