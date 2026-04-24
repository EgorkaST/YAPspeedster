import tkinter
from tkinter import *
from tkinter import filedialog

def create_gui():
    # Main window of GUI
    root = Tk()
    root.title("YUP speedster")
    root.geometry("500x300")

    # speed scaler
    speed_scale = Scale(
        orient="horizontal",
        from_=1.00,
        to=3.00,
        resolution= 0.25,
        tickinterval= 1,
        digits= 3,
        length= 100,
        label= "Speed"
    )
    speed_scale.pack(fill="x")

    # vad level scaler
    vad_scale = Scale(
        orient="horizontal",
        from_=1.00,
        to=3.00,
        resolution= 0.25,
        tickinterval= 1,
        digits= 3,
        length= 100,
        label= "VAD scale"
    )
    vad_scale.pack(fill="x")

    file_path_desc = Label(root, text="File Path")
    file_path_desc.pack()

    txt_path = Entry(root, width=200)
    txt_path.pack()

    def open_file(entry_field):
        audio_filepath = filedialog.askopenfilename()
        entry_field.delete(0, tkinter.END)
        entry_field.insert(0, audio_filepath)

    button_get_path = Button(root, text="Select file", command=lambda: open_file(txt_path))
    button_get_path.pack()

    root.mainloop()
    return root