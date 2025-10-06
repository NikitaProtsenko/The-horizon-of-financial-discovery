# main.py
from stock_monitor import StockMonitor
import tkinter as tk

def main():
    """
    Главная функция приложения.
    Создает главное окно и запускает монитор акций.
    """
    root = tk.Tk()
    app = StockMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
