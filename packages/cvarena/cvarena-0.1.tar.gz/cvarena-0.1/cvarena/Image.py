import cv2
import numpy as np


def avgColor(img):
    try:
        average_color_row = np.average(img, axis=0)
        average_color = np.average(average_color_row, axis=0)
        average_color[0], average_color[1], average_color[2] = average_color[2], average_color[1], average_color[0]
        return average_color
    except Exception as e:
        error_string = "Could not find average color." + "\n" + "Error: " + str(e) + "\n\n" + "ERROR #001"
        raise Exception(error_string)


def RGBTOBGR(img):
    try:
        image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return image
    except Exception as e:
        error_string = "Could not convert the Image from RGB to BGR" + "\n" + "Error: " + str(e) + "\n\n" + "ERROR #001"
        raise Exception(error_string)


def BGRTORGB(img):
    try:
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return image
    except Exception as e:
        error_string = "Could not convert the Image from BGR to RGB" + "\n" + "Error" + str(e) + "\n\n" + "ERROR #001"
        raise Exception(error_string)


def RGBTOGRAY(img):
    try:
        image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return image
    except Exception as e:
        error_string = "Could not convert the Image from RGB to GRAY" + "\n" + "Error" + str(e) + "\n\n" + "ERROR #001"
        raise Exception(error_string)


def BGRTOGRAY(img):
    try:
        image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return image
    except Exception as e:
        error_string = "Could not convert the Image from BGR to GRAY" + "\n" + "Error" + str(e) + "\n\n" + "ERROR #001"
        raise Exception(error_string)


def blurimage(img, threshold=10):
    try:
        th = 0
        if threshold % 2 == 0:
            th = threshold + 1
        else:
            th = threshold
        image = cv2.GaussianBlur(img, (th, th), 0)
        return image
    except Exception as e:
        if threshold.isdigit():
            error_string = "Could not blur image. Make sure threshold is int." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #002"
        else:
            error_string = "Could not blur image. Image not in the format." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #001"
        raise Exception(error_string)


def blurROI(img, cordinates, threshold=10):
    try:
        x, y, w, h = cordinates[0], cordinates[1], cordinates[2], cordinates[3]
        cropped_img = img[x:x + w, y:y + h]
    except Exception as e:
        error_string = "Could not blur ROI. Make sure cordinates are proper." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #003"
        raise Exception(error_string)
    try:
        th = 0
        if threshold % 2 == 0:
            th = threshold + 1
        else:
            th = threshold
        blur_roi = cv2.GaussianBlur(cropped_img, (th, th), 0)
        img[x:x + w, y:y + h] = blur_roi
        return img
    except Exception as e:
        if threshold.isdigit():
            error_string = "Could not blur ROI. Make sure threshold is int." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #002"
        else:
            error_string = "Could not blur ROI. Image not in the format." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #001"
        raise Exception(error_string)


def sharpImage(img):
    try:
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        image_sharp = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)
        return image_sharp
    except Exception as e:
        error_string = "Could not sharp the Image. Image not in the format." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #001"
        raise Exception(error_string)


def sharpROI(img, cordinates):
    try:
        x, y, w, h = cordinates[0], cordinates[1], cordinates[2], cordinates[3]
        roi_img = img[x:x + w, y:y + h]
    except Exception as e:
        error_string = "Could not sharp the ROI. Make sure cordinates are proper or Image not in the proper format" + "\n" + "Error" + str(e) + "\n\n" + "ERROR #003 / ERROR $001"
        raise Exception(error_string)
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    roi_sharp = cv2.filter2D(src=roi_img, ddepth=-1, kernel=kernel)
    img[x:x + w, y:y + h] = roi_sharp
    return img


def placeImage(background, foreground, cordinates):
    try:
        x, y, w, h = cordinates[0], cordinates[1], cordinates[2], cordinates[3]
        resolution = (h, w)
        foreground = resizeImage(foreground, resolution)
        background[x:x + w, y:y + h] = foreground
        return background
    except Exception as e:
        error_string = "Could not place the Image. Image not in the format or cordinates are not proper." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #001 / ERROR #003"
def solidimage(resolution, color):
    try:
        image = np.full((resolution[1], resolution[0], 3), 255, dtype=np.uint8)
    except Exception as e:
        error_string = "Could not create Solid Image. Make sure resolution is in proper format." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #004"
        raise Exception(error_string)
    try:
        image[:] = (color[0], color[1], color[2])
        return image
    except Exception as e:
        error_string = "Could not create Solid Image. Make sure color is in proper format." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #005"

def cropimage(img, cordinates):
    try:
        x, y, w, h = cordinates[0], cordinates[1], cordinates[2], cordinates[3]
        cropped_img = img[x:x + w, y:y + h]
        return cropped_img
    except Exception as e:
        error_string = "Could not Crop Image. Image not in proper format or Cordinates are not in proper format." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #001 / ERROR #003"
        raise Exception(error_string)


def resizeImage(img, resolution):
    try:
        return cv2.resize(img, resolution)
    except Exception as e:
        error_string = "Could not resize Image. Image not in proper format or Resolution is not in proper format." + "\n" + "Error" + str(e) + "\n\n" + "ERROR #001 / ERROR #004"
        raise Exception(error_string)