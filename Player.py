import tkinter as tk
# Importing the custom photo frame
import frame


def exit_fullscreen(event):
    # This functions allows the full-screen to be exited
    Window.attributes("-fullscreen", False)


# Editable variables that determine how the player performs
SHUFFLE = True
SHUFFLE_LEVEL = "folder"  # Either "folder" or "photo" and defines whether all folders are shuffles or all photos are
# shuffled
TIMER = 4  # seconds

# Initialising the window
Window = tk.Tk()  # Root window is created
Window.title("PhotoFrame")  # Title added
folder = "D:\\"
frame_object = frame.PhantomFrame(Window, target_folder=folder, timer=TIMER, shuffle=SHUFFLE,
                                  shuffle_level=SHUFFLE_LEVEL)  # Initialising the frame area
# within the root window
frame_object.pack(side="top", fill="both", expand="true", padx=0,
                  pady=0)  # Packing and displaying (in TkInter everything to be displayed in a window needs to be
# either "packed" or "placed"
Window.resizable(width=False, height=False)  # This locks the size of the window so it cant be resized
Window.attributes("-fullscreen", True)
Window.bind("<Escape>", exit_fullscreen)
# Window.geometry(str(Window.winfo_screenwidth())+"x"+str(Window.winfo_screenheight())) # This locks the geometry
# including side_size to encompass the visuals

frame_object._splash()