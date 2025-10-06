# portfolio_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class PortfolioWindow:
    """
    Окно для управления портфелем акций с автоматическим обновлением цен с MOEX
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Мой портфель акций")
        self.window.geometry("1000x600")
        self.window.minsize(800, 400)
        
        # Данные портфеля
        self.portfolio_data = []
        self.load_portfolio_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление цен при открытии
        self.update_all_prices()
        
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    def create_widgets(self):
        """Создание элементов интерфейса портфеля"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Мой портфель акций", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Поля для ввода новой акции
        input_frame = ttk.Frame(control_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Тикер:").pack(side=tk.LEFT, padx=2)
        self.ticker_var = tk.StringVar()
        self.ticker_entry = ttk.Entry(input_frame, textvariable=self.ticker_var, width=10)
        self.ticker_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Количество:").pack(side=tk.LEFT, padx=2)
        self.quantity_var = tk.StringVar()
        self.quantity_entry = ttk.Entry(input_frame, textvariable=self.quantity_var, width=10)
        self.quantity_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Цена покупки:").pack(side=tk.LEFT, padx=2)
        self.buy_price_var = tk.StringVar()
        self.buy_price_entry = ttk.Entry(input_frame, textvariable=self.buy_price_var, width=10)
        self.buy_price_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(input_frame, text="Добавить акцию", 
                  command=self.add_stock).pack(side=tk.LEFT, padx=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Обновить все цены", 
                  command=self.update_all_prices).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить выбранное", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить портфель", 
                  command=self.clear_portfolio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт в CSV", 
                  command=self.export_to_csv).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Импорт из CSV", 
                  command=self.import_from_csv).pack(side=tk.RIGHT, padx=5)
        
        # Таблица портфеля
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.create_portfolio_table(table_frame)
        
        # Статистика портфеля
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X)
        
        self.stats_label = ttk.Label(stats_frame, 
                                    text="Общая стоимость: 0.00 руб | Прибыль: 0.00 руб (0.00%)",
                                    font=("Arial", 10, "bold"))
        self.stats_label.pack()
        
        # Обновление статистики
        self.update_statistics()
    
    def create_portfolio_table(self, parent):
        """Создание таблицы портфеля"""
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Создание Treeview
        columns = ("ticker", "name", "quantity", "buy_price", "current_price", 
                  "current_value", "buy_value", "profit", "profit_percent")
        
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        headers = {
            "ticker": "Тикер",
            "name": "Название",
            "quantity": "Кол-во",
            "buy_price": "Цена покупки",
            "current_price": "Текущая цена",
            "current_value": "Текущая стоимость",
            "buy_value": "Стоимость покупки",
            "profit": "Прибыль",
            "profit_percent": "Прибыль %"
        }
        
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=100, minwidth=80)
        
        # Добавление прокрутки
        v_scroll = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Размещение элементов
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        
        # Заполнение таблицы данными
        self.refresh_table()
    
    def refresh_table(self):
        """Обновление данных в таблице"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполняем данными
        for stock in self.portfolio_data:
            self.tree.insert("", tk.END, values=(
                stock['ticker'],
                stock.get('name', ''),
                stock['quantity'],
                f"{stock['buy_price']:.2f}",
                f"{stock.get('current_price', 0):.2f}",
                f"{stock.get('current_value', 0):.2f}",
                f"{stock.get('buy_value', 0):.2f}",
                f"{stock.get('profit', 0):.2f}",
                f"{stock.get('profit_percent', 0):.2f}%"
            ))
    
    def add_stock(self):
        """Добавление новой акции в портфель"""
        ticker = self.ticker_var.get().strip().upper()
        quantity = self.quantity_var.get().strip()
        buy_price = self.buy_price_var.get().strip()
        
        if not ticker or not quantity or not buy_price:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        
        try:
            quantity = int(quantity)
            buy_price = float(buy_price)
            
            if quantity <= 0 or buy_price <= 0:
                messagebox.showerror("Ошибка", "Количество и цена должны быть положительными")
                return
            
            # Проверяем, есть ли уже такая акция
            for stock in self.portfolio_data:
                if stock['ticker'] == ticker:
                    if messagebox.askyesno("Подтверждение", 
                                         f"Акция {ticker} уже есть в портфеле. Обновить данные?"):
                        stock['quantity'] = quantity
                        stock['buy_price'] = buy_price
                        self.calculate_stock_values(stock)
                        self.refresh_table()
                        self.update_statistics()
                        self.save_portfolio_data()
                        self.clear_input_fields()
                    return
            
            # Добавляем новую акцию
            stock_data = {
                'ticker': ticker,
                'quantity': quantity,
                'buy_price': buy_price,
                'added_date': datetime.now().isoformat()
            }
            
            # Получаем текущую цену и название
            self.update_stock_price(stock_data)
            self.portfolio_data.append(stock_data)
            
            self.refresh_table()
            self.update_statistics()
            self.save_portfolio_data()
            self.clear_input_fields()
            
            messagebox.showinfo("Успех", f"Акция {ticker} добавлена в портфель")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    def clear_input_fields(self):
        """Очистка полей ввода"""
        self.ticker_var.set("")
        self.quantity_var.set("")
        self.buy_price_var.set("")
        self.ticker_entry.focus()
    
    def update_stock_price(self, stock_data):
        """Обновление текущей цены акции с MOEX"""
        try:
            ticker = stock_data['ticker']
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                market_data = data['marketdata']['data']
                
                if market_data:
                    stock_info = market_data[0]
                    current_price = stock_info[12]  # LAST цена
                    
                    if current_price is None:
                        current_price = stock_info[3]  # LCURRENTPRICE
                    
                    if current_price is not None:
                        stock_data['current_price'] = current_price
                        
                        # Получаем название акции
                        securities_data = data['securities']['data']
                        if securities_data:
                            stock_data['name'] = securities_data[0][2]  # SHORTNAME
                        
                        # Пересчитываем значения
                        self.calculate_stock_values(stock_data)
                        return True
            
            # Если не удалось получить данные, используем цену покупки
            stock_data['current_price'] = stock_data['buy_price']
            stock_data['name'] = ticker
            self.calculate_stock_values(stock_data)
            return False
            
        except Exception as e:
            print(f"Ошибка получения цены для {stock_data['ticker']}: {e}")
            stock_data['current_price'] = stock_data['buy_price']
            stock_data['name'] = stock_data['ticker']
            self.calculate_stock_values(stock_data)
            return False
    
    def calculate_stock_values(self, stock_data):
        """Расчет стоимости и прибыли для акции"""
        quantity = stock_data['quantity']
        buy_price = stock_data['buy_price']
        current_price = stock_data.get('current_price', buy_price)
        
        stock_data['buy_value'] = quantity * buy_price
        stock_data['current_value'] = quantity * current_price
        stock_data['profit'] = stock_data['current_value'] - stock_data['buy_value']
        
        if stock_data['buy_value'] > 0:
            stock_data['profit_percent'] = (stock_data['profit'] / stock_data['buy_value']) * 100
        else:
            stock_data['profit_percent'] = 0
    
    def update_all_prices(self):
        """Обновление цен для всех акций в портфеле"""
        if not self.portfolio_data:
            messagebox.showinfo("Информация", "Портфель пуст")
            return
        
        progress_window = tk.Toplevel(self.window)
        progress_window.title("Обновление цен")
        progress_window.geometry("300x100")
        progress_window.transient(self.window)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Обновление цен...").pack(pady=10)
        progress = ttk.Progressbar(progress_window, mode='indeterminate')
        progress.pack(pady=10, padx=20, fill=tk.X)
        progress.start()
        
        def update_prices():
            updated_count = 0
            for stock in self.portfolio_data:
                if self.update_stock_price(stock):
                    updated_count += 1
            
            self.window.after(0, lambda: finish_update(updated_count))
        
        def finish_update(updated_count):
            progress.stop()
            progress_window.destroy()
            self.refresh_table()
            self.update_statistics()
            self.save_portfolio_data()
            messagebox.showinfo("Обновление", 
                              f"Цены обновлены для {updated_count} из {len(self.portfolio_data)} акций")
        
        # Запускаем в отдельном потоке
        import threading
        thread = threading.Thread(target=update_prices)
        thread.daemon = True
        thread.start()
    
    def delete_selected(self):
        """Удаление выбранной акции из портфеля"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите акцию для удаления")
            return
        
        for item in selected:
            values = self.tree.item(item, "values")
            ticker = values[0]
            
            # Удаляем из данных
            self.portfolio_data = [s for s in self.portfolio_data if s['ticker'] != ticker]
        
        self.refresh_table()
        self.update_statistics()
        self.save_portfolio_data()
        messagebox.showinfo("Успех", "Акции удалены из портфеля")
    
    def clear_portfolio(self):
        """Очистка всего портфеля"""
        if not self.portfolio_data:
            return
        
        if messagebox.askyesno("Подтверждение", "Очистить весь портфель?"):
            self.portfolio_data.clear()
            self.refresh_table()
            self.update_statistics()
            self.save_portfolio_data()
    
    def update_statistics(self):
        """Обновление статистики портфеля"""
        total_buy_value = sum(stock.get('buy_value', 0) for stock in self.portfolio_data)
        total_current_value = sum(stock.get('current_value', 0) for stock in self.portfolio_data)
        total_profit = total_current_value - total_buy_value
        
        if total_buy_value > 0:
            total_profit_percent = (total_profit / total_buy_value) * 100
        else:
            total_profit_percent = 0
        
        profit_color = "green" if total_profit >= 0 else "red"
        
        stats_text = (f"Общая стоимость: {total_current_value:,.2f} руб | "
                     f"Прибыль: {total_profit:,.2f} руб ({total_profit_percent:.2f}%)")
        
        self.stats_label.config(text=stats_text)
        
        # Динамическое изменение цвета прибыли
        if hasattr(self.stats_label, 'config'):
            self.stats_label.config(foreground=profit_color)
    
    def load_portfolio_data(self):
        """Загрузка данных портфеля из файла"""
        try:
            if os.path.exists('portfolio_data.json'):
                with open('portfolio_data.json', 'r', encoding='utf-8') as f:
                    self.portfolio_data = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки портфеля: {e}")
            self.portfolio_data = []
    
    def save_portfolio_data(self):
        """Сохранение данных портфеля в файл"""
        try:
            with open('portfolio_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.portfolio_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения портфеля: {e}")
    
    def export_to_csv(self):
        """Экспорт портфеля в CSV"""
        try:
            if not self.portfolio_data:
                messagebox.showwarning("Экспорт", "Портфель пуст")
                return
            
            filename = f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                
                # Заголовки
                headers = ["Тикер", "Название", "Количество", "Цена покупки", 
                          "Текущая цена", "Текущая стоимость", "Стоимость покупки",
                          "Прибыль", "Прибыль %"]
                writer.writerow(headers)
                
                # Данные
                for stock in self.portfolio_data:
                    writer.writerow([
                        stock['ticker'],
                        stock.get('name', ''),
                        stock['quantity'],
                        f"{stock['buy_price']:.2f}",
                        f"{stock.get('current_price', 0):.2f}",
                        f"{stock.get('current_value', 0):.2f}",
                        f"{stock.get('buy_value', 0):.2f}",
                        f"{stock.get('profit', 0):.2f}",
                        f"{stock.get('profit_percent', 0):.2f}%"
                    ])
            
            messagebox.showinfo("Экспорт", f"Портфель экспортирован в файл:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать портфель: {e}")
    
    def import_from_csv(self):
        """Импорт портфеля из CSV"""
        # Реализация импорта может быть добавлена при необходимости
        messagebox.showinfo("Информация", "Функция импорта будет реализована в следующей версии")
    
    def focus(self):
        """Активация окна"""
        self.window.focus_force()
    
    def close(self):
        """Закрытие окна"""
        self.save_portfolio_data()
        self.window.destroy()