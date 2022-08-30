import tkinter as tk
import os
from PIL import Image, ImageTk, ImageFont, ImageDraw
import random
import math
import time
import datetime


class PhantomFrame(tk.Frame):
    """
    PhantomFrame is the host class for the logic that handles the pictures
    """

    def __init__(self, parent, target_folder="", timer=5, shuffle=True):
        '''
        The PhantomFrame object the slideshow code.
        :param parent: The tk root window inside of which you want the pictures to be drawn
        :param target_folder: The folder to pull photos from as the "Main" folder. This can contain folders within it
        :param timer: The duration between photos in seconds
        :param shuffle: A bool as to whether or not to play photos in order, or shuffle them. (Long term I would like to
                        move this decision to which port the USB stick is plugged into.
        '''
        # ---------------- Section 1 : Unpacking the images ----------------
        # All of the images are processed upon start-up and placed into a list
        # Additional information is also extracted and stored such that they can later be overlayed

        # Defining all of the lists that hold images and information.
        self.imgs = []
        self.origin = []
        self.date = []
        self.folder_stats = []
        # These are the types of image that can currently be handled
        self.valid_images = [".jpg",".gif",".png",".tga"]
        target_folder = "D:\\" # This is required to run the code on my laptop
        # This pulls all immediate folders from the location defined as "Main"
        folders = next(os.walk(target_folder))[1]
        if "System Volume Information" in folders:
            folders.remove("System Volume Information")
        # If no folders are found then the photos can all be unpacked from a single folder
        if len(folders) == 0:
            unpack_mode = "single_folder"
        else:
            unpack_mode = "multiple_folders"

        # Unpacking images into a list
        if unpack_mode == "single_folder":
            # Calling a function that appends all images found in that folder
            self._unpack(target_folder, "Main")
        else:
            self._unpack(target_folder, "Main")
            # Cycling through all folders that were found and extracting from them
            for x in range(0, len(folders)):
                self._unpack(target_folder+folders[x], folders[x])

        self.image_num = len(self.imgs)
        # Defining a list of positions to shuffle such that we don't have to shuffle the actual lists
        self.pos_list = [x for x in range(0, self.image_num)]
        if shuffle:
            random.shuffle(self.pos_list)
        self.timer = timer
        self.pos = 0

        # Imagefont requires the font file to be imported
        self.folder_font = ImageFont.truetype("theboldfont.ttf", 40)
        self.date_font = ImageFont.truetype("theboldfont.ttf", 25)

        # Creating the canvas for the window
        tk.Frame.__init__(self, parent)
        # This is self explanatory and provides a blank space upon which visual objects can be placed
        self.c_width = self.winfo_screenwidth()
        self.c_height = self.winfo_screenheight()
        self.canvas = tk.Canvas(self,borderwidth=0,highlightthickness=0,width=self.c_width,height=self.c_height,background="black")
        self.canvas.pack(side="top", fill="both", expand=True)  # Packed with a small amount of padding either side

    def _unpack(self, target, folder_name):
        """
        Searches through directory and appends all suitable images found to self.imgs
        :param target: Location in which to search for images
        :param folder_name: The name to be appended to self.origin
        :return: None
        """
        # Defining variables for tracking the first and last date in the folder
        first_date = datetime.datetime.now()
        # Setting a time a very long time in the past (1600s)
        last_date = datetime.datetime.now() - datetime.timedelta(days=150000)
        # For all files in the directory
        for f in os.listdir(target):
            if f[0] != ".":
                ext = os.path.splitext(f)[1]
                # Checking the filetype is supported
                if ext.lower() not in self.valid_images:
                    continue
                # Appending the image file to the list
                self.imgs.append(Image.open(os.path.join(target, f)))
                # Appending the folder name
                self.origin.append(folder_name)
                try:
                    # Attempt to pull the date exif data
                    exif = Image.open(os.path.join(target,f))._getexif()[36867]
                    # Turn the data into a datetime object
                    date_time_object = datetime.datetime.strptime(exif.split(" ")[0], '%Y:%m:%d')
                    # Format it in a better way
                    proper_date = date_time_object.strftime("%d-%B %Y")
                    self.date.append(proper_date)
                    # Check if this date will change the extremes in anyway
                    if date_time_object < first_date:
                        first_date = date_time_object
                    if date_time_object > last_date:
                        last_date = date_time_object
                except:
                    # If the above fails then just append a blank date
                    self.date.append("")
        # Set the folder stats
        self.folder_stats.append([first_date.strftime("%d-%B %Y"), last_date.strftime("%d-%B %Y")])

    def _run_image(self):
        """
        This function is self_calling and handles all of the visuals. Each image is cycled through
        :return: None
        """
        # Pulling out the image that we want to show next
        self.image = self.imgs[self.pos_list[self.pos]]
        self.date_1 = self.date[self.pos_list[self.pos]]
        self.folder = self.origin[self.pos_list[self.pos]]
        self.prev_folder = "Main"
        self.im = self._resized_image()
        self.im_overlay = self._overlay()
        img = ImageTk.PhotoImage(self.im_overlay)
        self.canvas.delete("image")
        self.canvas.create_image(self.c_width/2,self.c_height/2, image=img, anchor="c", tag="image") # First we create the image in the top left
        self.update()
        if self.pos >= self.image_num:
            self.pos = 0
        else:
            self.pos += 1
        time.sleep(self.timer)
        self.prev_folder = self.folder
        self.after(5000, self._run_image())

    def _resized_image(self):
        self.img_copy = self.image.copy()
        image_width, image_height = self.image.size
        HEIGHT, WIDTH = self.winfo_screenheight(), self.winfo_screenwidth()
        print(image_width, image_height, HEIGHT, WIDTH)
        if image_width > WIDTH:
            w_f = image_width / WIDTH
            if image_height > HEIGHT:
                h_f = image_height / HEIGHT
                if w_f >= h_f:
                    r_w = WIDTH
                    r_h = math.floor(image_height / w_f)
                else:
                    r_h = HEIGHT
                    r_w = math.floor(image_width / h_f)
            else:
                r_h = image_height / w_f
                r_w = WIDTH
        elif image_height > HEIGHT:
            h_f = image_height / HEIGHT
            r_h = HEIGHT
            r_w = image_width / h_f
        else:
            w_f = image_width / WIDTH
            h_f = image_height / HEIGHT
            if w_f >= h_f:
                r_w = WIDTH
                r_h = math.floor(image_height / w_f)
            else:
                r_h = HEIGHT
                r_w = math.floor(image_width / h_f)

        return self.img_copy.resize((int(r_w),int(r_h)))

    def _overlay(self):
        """
        Overlays text over the top of the image to show the folder name and capture date
        :return: Image with the overlay on top
        """
        im_check = self.im.crop((0, 0, 100, 50))
        npixels = im_check.size[0] * im_check.size[1]
        cols = im_check.getcolors(npixels)
        sumRGB = [(x[0] * x[1][0], x[0] * x[1][1], x[0] * x[1][2]) for x in cols]
        avg = tuple([sum(x) / npixels for x in zip(*sumRGB)])
        if sum(avg) < 300:
            font_color = (255, 255, 255)
        else:
            font_color = (0, 0, 0)
        draw = ImageDraw.Draw(self.im)
        draw.text((1, 1), self.folder, font_color, font=self.folder_font)
        draw.text((1, 46), self.date_1, font_color, font=self.date_font)

        return self.im