import numpy as np
import cv2.cv2 as cv2
import skimage


def load_image(image_path):
    image = cv2.imread(image_path)
    return image


def show_image(name, image):
    cv2.imshow(name, image)
    return image


def save_image(save_path, image):
    cv2.imwrite(save_path, image)
    return image


def box_blur(image, kernel_size):
    manipulated_image = cv2.blur(image, kernel_size)
    return manipulated_image


def gaussian_blur(image, kernel_size, sigma_x=0, sigma_y=0):
    manipulated_image = cv2.GaussianBlur(image, kernel_size, sigma_x, sigma_y)
    return manipulated_image


def median_blur(image, kernel_size):
    manipulated_image = cv2.medianBlur(image, kernel_size)
    return manipulated_image


def bilateral_blur(image, kernel_size, sigma_color=75, sigma_space=75):
    manipulated_image = cv2.bilateralFilter(image, kernel_size, sigma_color, sigma_space)
    return manipulated_image


def de_blur(image):
    de_blur_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    manipulated_image = cv2.filter2D(image, -1, de_blur_kernel)
    return manipulated_image


def grayscale_image(image):
    manipulated_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return manipulated_image


def crop_image(image, x1, y1, x2, y2):
    manipulated_image = image[y1:y2, x1:x2]
    return manipulated_image


def flip_image(image, axis):  # Axis 0 = X, Axis 1 = Y
    manipulated_image = cv2.flip(image, axis)
    return manipulated_image


def mirror_image(image, axis):  # Axis 0 = X, Axis 1 = Y
    flipped_image = flip_image(image, axis)
    manipulated_image = np.vstack((image, flipped_image)) if axis == 0 else np.hstack((image, flipped_image))
    return manipulated_image


def rotate_image(image, degree):
    degrees = {90: cv2.ROTATE_90_CLOCKWISE, 180: cv2.ROTATE_180, 270: cv2.ROTATE_90_COUNTERCLOCKWISE, -90: cv2.ROTATE_90_COUNTERCLOCKWISE}
    manipulated_image = cv2.rotate(image, degrees[degree])
    return manipulated_image


def reverse_image(image):
    manipulated_image = cv2.bitwise_not(image)
    return manipulated_image


def change_color_balance(image, channel, amount):
    manipulated_image = np.copy(image)
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            manipulated_image[y][x][channel] = np.clip(manipulated_image[y][x][channel] + amount, 0, 255)
    return manipulated_image


def change_contrast_and_brightness(image, alpha=1, beta=0, gamma=1):
    look_up_table1 = np.empty((1, 256), np.uint8)
    look_up_table2 = np.empty((1, 256), np.uint8)
    for i in range(256):
        look_up_table1[0][i] = np.clip(alpha * i + beta, 0, 255)
        look_up_table2[0][i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    manipulated_image = cv2.LUT(cv2.LUT(image, look_up_table1), look_up_table2)
    return manipulated_image


def gaussian_noise(image, mean=0, var=0.01):
    noise_image = skimage.util.random_noise(image=image, mode='gaussian', mean=mean, var=var)
    manipulated_image = np.array(255 * noise_image, dtype='uint8')
    return manipulated_image


def salt_and_pepper_noise(image, salt_vs_pepper=0.5, amount=0.05):
    noise_image = skimage.util.random_noise(image=image, mode='s&p', salt_vs_pepper=salt_vs_pepper, amount=amount)
    manipulated_image = np.array(255 * noise_image, dtype='uint8')
    return manipulated_image


def poisson_noise(image):
    noise_image = skimage.util.random_noise(image=image, mode='poisson')
    manipulated_image = np.array(255 * noise_image, dtype='uint8')
    return manipulated_image


def speckle_noise(image, mean=0, var=0.01):
    noise_image = skimage.util.random_noise(image=image, mode='speckle', mean=mean, var=var)
    manipulated_image = np.array(255 * noise_image, dtype='uint8')
    return manipulated_image


def naive_edge_detect(image):
    grayscaled_image = grayscale_image(image)
    detection_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
    manipulated_image = cv2.filter2D(grayscaled_image, -1, detection_kernel)
    return manipulated_image


def sobel_edge_detect(image, kernel_size, dx=0, dy=0):
    grayscaled_image = grayscale_image(image)
    manipulated_image = cv2.Sobel(grayscaled_image, ksize=kernel_size, dx=dx, dy=dy, ddepth=cv2.CV_8U)
    return manipulated_image


def canny_edge_detect(image, t1=100, t2=200):
    grayscaled_image = grayscale_image(image)
    manipulated_image = cv2.Canny(grayscaled_image, t1, t2)
    return manipulated_image
