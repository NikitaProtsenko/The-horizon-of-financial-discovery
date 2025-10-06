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
        self.window.geometry("1100x600")
        self.window.minsize(900, 400)
        
        # Данные портфеля
        self.portfolio_data = []
        self.load_portfolio_data()
        
        # Переменные для ввода продажи
        self.sell_quantity_var = tk.StringVar()
        self.sell_price_var = tk.StringVar()
        
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
        
        # Панель управления - добавление акций
        add_frame = ttk.LabelFrame(main_frame, text="Добавление акций", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_frame = ttk.Frame(add_frame)
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
        
        ttk.Button(input_frame, text="Купить/Добавить", 
                  command=self.add_stock).pack(side=tk.LEFT, padx=10)
        
        # Панель управления - продажа акций
        sell_frame = ttk.LabelFrame(main_frame, text="Продажа акций", padding="10")
        sell_frame.pack(fill=tk.X, pady=(0, 10))
        
        sell_input_frame = ttk.Frame(sell_frame)
        sell_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sell_input_frame, text="Тикер:").pack(side=tk.LEFT, padx=2)
        self.sell_ticker_var = tk.StringVar()
        self.sell_ticker_combo = ttk.Combobox(sell_input_frame, textvariable=self.sell_ticker_var, 
                                             width=10, state="readonly")
        self.sell_ticker_combo.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(sell_input_frame, text="Количество для продажи:").pack(side=tk.LEFT, padx=2)
        self.sell_quantity_entry = ttk.Entry(sell_input_frame, textvariable=self.sell_quantity_var, width=10)
        self.sell_quantity_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(sell_input_frame, text="Цена продажи:").pack(side=tk.LEFT, padx=2)
        self.sell_price_entry = ttk.Entry(sell_input_frame, textvariable=self.sell_price_var, width=10)
        self.sell_price_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(sell_input_frame, text="Продать", 
                  command=self.sell_stock).pack(side=tk.LEFT, padx=10)
        
        # Обновляем комбобокс при изменении портфеля
        self.update_sell_ticker_combo()
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Обновить все цены", 
                  command=self.update_all_prices).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить выбранное", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить портфель", 
                  command=self.clear_portfolio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт в CSV", 
                  command=self.export_to_csv).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="История операций", 
                  command=self.show_transaction_history).pack(side=tk.RIGHT, padx=5)
        
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
    
    def update_sell_ticker_combo(self):
        """Обновление списка тикеров для продажи"""
        tickers = [stock['ticker'] for stock in self.portfolio_data]
        self.sell_ticker_combo['values'] = tickers
        if tickers:
            self.sell_ticker_combo.set(tickers[0])
    
    def sell_stock(self):
        """Продажа акций из портфеля"""
        ticker = self.sell_ticker_var.get().strip().upper()
        quantity_str = self.sell_quantity_var.get().strip()
        price_str = self.sell_price_var.get().strip()
        
        if not ticker or not quantity_str or not price_str:
            messagebox.showerror("Ошибка", "Заполните все поля для продажи")
            return
        
        try:
            quantity_to_sell = int(quantity_str)
            sell_price = float(price_str)
            
            if quantity_to_sell <= 0 or sell_price <= 0:
                messagebox.showerror("Ошибка", "Количество и цена должны быть положительными")
                return
            
            # Ищем акцию в портфеле
            stock_to_sell = None
            for stock in self.portfolio_data:
                if stock['ticker'] == ticker:
                    stock_to_sell = stock
                    break
            
            if not stock_to_sell:
                messagebox.showerror("Ошибка", f"Акция {ticker} не найдена в портфеле")
                return
            
            current_quantity = stock_to_sell['quantity']
            
            if quantity_to_sell > current_quantity:
                messagebox.showerror("Ошибка", 
                                   f"Недостаточно акций для продажи. Доступно: {current_quantity}")
                return
            
            # Подтверждение продажи
            confirm_msg = (f"Подтвердите продажу {quantity_to_sell} акций {ticker} "
                          f"по цене {sell_price:.2f} руб?\n\n"
                          f"Выручка от продажи: {quantity_to_sell * sell_price:.2f} руб")
            
            if not messagebox.askyesno("Подтверждение продажи", confirm_msg):
                return
            
            # Регистрируем операцию продажи
            self.record_transaction(ticker, 'sell', quantity_to_sell, sell_price)
            
            # Обновляем количество акций
            if quantity_to_sell == current_quantity:
                # Продали все акции - удаляем из портфеля
                self.portfolio_data.remove(stock_to_sell)
                messagebox.showinfo("Успех", f"Все акции {ticker} проданы и удалены из портфеля")
            else:
                # Продали часть акций - обновляем количество
                stock_to_sell['quantity'] = current_quantity - quantity_to_sell
                # Пересчитываем значения
                self.calculate_stock_values(stock_to_sell)
                messagebox.showinfo("Успех", 
                                  f"Продано {quantity_to_sell} акций {ticker}. "
                                  f"Осталось: {stock_to_sell['quantity']}")
            
            # Обновляем интерфейс
            self.refresh_table()
            self.update_sell_ticker_combo()
            self.update_statistics()
            self.save_portfolio_data()
            
            # Очищаем поля продажи
            self.sell_quantity_var.set("")
            self.sell_price_var.set("")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    def record_transaction(self, ticker, operation, quantity, price):
        """Запись операции в историю транзакций"""
        try:
            # Загружаем существующую историю
            history = []
            if os.path.exists('transaction_history.json'):
                with open('transaction_history.json', 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Добавляем новую операцию
            transaction = {
                'date': datetime.now().isoformat(),
                'ticker': ticker,
                'operation': operation,  # 'buy' или 'sell'
                'quantity': quantity,
                'price': price,
                'total': quantity * price
            }
            
            history.append(transaction)
            
            # Сохраняем историю
            with open('transaction_history.json', 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Ошибка сохранения истории транзакций: {e}")
    
    def show_transaction_history(self):
        """Показать историю транзакций"""
        try:
            history = []
            if os.path.exists('transaction_history.json'):
                with open('transaction_history.json', 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            if not history:
                messagebox.showinfo("История операций", "История операций пуста")
                return
            
            # Создаем окно истории
            history_window = tk.Toplevel(self.window)
            history_window.title("История операций")
            history_window.geometry("800x400")
            
            # Таблица истории
            table_frame = ttk.Frame(history_window, padding="10")
            table_frame.pack(fill=tk.BOTH, expand=True)
            
            columns = ("date", "ticker", "operation", "quantity", "price", "total")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
            
            headers = {
                "date": "Дата и время",
                "ticker": "Тикер",
                "operation": "Операция",
                "quantity": "Количество",
                "price": "Цена",
                "total": "Сумма"
            }
            
            for col in columns:
                tree.heading(col, text=headers[col])
                tree.column(col, width=120, minwidth=100)
            
            # Заполняем данными
            for transaction in reversed(history[-100:]):  # Последние 100 операций
                operation_text = "Покупка" if transaction['operation'] == 'buy' else "Продажа"
                operation_color = "green" if transaction['operation'] == 'buy' else "red"
                
                date_obj = datetime.fromisoformat(transaction['date'])
                date_str = date_obj.strftime("%d.%m.%Y %H:%M")
                
                tree.insert("", tk.END, values=(
                    date_str,
                    transaction['ticker'],
                    operation_text,
                    transaction['quantity'],
                    f"{transaction['price']:.2f}",
                    f"{transaction['total']:.2f}"
                ))
            
            # Прокрутка
            v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=v_scroll.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Кнопки
            button_frame = ttk.Frame(history_window)
            button_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(button_frame, text="Очистить историю", 
                      command=lambda: self.clear_transaction_history(history_window)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Закрыть", 
                      command=history_window.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю операций: {e}")
    
    def clear_transaction_history(self, parent_window):
        """Очистка истории транзакций"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю операций?"):
            try:
                with open('transaction_history.json', 'w', encoding='utf-8') as f:
                    json.dump([], f)
                messagebox.showinfo("Успех", "История операций очищена")
                parent_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось очистить историю: {e}")
    
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
            profit = stock.get('profit', 0)
            profit_percent = stock.get('profit_percent', 0)
            
            self.tree.insert("", tk.END, values=(
                stock['ticker'],
                stock.get('name', ''),
                stock['quantity'],
                f"{stock['buy_price']:.2f}",
                f"{stock.get('current_price', 0):.2f}",
                f"{stock.get('current_value', 0):.2f}",
                f"{stock.get('buy_value', 0):.2f}",
                f"{profit:+.2f}",
                f"{profit_percent:+.2f}%"
            ))
    
    def add_stock(self):
        """Добавление новой акции в портфель или обновление существующей"""
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
            existing_stock = None
            for stock in self.portfolio_data:
                if stock['ticker'] == ticker:
                    existing_stock = stock
                    break
            
            if existing_stock:
                # Спрашиваем пользователя, что делать с существующей акцией
                choice = messagebox.askyesnocancel(
                    "Акция уже в портфеле", 
                    f"Акция {ticker} уже есть в портфеле.\n\n"
                    f"Текущее количество: {existing_stock['quantity']}\n"
                    f"Новое количество: {quantity}\n\n"
                    f"ДА - добавить к существующему количеству\n"
                    f"НЕТ - заменить количество\n"
                    f"ОТМЕНА - не добавлять"
                )
                
                if choice is None:  # Отмена
                    return
                elif choice:  # Да - добавить к существующему
                    # Рассчитываем среднюю цену покупки
                    total_quantity = existing_stock['quantity'] + quantity
                    total_cost = (existing_stock['quantity'] * existing_stock['buy_price'] + 
                                quantity * buy_price)
                    average_price = total_cost / total_quantity
                    
                    existing_stock['quantity'] = total_quantity
                    existing_stock['buy_price'] = average_price
                    
                else:  # Нет - заменить количество и цену
                    existing_stock['quantity'] = quantity
                    existing_stock['buy_price'] = buy_price
                
                # Регистрируем операцию покупки
                self.record_transaction(ticker, 'buy', quantity, buy_price)
                
                # Обновляем данные акции
                self.calculate_stock_values(existing_stock)
                self.refresh_table()
                self.update_statistics()
                self.save_portfolio_data()
                self.clear_input_fields()
                self.update_sell_ticker_combo()
                
                messagebox.showinfo("Успех", f"Акция {ticker} обновлена в портфеле")
                return
            
            # Добавляем новую акцию (если не найдена существующая)
            stock_data = {
                'ticker': ticker,
                'quantity': quantity,
                'buy_price': buy_price,
                'added_date': datetime.now().isoformat()
            }
            
            # Регистрируем операцию покупки
            self.record_transaction(ticker, 'buy', quantity, buy_price)
            
            # Получаем текущую цену и название
            self.update_stock_price(stock_data)
            self.portfolio_data.append(stock_data)
            
            self.refresh_table()
            self.update_statistics()
            self.save_portfolio_data()
            self.clear_input_fields()
            self.update_sell_ticker_combo()
            
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
        self.update_sell_ticker_combo()
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
            self.update_sell_ticker_combo()
    
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
        
        self.stats_label.config(text=stats_text, foreground=profit_color)
    
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
        messagebox.showinfo("Информация", "Функция импорта будет реализована в следующей версии")
    
    def focus(self):
        """Активация окна"""
        self.window.focus_force()
    
    def close(self):
        """Закрытие окна"""
        self.save_portfolio_data()
        self.window.destroy()