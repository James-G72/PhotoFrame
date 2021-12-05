import tkinter as tk
# Importing the custom photo frame
import frame

def test(event):
    # This functions allows the full-screen to be exited
    Window.attributes("-fullscreen", False)

# Initialising the window
Window = tk.Tk() # Root window is created
Window.title("PhotoFrame") # Title added
folder = "/Volumes/Photos"
frame_object = frame.PhantomFrame(Window,target_folder=folder,timer=5,shuffle=True) # Initialising the frame area within the root window
frame_object.pack(side="top", fill="both", expand="true", padx=0, pady=0) # Packing and displaying (in TkInter everything to be displayed in a window needs to be either "packed" or "placed"
Window.resizable(width=False, height=False) # This locks the size of the window so it cant be resized
Window.attributes("-fullscreen", True)
Window.bind("<Escape>",test)
# Window.geometry(str(Window.winfo_screenwidth())+"x"+str(Window.winfo_screenheight())) # This locks the geometry including side_size to encompass the visuals

# As with most GUIs the game runs out of the host object which in this case is a GameBoard called board.
# All the logic required to run a game of sudoku is included in the board class
# By calling mainloop() on the tkinter window we allow the buttons to run the game with no further code required here,
Window.after(1,frame_object._run_image())
Window.mainloop()