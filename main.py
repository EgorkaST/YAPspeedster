from gui import GUI
import tkinter as tk

def main():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()
    print("meow")

if __name__ == '__main__':
    main()