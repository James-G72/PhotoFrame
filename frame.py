import tkinter as tk
import os
from PIL import Image, ImageTk, ImageFont, ImageDraw
import random
import math
import time
import datetime
import copy


def _re_order_list(list_in, offset):
    """
    Taking a list and offset and re-ordering the list such that the xth element onwards are at the start and all
    elements before that are before it.
    """
    assert offset < len(list_in), "Cannot split a list by an index that is greater than the length of the list"
    first = list_in[offset:]
    last = list_in[:offset]
    last.reverse()
    for name in last:
        first.append(name)
    return first


class PhantomFrame(tk.Frame):
    """
    PhantomFrame is the host class for the logic that handles the pictures
    """

    def __init__(self, parent, target_folder="", timer=5, shuffle_level="folder", shuffle=True, offset=0):
        """
        The PhantomFrame object the slideshow code.
        :param parent: The tk root window inside of which you want the pictures to be drawn
        :param target_folder: The folder to pull photos from as the "Main" folder. This can contain folders within it
        :param timer: The duration between photos in seconds
        :param shuffle: A bool as to whether or not to play photos in order, or shuffle them. (Long term I would like to
                        move this decision to which port the USB stick is plugged into.
        """
        # ---------------- Section 1 : Unpacking the images ----------------
        # All of the images are processed upon start-up and placed into a list
        # Additional information is also extracted and stored such that they can later be overlayed

        # Defining all lists that hold images and information.
        self.imgs = {}
        self.date = {}
        self.folder_stats = {}
        self.image_num = 0
        self.menu_state = {"active": self._null}

        # Trying to find a previous start point.
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        with open(self.base_path + "\\continue.txt", "r") as f:
            self.continue_from = f.read()

        # Shuffling cannot be done properly when you have an offset
        if shuffle:
            offset = 0

        # These are the types of image that can currently be handled
        self.valid_images = [".jpg", ".gif", ".png", ".tga"]
        # This pulls all immediate folders from the location defined as "Main"
        folders = sorted(next(os.walk(target_folder))[1])
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
            self._unpack(target_folder, "Main Folder")
            self.shuffle_level = "photos"
        else:
            # Checking to see if there are pictures in the top level folder
            self._unpack(target_folder, "Main Folder")
            # Cycling through all folders that were found and extracting from them
            assert offset < len(folders), "The defined folder offset is greater than the number of folders."
            for x in range(offset, len(folders)):
                self._unpack(target_folder + "\\" + folders[x], folders[x])
            self.shuffle_level = shuffle_level

        # Defining the order in which the folders or photos should be iterated through
        self.folder_order = [x for x in self.imgs.keys()]
        if self.shuffle_level == "folder":
            if shuffle:
                random.shuffle(self.folder_order)
        elif self.shuffle_level == "photos":
            self.pos_list = [x for x in range(0, self.image_num)]
            if shuffle:
                random.shuffle(self.pos_list)
        self.shuffle = shuffle
        # Checking if the continue_from value is a valid folder
        if self.continue_from in [x for x in self.imgs.keys()] and not shuffle:
            cut_index = [x for x in self.imgs.keys()].index(self.continue_from)
            self.folder_order = _re_order_list(self.folder_order, cut_index)

        # Setting values required for tracking image order etc
        self.timer = timer
        self.pos = 0
        self.paused = False
        self.in_menu = True
        self.folder_pos = 0
        self.prev_folder = ""
        self.current_folder = self.folder_order[0]

        # Imagefont requires the font file to be imported
        self.font_path = self.base_path + "\\theboldfont.ttf"

        # Creating the canvas for the window
        self.top = parent
        tk.Frame.__init__(self, self.top)
        # This is self-explanatory and provides a blank space upon which visual objects can be placed
        self.c_width = self.winfo_screenwidth()
        self.c_height = self.winfo_screenheight()
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, width=self.c_width, height=self.c_height,
                                background="black")
        self.canvas.pack(side="top", fill="both", expand=True)  # Packed with a small amount of padding either side

        # Setting up a bool that means the big intro page is only played once
        self.boot = True

        self._bind_keys()

    def _tksleep(self, t):
        """
        This function is taken from: https://stackoverflow.com/questions/74214619/how-to-use-tkinter-after-method-to-delay-a-loop-instead-time-sleep
        It performs a function that I have been trying to do for a long time in tkinter which is to successfully wait
        for a set amount of time while still receiving inputs.
        """
        self.sleep_time = time.time()
        ms = int(t * 1000)
        root = tk._get_default_root()
        var = tk.IntVar(root)
        root.after(ms, lambda: var.set(1))
        root.wait_variable(var)

    def _null(self):
        """
        A placeholder function that doesn't do anything but sits inside the menu_state dictionary when there is no
        selected menu item.
        """
        print("Null menu function triggered.")
        return

    def _bind_keys(self):
        """
        Binding certain keys to the top level widget such that a keyboard can interact with the frame object.
        """
        self.top.bind("<Return>", self._return_statemachine)
        self.top.bind("<Left>", self._left_statemachine)
        self.top.bind("<Right>", self._right_statemachine)
        self.top.bind("<Up>", self._up_statemachine)
        self.top.bind("<Down>", self._down_statemachine)

    def _left_statemachine(self, event):
        """
        Controlling the response to pressing the left arrow on the keyboard. This is used for either navigating the
        menu or for going to the previous picture
        """
        if self.in_menu:
            self.menu_state["active"]()
        self.top.mainloop()

    def _right_statemachine(self, event):
        """
        Controlling the response to pressing the right arrow on the keyboard. This is used for either navigating the
        menu or for going to the next picture.
        """
        if self.in_menu:
            self.menu_state["active"]()
        self.top.mainloop()

    def _up_statemachine(self, event):
        """
        Controlling the response to pressing the up arrow on the keyboard. This is used for either navigating the
        menu or no function.
        """
        if self.in_menu:
            self.menu_state["active"]()
        self.top.mainloop()

    def _down_statemachine(self, event):
        """
        Controlling the response to pressing the down arrow on the keyboard. This is used for either navigating the
        menu or no function.
        """
        if self.in_menu:
            self.menu_state["active"]()
        self.top.mainloop()

    def _return_statemachine(self, event):
        """
        Controlling how the space bar interacts. Its action is dependent on the current state of the frame.
        """
        if not self.in_menu:
            if self.paused:
                self.paused = False
                self._redraw()
                self._tksleep(self.sleep_remaining)
                self._run_image()
            else:
                self.paused = True
                # Working out how long ago the previous _tksleep started
                self.sleep_remaining = max(self.timer - (time.time() - self.sleep_time), 0)
                self.sleep_time = None
                self._draw_pause()
        else:
            self.playing_photos = True
            self.in_menu = False
            self._run_image()
        self.top.mainloop()

    def _draw_to_canvas(self, image, set_drawn=True):
        """
        The function that draws a given image to the tkinter canvas.
        This has been packaged into a function as there are several steps to this process in order to store the PIL
        image that is being drawn as well as the ImageTK.PhotoImage object.
        """
        # This has to be a self. variable or else upon exiting the _draw_pause function the canvas loses the
        # reference to the image and goes blank
        self.photo_image = ImageTk.PhotoImage(image)
        self.canvas.delete("image")
        # Pasting the new image onto the canvas with the tag "image" so it can easily be removed
        self.canvas.create_image(self.c_width / 2, self.c_height / 2, image=self.photo_image, anchor="c", tag="image")
        self.update()
        # If it has been requested to save the PIL image
        if set_drawn:
            self.drawn_image = image

    def _draw_pause(self):
        if self.paused:
            # Pulling in the existing image that is on the canvas
            # Because of the way Python handles the memory we need to make a copy of the image so we don't edit the
            # original
            back_im = copy.copy(self.drawn_image)
            # Creating a blank image with an alpha of 120
            pause_im = Image.new('RGBA', back_im.size, (255, 255, 255, 180))
            draw_pause = ImageDraw.Draw(pause_im)
            draw_pause.text((960, 540), "I I", (0, 0, 0), font=self._font_gen(200), anchor="mm")
            back_im.putalpha(pause_im.getchannel('A').point(lambda x: (x*0.2)))
            # Draw the image to the canvas but don't update the drawn image
            self._draw_to_canvas(back_im, set_drawn=False)

    def _unpack(self, target, folder_name):
        """
        Searches through directory and appends all suitable images found to self.imgs
        :param target: Location in which to search for images
        :param folder_name: The name of the folder for use in dictionaries
        :return: None
        """
        # Defining variables for tracking the first and last date in the folder
        first_date = datetime.datetime.now()
        # Setting a time a very long time in the past (1600s)
        last_date = datetime.datetime.now() - datetime.timedelta(days=150000)

        # Appending a new list to the origin dictionary
        if folder_name not in self.imgs.keys():
            self.imgs[folder_name] = {}
            self.date[folder_name] = {}

        # index tracker within each folder
        folder_pos = 0

        # For all files in the directory
        for f in os.listdir(target):
            if f[0] != ".":
                ext = os.path.splitext(f)[1]
                # Checking the filetype is supported
                if ext.lower() not in self.valid_images:
                    continue
                # Appending the image file to the list
                self.imgs[folder_name][folder_pos] = Image.open(os.path.join(target, f))
                self.image_num += 1
                try:
                    # Attempt to pull the date exif data
                    exif = Image.open(os.path.join(target, f))._getexif()[36867]
                    # Turn the data into a datetime object
                    date_time_object = datetime.datetime.strptime(exif.split(" ")[0], '%Y:%m:%d')
                    # Format it in a better way
                    proper_date = date_time_object.strftime("%d-%B-%Y")
                    self.date[folder_name][folder_pos] = proper_date
                    # Check if this date will change the extremes in any way
                    if date_time_object < first_date:
                        first_date = date_time_object
                    if date_time_object > last_date:
                        last_date = date_time_object
                except:
                    # If the above fails then just append a blank date
                    self.date[folder_name][folder_pos] = ""
                folder_pos += 1
        # Set the folder stats
        self.folder_stats[folder_name] = [folder_name, first_date.strftime("%d-%B %Y"), last_date.strftime("%d-%B %Y")]

    def _run_image(self):
        """
        This function is self_calling and handles all the visuals. Each image is cycled through
        :return: None
        """
        # Pulling out the image that we want to show next
        self.image = self.imgs[self.current_folder][self.pos]
        self.date_1 = self.date[self.current_folder][self.pos]

        # The previous folder is tracked to know whether to show a splash image for that folder
        if self.current_folder != self.prev_folder and self.shuffle_level != "photos":
            # Ask the intro screen function to display the name of the folder and the range of dates within it
            self.im_overlay = self._intro_screen(self.current_folder)
            skip = False
        else:
            # Calling the resize function to ensure that the image is shown full screen
            self.im = self._resized_image()
            # Calling the overlay function to add the text over the image
            self.im_overlay = self._overlay()
            skip = True

        self._draw_to_canvas(self.im_overlay)

        # Preventing the counter from exceeding the number of images while iterating
        if self.pos == len(self.imgs[self.current_folder]) - 1 and skip:
            self.pos = 0
            self.folder_pos += 1
            self.prev_folder = self.current_folder
            self.current_folder = self.folder_order[self.folder_pos]
            with open(self.base_path + "\\continue.txt", "w") as f:
                f.write(self.current_folder)
        elif skip:
            self.pos += 1
            self.prev_folder = self.current_folder
        else:
            self.prev_folder = self.current_folder

        self._tksleep(self.timer)
        self._run_image()


    def _redraw(self):
        """
        If this function is called it implies that there has been a state-change that is not currently implemented in
        the image self.img. The current image is therefore redrawn from scratch.
        """
        self._draw_to_canvas(self.drawn_image)

    def _resized_image(self):
        """
        Takes an image and fits it to fill the full screen by expending until either the width ot the height is at max
        :return: The original image re-sized
        """
        # Creating a copy of the original image
        self.img_copy = self.image.copy()
        # Extracting the size data
        image_width, image_height = self.image.size
        # Pulling the side of the window for comparison
        HEIGHT, WIDTH = self.winfo_screenheight(), self.winfo_screenwidth()

        # Running through the heights and widths to work out what needs to be increased by what
        if image_width > WIDTH:  # If the image is wider than the screen we know we need to make it smaller
            w_f = image_width / WIDTH  # Working out the required reduction
            if image_height > HEIGHT:  # Same for the height
                h_f = image_height / HEIGHT
                if w_f >= h_f:  # Checking which reduction is larger and setting this as the reduction amount
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
        else:  # Otherwise we just need to know which can be expanded the most
            w_f = image_width / WIDTH
            h_f = image_height / HEIGHT
            if w_f >= h_f:
                r_w = WIDTH
                r_h = math.floor(image_height / w_f)
            else:
                r_h = HEIGHT
                r_w = math.floor(image_width / h_f)

        # Return the image scaled by the factors calculated above
        return self.img_copy.resize((int(r_w), int(r_h)))

    def _overlay(self):
        """
        Overlays text over the top of the image to show the folder name and capture date
        :return: Image with the overlay on top
        """
        # Take a cropped section of the top left of the image
        im_check = self.im.crop((0, 0, 100, 50))
        # Count and get all those pixels in a list
        npixels = im_check.size[0] * im_check.size[1]
        cols = im_check.getcolors(npixels)
        # Get the sum of all the RGB values in the cropped image
        sumRGB = [(x[0] * x[1][0], x[0] * x[1][1], x[0] * x[1][2]) for x in cols]
        # Find the average value in the cropped image
        avg = tuple([sum(x) / npixels for x in zip(*sumRGB)])
        # If the average RGB value is less than 300 then set as white, else black
        if sum(avg) < 300:
            font_color = (255, 255, 255)
        else:
            font_color = (0, 0, 0)
        # Create a draw image
        draw = ImageDraw.Draw(self.im)
        # Draw over the top for the folder name
        # TODO add some room to this so that it isn't right against the left hand side of the screen if the image is
        #  full width
        draw.text((1, 1), self.current_folder, font_color, font=self._font_gen(40))
        # Draw over the top for the date
        draw.text((1, 46), self.date_1, font_color, font=self._font_gen(25))

        # Return the image with the overlay on top
        return self.im

    def _font_gen(self, size):
        """
        Generate an ImageFont object of a given font-size
        size: Font size to be created
        :return: ImageFont object
        """
        return ImageFont.truetype(self.font_path, size)

    def _intro_screen(self, name):
        """
        Creates a black image to be displayed before a folder with the folder name and overlays the name and dates
        :return: Black image with overlays applied
        """
        # TODO make the font-size dependent on the width of the words
        self.image = Image.new(mode="RGBA", size=(1920, 1080))
        self.im = self._resized_image()
        draw = ImageDraw.Draw(self.im)
        # Draw over the top for the folder name
        centre_width = int(self.im.size[0] / 2)
        centre_height = int(self.im.size[1] / 2)
        draw.text((centre_width, centre_height), self.folder_stats[name][0], (256, 256, 256), font=self._font_gen(100),
                  anchor="mm")
        # Draw over the top for the date
        date_string = "(" + self.folder_stats[name][1] + "    -    " + self.folder_stats[name][2] + ")"
        draw.text((centre_width, centre_height + 120), date_string, (256, 256, 256), font=self._font_gen(40),
                  anchor="mm")

        return self.im

    def _splash(self):
        self.image = Image.new(mode="RGBA", size=(1920, 1080), color=(255, 255, 255))
        self.im = self._resized_image()
        draw = ImageDraw.Draw(self.im)
        centre_width = int(self.im.size[0] / 2)
        centre_height = int(self.im.size[1] / 2)
        color = (0, 0, 0)
        draw.text((centre_width, centre_height - 200), "PhotoFrame", color, font=self._font_gen(220),
                  anchor="mm")
        draw.text((centre_width + 500, centre_height - 90), "by James Gower", color, font=self._font_gen(40),
                  anchor="mm")
        draw.text((centre_width - 450, centre_height + 10), "Settings:", color, font=self._font_gen(70),
                  anchor="mm")
        height = 60
        for setting in ["* Shuffle:  " + str(self.shuffle), "* Level:  " + str(self.shuffle_level), "* Delay:  "
                                                                                                    + str(self.timer)]:
            draw.text((centre_width - 350, centre_height + height), setting, color, font=self._font_gen(40),
                      anchor="mm")
            height += 40
        draw.text((centre_width + 350, centre_height + 10), "Total Images:", color, font=self._font_gen(70),
                  anchor="mm")
        draw.text((centre_width + 350, centre_height + 60), str(self.image_num), color, font=self._font_gen(40),
                  anchor="mm")

        self._draw_to_canvas(self.im)
        # Ensuring that the splash screen cannot be called again
        self.boot = False

        self.mainloop()
