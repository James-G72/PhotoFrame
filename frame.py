import tkinter as tk
import os
from PIL import Image, ImageTk
import random
import math
import time


class PhantomFrame(tk.Frame):
    """
    The main host that is called to start the game
    """

    def __init__(self, parent, target_folder="",timer=5,shuffle=True):
        '''
        The GameBoard object hosts the whole game. Upon iitialisation the Sudoku squares are created and pieces drawn.
        :param parent: The tk root window inside of which you want the board to be drawn
        :param side_size: Dictates the width of the side panel with the game controls
        :param square_size: The size of the chess board in pixels
        :param rows: Rows in the chess board (default = 8)
        :param columns: Columns in the chess board (defailt = 8)
        :param color: This defines the background board colour
        '''
        # There is no need to edit any of the sizes. The default for side_size is 200
        # The default colors here are pure white and a dark gray

        # ---------------- Section 1 : Assembling basic variables ----------------
        # Adding all of the pictures from Images folder
        # self.imageHolder = {}  # Creating a dictionary
        # pieceList = "0123456789"  # These are all the different types of pieces possible
        # for f in pieceList:  # Cycling through the pieces
        #     for add in ["","_mini"]:
        #         with open("Images/"+f+add+".png","rb") as imageFile:  # Opening the photo within the variable space
        #             # The images can't be stored as P or p in MacOS as they're read the same
        #             # So the colour is introduced by adding b or w after the piece notation
        #             string = base64.b64encode(imageFile.read())  # Creating a string that describes the gif in base64 format
        #             self.imageHolder[f+add] = tk.PhotoImage(data=string)

        # ---------------- Section 2 : Creating the board ----------------
        # The whole board is drawn within the window in TkInter
        # This a very long section defining a lot of stationary visuals for the GUI
        # Most of the placement is just done by eye to make sure it all looks okay
        imgs = []
        path = "/Users/jamesgower2/Pictures/Honor10"
        valid_images = [".jpg",".gif",".png",".tga"]
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1]
            if ext.lower() not in valid_images:
                continue
            imgs.append(Image.open(os.path.join(path,f)))
        self.list = imgs
        self.image_num = len(self.list)
        if shuffle:
            random.shuffle(self.list)
        self.timer = timer
        self.pos = 0

        # Creating the canvas for the window
        tk.Frame.__init__(self,parent)
        # This is self explanatory and provides a blank space upon which visual objects can be placed
        self.c_width = self.winfo_screenwidth()
        self.c_height = self.winfo_screenheight()
        self.canvas = tk.Canvas(self,borderwidth=0,highlightthickness=0,width=self.c_width,height=self.c_height,background="black")
        self.canvas.pack(side="top",fill="both",expand=True)  # Packed with a small amount of padding either side

    def _run_image(self):
        self.image = self.list[self.pos]
        im = self._resized_image()
        img = ImageTk.PhotoImage(im)
        self.canvas.delete("image")
        self.canvas.create_image(self.c_width/2,self.c_height/2, image=img, anchor="c", tag="image") # First we create the image in the top left
        self.update()
        if self.pos >= self.image_num:
            self.pos = 0
        else:
            self.pos += 1
        time.sleep(self.timer)
        self.after(5000,self._run_image())

    def _resized_image(self):
        self.img_copy = self.image.copy()
        image_width, image_height = self.image.size
        HEIGHT,WIDTH = self.winfo_screenheight(), self.winfo_screenwidth()
        print(image_width,image_height,HEIGHT,WIDTH)
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

        return self.img_copy.resize((r_w,r_h))