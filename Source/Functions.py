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


def box_blur(image, args):
    kernel_size = (args[0], args[1])
    manipulated_image = cv2.blur(image, kernel_size)
    return manipulated_image


def gaussian_blur(image, args):
    kernel_size = (args[0], args[1])
    sigma_x = args[2]
    manipulated_image = cv2.GaussianBlur(image, kernel_size, sigma_x, 0)
    return manipulated_image


def median_blur(image, args):
    kernel_size = args[0]
    manipulated_image = cv2.medianBlur(image, kernel_size)
    return manipulated_image


def bilateral_blur(image, args):
    kernel_size = args[0]
    sigma_color, sigma_space = args[1], args[2]
    manipulated_image = cv2.bilateralFilter(image, kernel_size, sigma_color, sigma_space)
    return manipulated_image


def de_blur(image):
    de_blur_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    manipulated_image = cv2.filter2D(image, -1, de_blur_kernel)
    return manipulated_image


def crop_image(image, args):
    x1, x2, y1, y2 = args
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    manipulated_image = image[y1:y2, x1:x2]
    return manipulated_image


def flip_image(image, args):  # Axis 0 = X, Axis 1 = Y
    axis_x, axis_y = args
    manipulated_image = np.copy(image)
    if axis_x == 1:
        manipulated_image = cv2.flip(manipulated_image, 0)
    if axis_y == 1:
        manipulated_image = cv2.flip(manipulated_image, 1)
    return manipulated_image


def mirror_image(image, args):  # Axis 0 = X, Axis 1 = Y
    axis_x, axis_y = args
    manipulated_image = np.copy(image)
    if axis_x == 1:
        flipped_image = cv2.flip(manipulated_image, 0)
        manipulated_image = np.vstack((manipulated_image, flipped_image))
    if axis_y == 1:
        flipped_image = cv2.flip(manipulated_image, 1)
        manipulated_image = np.hstack((manipulated_image, flipped_image))
    return manipulated_image


def rotate_image(image, args):
    angle, image_center_x, image_center_y = args
    rot_mat = cv2.getRotationMatrix2D((image_center_x, image_center_y), angle, 1.0)
    manipulated_image = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return manipulated_image


def reverse_image(image):
    manipulated_image = cv2.bitwise_not(image)
    return manipulated_image


def grayscale_image(image):
    manipulated_image = np.copy(image)
    if len(image.shape) > 2:
        manipulated_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return manipulated_image


def change_color_balance(image, args):
    channel, amount = args
    manipulated_image = np.copy(image)
    manipulated_image = cv2.cvtColor(manipulated_image, cv2.COLOR_BGR2RGB)
    manipulated_image[:, :, channel] = np.clip(manipulated_image[:, :, channel] + amount, 0, 255)
    print(manipulated_image[:, :, channel])
    manipulated_image = cv2.cvtColor(manipulated_image, cv2.COLOR_RGB2BGR)
    return manipulated_image


def change_contrast_and_brightness(image, args):
    alpha, beta, gamma = args
    look_up_table1 = np.empty((1, 256), np.uint8)
    look_up_table2 = np.empty((1, 256), np.uint8)
    for i in range(256):
        look_up_table1[0][i] = np.clip(alpha * i + beta, 0, 255)
        look_up_table2[0][i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    manipulated_image = cv2.LUT(cv2.LUT(image, look_up_table1), look_up_table2)
    return manipulated_image


def salt_and_pepper_noise(image, args):
    salt_vs_pepper, amount = args
    salt_vs_pepper, amount = salt_vs_pepper / 100, amount / 100
    noise_image = skimage.util.random_noise(image=image, mode='s&p', salt_vs_pepper=salt_vs_pepper, amount=amount)
    manipulated_image = np.array(255 * noise_image, dtype='uint8')
    return manipulated_image


def gaussian_noise(image, args):
    mean, var = args
    mean, var = mean / 100, var / 100
    noise_image = skimage.util.random_noise(image=image, mode='gaussian', mean=mean, var=var)
    manipulated_image = np.array(255 * noise_image, dtype='uint8')
    return manipulated_image


def poisson_noise(image):
    noise_image = skimage.util.random_noise(image=image, mode='poisson')
    manipulated_image = np.array(255 * noise_image, dtype='uint8')
    return manipulated_image


def speckle_noise(image, args):
    mean, var = args
    mean, var = mean / 100, var / 100
    noise_image = skimage.util.random_noise(image=image, mode='speckle', mean=mean, var=var)
    manipulated_image = np.array(255 * noise_image, dtype='uint8')
    return manipulated_image


def naive_edge_detect(image):
    grayscaled_image = grayscale_image(image)
    detection_kernel = np.array([[-1, -1, -1], [-1, 7, -1], [-1, -1, -1]])
    manipulated_image = cv2.filter2D(grayscaled_image, -1, detection_kernel)
    return manipulated_image


def sobel_edge_detect(image, args):
    kernel_size, dx, dy = args
    grayscaled_image = grayscale_image(image)
    manipulated_image = cv2.Sobel(grayscaled_image, ksize=kernel_size, dx=dx, dy=dy, ddepth=cv2.CV_8U)
    return manipulated_image


def canny_edge_detect(image, args):
    t1, t2 = args
    grayscaled_image = grayscale_image(image)
    manipulated_image = cv2.Canny(grayscaled_image, t1, t2)
    return manipulated_image
