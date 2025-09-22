import tkinter as tk
from ..interfaccia_grafica_tkinter_app import AppTaxi

def main():
    root = tk.Tk()
    root.geometry("1020x512")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    AppTaxi(root)
    root.mainloop()

if __name__ == "__main__":
    main()
