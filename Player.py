from tkinter import *
from PIL import Image, ImageTk
import math
import os
import time

root = Tk()
root.title("Title")
HEIGHT = root.winfo_screenheight()
WIDTH = root.winfo_screenwidth()
root.geometry("{0}x{1}+0+0".format(WIDTH, HEIGHT))
root.configure(background="black")



class Example(Frame):
    def __init__(self, master, *pargs):
        Frame.__init__(self, master, *pargs)

        imgs = []
        path = "/Users/jamesgower2/Pictures/Honor10"
        valid_images = [".jpg",".gif",".png",".tga"]
        for f in os.listdir(path):
            ext = os.path.splitext(f)[1]
            if ext.lower() not in valid_images:
                continue
            imgs.append(Image.open(os.path.join(path,f)))
        self.list = imgs
        self._run_image(0)

    def _run_image(self, possition):
        while possition > len(self.list):
            possition -= len(self.list)
        self.image = self.list[possition]
        self.poss = possition
        self.img_copy = self.image.copy()

        self.background_image = ImageTk.PhotoImage(self.image)

        self.background = Label(self,image=self.background_image)
        self.background.pack(fill=Y,expand=NO)
        self.background.bind('<Configure>', self._resize_image)

    def _resize_image(self,event):
        self.image = self.list[self.poss]
        self.img_copy = self.image.copy()
        image_width, image_height = self.image.size
        HEIGHT, WIDTH = event.height, event.width
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


        self.image = self.img_copy.resize((r_w,r_h))

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)
        if self.poss + 1 > len(self.list):
            self.poss = 0
        else:
            self.poss += 1
        print(self.poss)
        time.sleep(2)



e = Example(root)
e.pack(fill=BOTH, expand=YES)


root.mainloop()