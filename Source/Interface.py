import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfile
# import customtkinter
import cv2.cv2 as cv2
from PIL import ImageTk, Image

import Functions

# TODO revert changes to image


WIDTH = 1024  # TODO get those values dynamically
HEIGHT = 768
img_loaded = None  # Will pass this to edit functions to load it using cv2, TODO no global?


def init():  # Setting up the interface
    root = tk.Tk()
    root.title("Epic Image Editor")
    root.resizable(width=False, height=False)

    canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
    canvas.pack()

    # The frames that will hold the original and modified image
    img_orig = tk.Frame(root, borderwidth=1, relief="solid", height=512, width=512)
    img_orig.place(x=2, y=257)

    img_mod = tk.Frame(root, borderwidth=1, relief="solid", height=512, width=512)
    img_mod.place(x=514, y=257)

    # Setting up the File menu, can load/save images using it
    file_menu = tk.Menubutton(root, text="File")
    file_menu.pack()
    file_menu.place(x=0, y=0)
    file_menu.menu = tk.Menu(file_menu, tearoff=0)
    file_menu["menu"] = file_menu.menu

    file_menu.menu.add_command(label="Load Image", command=lambda: load_image(img_orig, img_mod))
    file_menu.menu.add_command(label="Save Image", command=lambda: save_image())

    # Setting up the Edit menu, has all the methods to edit the image
    edit_menu = tk.Menubutton(root, text="Edit")
    edit_menu.pack()
    edit_menu.place(x=30, y=0)
    edit_menu.menu = tk.Menu(edit_menu, tearoff=0)
    edit_menu["menu"] = edit_menu.menu

    # Setting up the sub-menus for each edit category
    global img_loaded

    blur_menu = tk.Menu(edit_menu, tearoff=0)
    blur_menu.add_command(label="Box Blur",
                          command=lambda: load_image_canvas(Functions.box_blur(img_loaded, (5, 5)), img_mod))
    blur_menu.add_command(label="Gaussian Blur",
                          command=lambda: load_image_canvas(Functions.gaussian_blur(img_loaded, (5, 5)), img_mod))
    blur_menu.add_command(label="Median Blur",
                          command=lambda: load_image_canvas(Functions.median_blur(img_loaded, 5), img_mod))
    blur_menu.add_command(label="Bilateral Blur",
                          command=lambda: load_image_canvas(Functions.bilateral_blur(img_loaded, 5), img_mod))
    blur_menu.add_command(label="Remove Blur",
                          command=lambda: load_image_canvas(Functions.de_blur(img_loaded), img_mod))

    orientation_menu = tk.Menu(edit_menu, tearoff=0)
    orientation_menu.add_command(label="Crop Image",
                                 command=lambda: load_image_canvas(Functions.crop_image(img_loaded, 0, 0, 256, 256), img_mod))
    orientation_menu.add_command(label="Flip Image",
                                 command=lambda: load_image_canvas(Functions.flip_image(img_loaded, 0), img_mod))
    orientation_menu.add_command(label="Mirror Image",
                                 command=lambda: load_image_canvas(Functions.mirror_image(img_loaded, 0), img_mod))
    orientation_menu.add_command(label="Rotate Image",
                                 command=lambda: load_image_canvas(Functions.rotate_image(img_loaded, 90), img_mod))
    orientation_menu.add_command(label="Reverse Image",
                                 command=lambda: load_image_canvas(Functions.reverse_image(img_loaded), img_mod))

    color_menu = tk.Menu(edit_menu, tearoff=0)
    color_menu.add_command(label="Grayscale",
                           command=lambda: load_image_canvas(Functions.grayscale_image(img_loaded), img_mod))
    color_menu.add_command(label="Change Color Balance",
                           command=lambda: load_image_canvas(Functions.change_color_balance(img_loaded, 0, 50), img_mod))
    color_menu.add_command(label="Change Contrast and Brightness",
                           command=lambda: load_image_canvas(Functions.change_contrast_and_brightness(img_loaded, 1.1, 0, 0.6), img_mod))

    noise_menu = tk.Menu(edit_menu, tearoff=0)
    noise_menu.add_command(label="Gaussian Noise",
                           command=lambda: load_image_canvas(Functions.gaussian_noise(img_loaded), img_mod))
    noise_menu.add_command(label="Salt and Pepper Noise",
                           command=lambda: load_image_canvas(Functions.salt_and_pepper_noise(img_loaded), img_mod))
    noise_menu.add_command(label="Poisson Noise",
                           command=lambda: load_image_canvas(Functions.poisson_noise(img_loaded), img_mod))
    noise_menu.add_command(label="Speckle Noise",
                           command=lambda: load_image_canvas(Functions.speckle_noise(img_loaded), img_mod))

    detection_menu = tk.Menu(edit_menu, tearoff=0)
    detection_menu.add_command(label="Naïve Edge Detection",
                               command=lambda: load_image_canvas(Functions.naive_edge_detect(img_loaded), img_mod))
    detection_menu.add_command(label="Sobel Edge Detection",
                               command=lambda: load_image_canvas(Functions.sobel_edge_detect(img_loaded, 3, 0, 1), img_mod))
    detection_menu.add_command(label="Canny Edge Detection",
                               command=lambda: load_image_canvas(Functions.canny_edge_detect(img_loaded), img_mod))

    # Linking the sub-menus to edit menu
    edit_menu.menu.add_cascade(label="Blur", menu=blur_menu)
    edit_menu.menu.add_cascade(label="Orientation", menu=orientation_menu)
    edit_menu.menu.add_cascade(label="Color", menu=color_menu)
    edit_menu.menu.add_cascade(label="Noise", menu=noise_menu)
    edit_menu.menu.add_cascade(label="Detect Edge", menu=detection_menu)

    root.mainloop()


def load_image(orig, mod):
    tk.Tk().withdraw()
    filename = askopenfilename()

    if filename == "":  # If choosing close instead of opening an image
        return

    img = cv2.imread(filename)
    load_image_canvas(img, orig)
    load_image_canvas(img, mod)

    return img


def load_image_canvas(img, frame):
    global img_loaded
    img_loaded = img
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    img_tk = ImageTk.PhotoImage(img.resize((512, 512), Image.ANTIALIAS))  # Resizing for the reserved area

    # Clearing all the past images
    for child in frame.winfo_children():
        child.destroy()

    # Generating canvases to hold the images and assigning them to their frames
    img_canvas = tk.Canvas(frame, bg='white', height=512, width=512, borderwidth=0, highlightthickness=0)
    img_canvas.grid(row=0, column=0, sticky='nesw', padx=0, pady=0)
    img_canvas.image = img_tk
    img_canvas.create_image(0, 0, image=img_canvas.image, anchor='nw')


def save_image():
    tk.Tk().withdraw()

    if img_loaded is None:  # if img_loaded == something
        print("ERROR! No image to save!")
        return

    filename = asksaveasfile(mode='w', defaultextension=".jpg")

    if filename == "":  # If choosing close instead of saving the image
        return

    img_saved = Image.fromarray(cv2.cvtColor(img_loaded, cv2.COLOR_BGR2RGB))
    img_saved.save(filename)


if __name__ == '__main__':
    init()
