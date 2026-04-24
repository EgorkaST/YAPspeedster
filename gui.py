from tkinter import *
from tkinter import filedialog

root = Tk()
root.title("YUP speedster")
root.geometry("500x300")

# podcast speed
podcastSpeedScale = Scale(orient="horizontal", from_=1.00, to=3.00, resolution= 0.25, tickinterval= 0.5, digits= 3, length= 100)
podcastSpeedScale.coords()
podcastSpeedScale.pack(fill="x")

audio_filepath = filedialog.askopenfilename()
print(audio_filepath)
print(type(audio_filepath))

root.mainloop()
print("meow")
