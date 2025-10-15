# main.py
from stock_monitor import StockMonitor
import tkinter as tk
from PIL import Image, ImageTk
def main():
    """
    Главная функция приложения.
    Создает главное окно и запускает монитор акций.
    """
    root = tk.Tk()
    app = StockMonitor(root)
    load = Image.open('logo.png')
    render = ImageTk.PhotoImage(load)
    root.iconphoto(False, render)
    
    root.mainloop()

if __name__ == "__main__":
    main()
