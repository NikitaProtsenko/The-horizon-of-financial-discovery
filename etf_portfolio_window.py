# etf_portfolio_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from commission_manager import CommissionManager


class ETFPortfolioWindow:
    """
    Окно для управления портфелем ETF с автоматическим обновлением цен с MOEX
    и специализированными функциями для фондов
    """
    
    def __init__(self, parent, data_handler=None):
        self.parent = parent
        self.data_handler = data_handler
        self.commission_manager = CommissionManager(parent)
        self.window = tk.Toplevel(parent)
        self.window.title("Мой портфель ETF")
        self.window.geometry("1200x700")
        self.window.minsize(900, 400)
        
        # Данные портфеля ETF
        self.etf_portfolio_data = []
        self.load_etf_portfolio_data()
        
        # Переменные для ввода продажи
        self.sell_quantity_var = tk.StringVar()
        self.sell_price_var = tk.StringVar()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление цен при открытии
        self.update_all_prices()
        
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    def create_widgets(self):
        """Создание элементов интерфейса портфеля ETF"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Мой портфель ETF", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Информация о ETF
        info_frame = ttk.LabelFrame(main_frame, text="Информация о ETF", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = ("ETF (Exchange Traded Fund) - биржевые инвестиционные фонды.\n"
                    "Доходность ETF включает купонные выплаты и изменение цены.\n"
                    "Для ETF обычно применяется льготное налогообложение.")
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Arial", 9)).pack()
        
        # Панель управления - добавление ETF
        add_frame = ttk.LabelFrame(main_frame, text="Добавление ETF", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Тикер ETF:").pack(side=tk.LEFT, padx=2)
        self.ticker_var = tk.StringVar()
        self.ticker_entry = ttk.Entry(input_frame, textvariable=self.ticker_var, width=12)
        self.ticker_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Количество:").pack(side=tk.LEFT, padx=2)
        self.quantity_var = tk.StringVar()
        self.quantity_entry = ttk.Entry(input_frame, textvariable=self.quantity_var, width=10)
        self.quantity_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Цена покупки:").pack(side=tk.LEFT, padx=2)
        self.buy_price_var = tk.StringVar()
        self.buy_price_entry = ttk.Entry(input_frame, textvariable=self.buy_price_var, width=10)
        self.buy_price_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Дивидендная yield (%):").pack(side=tk.LEFT, padx=2)
        self.dividend_yield_var = tk.StringVar(value="0")
        self.dividend_yield_entry = ttk.Entry(input_frame, textvariable=self.dividend_yield_var, width=8)
        self.dividend_yield_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(input_frame, text="Купить/Добавить", 
                  command=self.add_etf).pack(side=tk.LEFT, padx=10)
        
        # Панель управления - продажа ETF
        sell_frame = ttk.LabelFrame(main_frame, text="Продажа ETF", padding="10")
        sell_frame.pack(fill=tk.X, pady=(0, 10))
        
        sell_input_frame = ttk.Frame(sell_frame)
        sell_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sell_input_frame, text="Тикер ETF:").pack(side=tk.LEFT, padx=2)
        self.sell_ticker_var = tk.StringVar()
        self.sell_ticker_combo = ttk.Combobox(sell_input_frame, textvariable=self.sell_ticker_var, 
                                             width=12, state="readonly")
        self.sell_ticker_combo.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(sell_input_frame, text="Количество для продажи:").pack(side=tk.LEFT, padx=2)
        self.sell_quantity_entry = ttk.Entry(sell_input_frame, textvariable=self.sell_quantity_var, width=10)
        self.sell_quantity_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(sell_input_frame, text="Цена продажи:").pack(side=tk.LEFT, padx=2)
        self.sell_price_entry = ttk.Entry(sell_input_frame, textvariable=self.sell_price_var, width=10)
        self.sell_price_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(sell_input_frame, text="Продать", 
                  command=self.sell_etf).pack(side=tk.LEFT, padx=10)
        
        # Обновляем комбобокс при изменении портфеля
        self.update_sell_ticker_combo()
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Настройки комиссий", 
                  command=self.commission_manager.show_commission_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Расчет дивидендного дохода", 
                  command=self.show_dividend_calculation).pack(side=tk.LEFT, padx=5)
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
        
        # Таблица портфеля ETF
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.create_etf_portfolio_table(table_frame)
        
        # Статистика портфеля ETF
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X)
        
        self.stats_label = ttk.Label(stats_frame, 
                                    text="Общая стоимость: 0.00 руб | Прибыль: 0.00 руб (0.00%) | Годовой дивидендный доход: 0.00 руб",
                                    font=("Arial", 10, "bold"))
        self.stats_label.pack()
        
        # Обновление статистики
        self.update_statistics()
    
    def update_sell_ticker_combo(self):
        """Обновление списка тикеров ETF для продажи"""
        tickers = [etf['ticker'] for etf in self.etf_portfolio_data]
        self.sell_ticker_combo['values'] = tickers
        if tickers:
            self.sell_ticker_combo.set(tickers[0])
    
    def sell_etf(self):
        """Продажа ETF из портфеля"""
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
            
            # Ищем ETF в портфеле
            etf_to_sell = None
            for etf in self.etf_portfolio_data:
                if etf['ticker'] == ticker:
                    etf_to_sell = etf
                    break
            
            if not etf_to_sell:
                messagebox.showerror("Ошибка", f"ETF {ticker} не найден в портфеле")
                return
            
            current_quantity = etf_to_sell['quantity']
            
            if quantity_to_sell > current_quantity:
                messagebox.showerror("Ошибка", 
                                   f"Недостаточно ETF для продажи. Доступно: {current_quantity}")
                return
            
            # Расчет комиссий при продаже
            sell_amount = quantity_to_sell * sell_price
            commission_calc = self.commission_manager.calculate_sell_commission(sell_amount)
            total_commission = commission_calc['total_commission']
            
            # Расчет налога (для ETF часто льготное налогообложение)
            buy_price_per_share = etf_to_sell['total_cost'] / etf_to_sell['quantity']
            tax = self.commission_manager.calculate_tax(
                buy_price_per_share * quantity_to_sell, 
                sell_amount, 
                quantity_to_sell
            )
            
            # Чистая выручка от продажи
            net_proceeds = sell_amount - total_commission - tax
            
            # Подтверждение продажи
            confirm_msg = (f"Подтвердите продажу {quantity_to_sell} ETF {ticker} "
                          f"по цене {sell_price:.2f} руб?\n\n"
                          f"Выручка от продажи: {sell_amount:.2f} руб\n"
                          f"Комиссии: {total_commission:.2f} руб\n"
                          f"Налог: {tax:.2f} руб\n"
                          f"Чистая выручка: {net_proceeds:.2f} руб")
            
            if not messagebox.askyesno("Подтверждение продажи", confirm_msg):
                return
            
            # Регистрируем операцию продажи
            self.record_transaction(ticker, 'sell', quantity_to_sell, sell_price)
            
            # Обновляем количество ETF
            if quantity_to_sell == current_quantity:
                # Продали все ETF - удаляем из портфеля
                self.etf_portfolio_data.remove(etf_to_sell)
                messagebox.showinfo("Успех", f"Все ETF {ticker} проданы и удалены из портфеля")
            else:
                # Продали часть ETF - обновляем количество
                etf_to_sell['quantity'] = current_quantity - quantity_to_sell
                # Пересчитываем значения
                self.calculate_etf_values(etf_to_sell)
                messagebox.showinfo("Успех", 
                                  f"Продано {quantity_to_sell} ETF {ticker}. "
                                  f"Осталось: {etf_to_sell['quantity']}")
            
            # Обновляем интерфейс
            self.refresh_table()
            self.update_sell_ticker_combo()
            self.update_statistics()
            self.save_etf_portfolio_data()
            
            # Очищаем поля продажи
            self.sell_quantity_var.set("")
            self.sell_price_var.set("")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    def record_transaction(self, ticker, operation, quantity, price):
        """Запись операции в историю транзакций ETF"""
        try:
            # Загружаем существующую историю
            history = []
            history_file = 'etf_transaction_history.json'
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Добавляем новую операцию
            transaction = {
                'date': datetime.now().isoformat(),
                'ticker': ticker,
                'operation': operation,  # 'buy' или 'sell'
                'quantity': quantity,
                'price': price,
                'total': quantity * price,
                'asset_type': 'ETF'
            }
            
            history.append(transaction)
            
            # Сохраняем историю
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Ошибка сохранения истории транзакций ETF: {e}")
    
    def show_transaction_history(self):
        """Показать историю транзакций ETF"""
        try:
            history = []
            history_file = 'etf_transaction_history.json'
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            if not history:
                messagebox.showinfo("История операций", "История операций ETF пуста")
                return
            
            # Создаем окно истории
            history_window = tk.Toplevel(self.window)
            history_window.title("История операций ETF")
            history_window.geometry("800x400")
            
            # Таблица истории
            table_frame = ttk.Frame(history_window, padding="10")
            table_frame.pack(fill=tk.BOTH, expand=True)
            
            columns = ("date", "ticker", "operation", "quantity", "price", "total")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
            
            headers = {
                "date": "Дата и время",
                "ticker": "Тикер ETF",
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
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю операций ETF: {e}")
    
    def clear_transaction_history(self, parent_window):
        """Очистка истории транзакций ETF"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю операций ETF?"):
            try:
                with open('etf_transaction_history.json', 'w', encoding='utf-8') as f:
                    json.dump([], f)
                messagebox.showinfo("Успех", "История операций ETF очищена")
                parent_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось очистить историю: {e}")
    
    def create_etf_portfolio_table(self, parent):
        """Создание таблицы портфеля ETF с учетом дивидендной доходности"""
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Создание Treeview
        columns = ("ticker", "name", "quantity", "buy_price", "commission", 
                  "total_cost", "current_price", "current_value", 
                  "dividend_yield", "annual_dividend", "profit", "profit_percent")
        
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        headers = {
            "ticker": "Тикер ETF",
            "name": "Название",
            "quantity": "Кол-во",
            "buy_price": "Цена покупки",
            "commission": "Комиссия",
            "total_cost": "Общая стоимость",
            "current_price": "Текущая цена",
            "current_value": "Текущая стоимость",
            "dividend_yield": "Див. yield (%)",
            "annual_dividend": "Годовой дивиденд",
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
    
    def calculate_commission_costs(self, quantity, price):
        """Расчет комиссий при покупке"""
        total_amount = quantity * price
        commission_calc = self.commission_manager.calculate_buy_commission(total_amount)
        return commission_calc['total_commission']
    
    def add_etf(self):
        """Добавление нового ETF в портфель с учетом комиссий и дивидендной доходности"""
        ticker = self.ticker_var.get().strip().upper()
        quantity_str = self.quantity_var.get().strip()
        buy_price_str = self.buy_price_var.get().strip()
        dividend_yield_str = self.dividend_yield_var.get().strip()
        
        if not ticker or not quantity_str or not buy_price_str:
            messagebox.showerror("Ошибка", "Заполните все обязательные поля")
            return
        
        try:
            quantity = int(quantity_str)
            buy_price = float(buy_price_str)
            dividend_yield = float(dividend_yield_str) if dividend_yield_str else 0.0
            
            if quantity <= 0 or buy_price <= 0:
                messagebox.showerror("Ошибка", "Количество и цена должны быть положительными")
                return
            
            # Расчет комиссий
            commission = self.calculate_commission_costs(quantity, buy_price)
            total_cost = quantity * buy_price + commission
            
            # Проверяем, есть ли уже такой ETF
            existing_etf = None
            for etf in self.etf_portfolio_data:
                if etf['ticker'] == ticker:
                    existing_etf = etf
                    break
            
            if existing_etf:
                # Спрашиваем пользователя, что делать с существующим ETF
                choice = messagebox.askyesnocancel(
                    "ETF уже в портфеле", 
                    f"ETF {ticker} уже есть в портфеле.\n\n"
                    f"Текущее количество: {existing_etf['quantity']}\n"
                    f"Новое количество: {quantity}\n\n"
                    f"ДА - добавить к существующему количеству\n"
                    f"НЕТ - заменить количество\n"
                    f"ОТМЕНА - не добавлять"
                )
                
                if choice is None:  # Отмена
                    return
                elif choice:  # Да - добавить к существующему
                    # Рассчитываем среднюю цену покупки с учетом комиссий
                    total_quantity = existing_etf['quantity'] + quantity
                    total_investment = existing_etf['total_cost'] + total_cost
                    average_price = (total_investment - self.calculate_commission_costs(total_quantity, 0)) / total_quantity
                    
                    # Обновляем среднюю дивидендную доходность
                    current_dividend = existing_etf.get('dividend_yield', 0)
                    weighted_dividend = ((existing_etf['quantity'] * current_dividend) + 
                                       (quantity * dividend_yield)) / total_quantity
                    
                    existing_etf['quantity'] = total_quantity
                    existing_etf['buy_price'] = average_price
                    existing_etf['commission'] = existing_etf.get('commission', 0) + commission
                    existing_etf['total_cost'] = total_investment
                    existing_etf['dividend_yield'] = weighted_dividend
                    
                else:  # Нет - заменить количество и цену
                    existing_etf['quantity'] = quantity
                    existing_etf['buy_price'] = buy_price
                    existing_etf['commission'] = commission
                    existing_etf['total_cost'] = total_cost
                    existing_etf['dividend_yield'] = dividend_yield
                
                # Регистрируем операцию покупки
                self.record_transaction(ticker, 'buy', quantity, buy_price)
                
                # Обновляем данные ETF
                self.update_etf_price(existing_etf)
                self.refresh_table()
                self.update_statistics()
                self.save_etf_portfolio_data()
                self.clear_input_fields()
                self.update_sell_ticker_combo()
                
                messagebox.showinfo("Успех", f"ETF {ticker} обновлен в портфеле")
                return
            
            # Добавляем новый ETF (если не найден существующий)
            etf_data = {
                'ticker': ticker,
                'quantity': quantity,
                'buy_price': buy_price,
                'commission': commission,
                'total_cost': total_cost,
                'dividend_yield': dividend_yield,
                'added_date': datetime.now().isoformat()
            }
            
            # Регистрируем операцию покупки
            self.record_transaction(ticker, 'buy', quantity, buy_price)
            
            # Получаем текущую цену и название
            self.update_etf_price(etf_data)
            self.etf_portfolio_data.append(etf_data)
            
            self.refresh_table()
            self.update_statistics()
            self.save_etf_portfolio_data()
            self.clear_input_fields()
            self.update_sell_ticker_combo()
            
            messagebox.showinfo("Успех", f"ETF {ticker} добавлен в портфель")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    def clear_input_fields(self):
        """Очистка полей ввода"""
        self.ticker_var.set("")
        self.quantity_var.set("")
        self.buy_price_var.set("")
        self.dividend_yield_var.set("0")
        self.ticker_entry.focus()
    
    def update_etf_price(self, etf_data):
        """Обновление текущей цены ETF с MOEX"""
        try:
            ticker = etf_data['ticker']
            
            # Используем data_handler если он доступен
            if self.data_handler:
                # Сохраняем текущий тикер
                original_ticker = self.data_handler.ticker
                # Временно меняем тикер
                self.data_handler.set_ticker(ticker)
                data = self.data_handler.get_stock_data()
                # Восстанавливаем оригинальный тикер
                self.data_handler.set_ticker(original_ticker)
                
                if data['success']:
                    etf_data['current_price'] = data['price']
                    etf_data['name'] = ticker  # MOEX API не всегда возвращает название
                    self.calculate_etf_values(etf_data)
                    return True
            else:
                # Альтернативный способ получения данных
                url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    market_data = data['marketdata']['data']
                    
                    if market_data:
                        etf_info = market_data[0]
                        current_price = etf_info[12]  # LAST цена
                        
                        if current_price is None:
                            current_price = etf_info[3]  # LCURRENTPRICE
                        
                        if current_price is not None:
                            etf_data['current_price'] = current_price
                            
                            # Получаем название ETF
                            securities_data = data['securities']['data']
                            if securities_data:
                                etf_data['name'] = securities_data[0][2]  # SHORTNAME
                            
                            # Пересчитываем значения
                            self.calculate_etf_values(etf_data)
                            return True
            
            # Если не удалось получить данные, используем цену покупки
            etf_data['current_price'] = etf_data['buy_price']
            etf_data['name'] = ticker
            self.calculate_etf_values(etf_data)
            return False
            
        except Exception as e:
            print(f"Ошибка получения цены для {etf_data['ticker']}: {e}")
            etf_data['current_price'] = etf_data['buy_price']
            etf_data['name'] = etf_data['ticker']
            self.calculate_etf_values(etf_data)
            return False
    
    def calculate_etf_values(self, etf_data):
        """Расчет стоимости, прибыли и дивидендного дохода для ETF"""
        try:
            quantity = etf_data['quantity']
            current_price = etf_data.get('current_price', etf_data['buy_price'])
            dividend_yield = etf_data.get('dividend_yield', 0)
            
            # Инициализируем необходимые поля если их нет
            if 'total_cost' not in etf_data:
                etf_data['total_cost'] = quantity * etf_data['buy_price'] + etf_data.get('commission', 0)
            
            etf_data['current_value'] = quantity * current_price
            etf_data['profit'] = etf_data['current_value'] - etf_data['total_cost']
            
            if etf_data['total_cost'] > 0:
                etf_data['profit_percent'] = (etf_data['profit'] / etf_data['total_cost']) * 100
            else:
                etf_data['profit_percent'] = 0
            
            # Расчет годового дивидендного дохода
            etf_data['annual_dividend'] = etf_data['current_value'] * (dividend_yield / 100)
            
        except KeyError as e:
            print(f"Ошибка расчета значений для ETF {etf_data.get('ticker', 'unknown')}: {e}")
            # Устанавливаем значения по умолчанию
            etf_data['current_value'] = 0
            etf_data['profit'] = 0
            etf_data['profit_percent'] = 0
            etf_data['annual_dividend'] = 0
    
    def refresh_table(self):
        """Обновление данных в таблице"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполняем данными
        for etf in self.etf_portfolio_data:
            # Убедимся, что все необходимые поля существуют
            if 'total_cost' not in etf:
                etf['total_cost'] = etf['quantity'] * etf['buy_price'] + etf.get('commission', 0)
            if 'current_value' not in etf:
                etf['current_value'] = etf['quantity'] * etf.get('current_price', etf['buy_price'])
            if 'profit' not in etf:
                etf['profit'] = etf['current_value'] - etf['total_cost']
            if 'profit_percent' not in etf:
                if etf['total_cost'] > 0:
                    etf['profit_percent'] = (etf['profit'] / etf['total_cost']) * 100
                else:
                    etf['profit_percent'] = 0
            if 'annual_dividend' not in etf:
                etf['annual_dividend'] = etf['current_value'] * (etf.get('dividend_yield', 0) / 100)
            
            profit = etf.get('profit', 0)
            profit_percent = etf.get('profit_percent', 0)
            
            self.tree.insert("", tk.END, values=(
                etf['ticker'],
                etf.get('name', ''),
                etf['quantity'],
                f"{etf['buy_price']:.2f}",
                f"{etf.get('commission', 0):.2f}",
                f"{etf.get('total_cost', 0):.2f}",
                f"{etf.get('current_price', 0):.2f}",
                f"{etf.get('current_value', 0):.2f}",
                f"{etf.get('dividend_yield', 0):.2f}%",
                f"{etf.get('annual_dividend', 0):.2f}",
                f"{profit:+.2f}",
                f"{profit_percent:+.2f}%"
            ))
    
    def update_statistics(self):
        """Обновление статистики портфеля ETF"""
        total_cost = sum(etf.get('total_cost', 0) for etf in self.etf_portfolio_data)
        total_current_value = sum(etf.get('current_value', 0) for etf in self.etf_portfolio_data)
        total_profit = total_current_value - total_cost
        total_annual_dividend = sum(etf.get('annual_dividend', 0) for etf in self.etf_portfolio_data)
        
        if total_cost > 0:
            total_profit_percent = (total_profit / total_cost) * 100
        else:
            total_profit_percent = 0
        
        profit_color = "green" if total_profit >= 0 else "red"
        
        stats_text = (f"Общая стоимость: {total_current_value:,.2f} руб | "
                     f"Прибыль: {total_profit:,.2f} руб ({total_profit_percent:.2f}%) | "
                     f"Годовой дивидендный доход: {total_annual_dividend:,.2f} руб")
        
        self.stats_label.config(text=stats_text, foreground=profit_color)
    
    def show_dividend_calculation(self):
        """Показать расчет дивидендного дохода"""
        if not self.etf_portfolio_data:
            messagebox.showwarning("Внимание", "Портфель ETF пуст")
            return
        
        dividend_window = tk.Toplevel(self.window)
        dividend_window.title("Расчет дивидендного дохода")
        dividend_window.geometry("600x500")
        
        main_frame = ttk.Frame(dividend_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Расчет дивидендного дохода по портфелю ETF", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Общая статистика дивидендов
        total_annual_dividend = sum(etf.get('annual_dividend', 0) for etf in self.etf_portfolio_data)
        total_current_value = sum(etf.get('current_value', 0) for etf in self.etf_portfolio_data)
        
        if total_current_value > 0:
            portfolio_dividend_yield = (total_annual_dividend / total_current_value) * 100
        else:
            portfolio_dividend_yield = 0
        
        stats_frame = ttk.LabelFrame(main_frame, text="Общая статистика дивидендов", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(stats_frame, text=f"Общий годовой дивидендный доход: {total_annual_dividend:,.2f} руб", 
                 font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=2)
        ttk.Label(stats_frame, text=f"Средняя дивидендная доходность портфеля: {portfolio_dividend_yield:.2f}%", 
                 font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=2)
        ttk.Label(stats_frame, text=f"Ежемесячный дивидендный доход: {total_annual_dividend / 12:,.2f} руб", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(stats_frame, text=f"Ежеквартальный дивидендный доход: {total_annual_dividend / 4:,.2f} руб", 
                 font=("Arial", 10)).pack(anchor=tk.W, pady=2)
        
        # Детали по каждому ETF
        details_frame = ttk.LabelFrame(main_frame, text="Детали по ETF", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем таблицу для деталей
        columns = ("ticker", "dividend_yield", "annual_dividend", "percent_of_total")
        tree = ttk.Treeview(details_frame, columns=columns, show="headings", height=8)
        
        headers = {
            "ticker": "Тикер ETF",
            "dividend_yield": "Див. yield (%)",
            "annual_dividend": "Годовой дивиденд",
            "percent_of_total": "% от общего дохода"
        }
        
        for col in columns:
            tree.heading(col, text=headers[col])
            tree.column(col, width=120, minwidth=100)
        
        # Заполняем таблицу
        for etf in self.etf_portfolio_data:
            annual_dividend = etf.get('annual_dividend', 0)
            if total_annual_dividend > 0:
                percent_of_total = (annual_dividend / total_annual_dividend) * 100
            else:
                percent_of_total = 0
            
            tree.insert("", tk.END, values=(
                etf['ticker'],
                f"{etf.get('dividend_yield', 0):.2f}%",
                f"{annual_dividend:,.2f} руб",
                f"{percent_of_total:.1f}%"
            ))
        
        # Прокрутка
        v_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=v_scroll.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка закрытия
        ttk.Button(main_frame, text="Закрыть", 
                  command=dividend_window.destroy).pack(pady=10)
    
    def update_all_prices(self):
        """Обновление цен всех ETF в портфеле"""
        if not self.etf_portfolio_data:
            messagebox.showinfo("Обновление цен", "Портфель ETF пуст")
            return
        
        progress_window = tk.Toplevel(self.window)
        progress_window.title("Обновление цен")
        progress_window.geometry("300x100")
        progress_window.transient(self.window)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Обновление цен ETF...", 
                 font=("Arial", 10)).pack(pady=10)
        
        progress = ttk.Progressbar(progress_window, mode='indeterminate')
        progress.pack(fill=tk.X, padx=20, pady=5)
        progress.start()
        
        # Обновляем цены в отдельном потоке
        def update_prices():
            updated_count = 0
            for etf in self.etf_portfolio_data:
                if self.update_etf_price(etf):
                    updated_count += 1
            
            progress_window.destroy()
            self.refresh_table()
            self.update_statistics()
            self.save_etf_portfolio_data()
            
            messagebox.showinfo("Обновление завершено", 
                              f"Цены обновлены для {updated_count} из {len(self.etf_portfolio_data)} ETF")
        
        # Запускаем обновление с небольшой задержкой для отображения прогресса
        self.window.after(100, update_prices)
    
    def delete_selected(self):
        """Удаление выбранного ETF из портфеля"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите ETF для удаления")
            return
        
        item = selection[0]
        values = self.tree.item(item)['values']
        ticker = values[0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить ETF {ticker} из портфеля?"):
            self.etf_portfolio_data = [etf for etf in self.etf_portfolio_data if etf['ticker'] != ticker]
            self.refresh_table()
            self.update_statistics()
            self.save_etf_portfolio_data()
            self.update_sell_ticker_combo()
            messagebox.showinfo("Успех", f"ETF {ticker} удален из портфеля")
    
    def clear_portfolio(self):
        """Полная очистка портфеля ETF"""
        if not self.etf_portfolio_data:
            messagebox.showinfo("Очистка", "Портфель ETF уже пуст")
            return
        
        if messagebox.askyesno("Подтверждение", 
                              "Вы уверены, что хотите полностью очистить портфель ETF?\n"
                              "Все данные будут удалены безвозвратно."):
            self.etf_portfolio_data = []
            self.refresh_table()
            self.update_statistics()
            self.save_etf_portfolio_data()
            self.update_sell_ticker_combo()
            messagebox.showinfo("Успех", "Портфель ETF очищен")
    
    def export_to_csv(self):
        """Экспорт портфеля ETF в CSV файл"""
        if not self.etf_portfolio_data:
            messagebox.showwarning("Внимание", "Портфель ETF пуст")
            return
        
        try:
            filename = f"etf_portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', encoding='utf-8') as f:
                # Заголовок
                f.write("Тикер;Название;Количество;Цена покупки;Комиссия;Общая стоимость;"
                       "Текущая цена;Текущая стоимость;Див. yield (%);Годовой дивиденд;"
                       "Прибыль;Прибыль %\n")
                
                # Данные
                for etf in self.etf_portfolio_data:
                    f.write(f"{etf['ticker']};"
                           f"{etf.get('name', '')};"
                           f"{etf['quantity']};"
                           f"{etf['buy_price']:.2f};"
                           f"{etf.get('commission', 0):.2f};"
                           f"{etf.get('total_cost', 0):.2f};"
                           f"{etf.get('current_price', 0):.2f};"
                           f"{etf.get('current_value', 0):.2f};"
                           f"{etf.get('dividend_yield', 0):.2f};"
                           f"{etf.get('annual_dividend', 0):.2f};"
                           f"{etf.get('profit', 0):.2f};"
                           f"{etf.get('profit_percent', 0):.2f}\n")
            
            messagebox.showinfo("Экспорт завершен", f"Портфель ETF экспортирован в файл:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")
    
    def load_etf_portfolio_data(self):
        """Загрузка данных портфеля ETF из файла"""
        try:
            if os.path.exists('etf_portfolio.json'):
                with open('etf_portfolio.json', 'r', encoding='utf-8') as f:
                    self.etf_portfolio_data = json.load(f)
                    
                # Убедимся, что все ETF имеют правильные расчеты
                for etf in self.etf_portfolio_data:
                    self.calculate_etf_values(etf)
        except Exception as e:
            print(f"Ошибка загрузки портфеля ETF: {e}")
            self.etf_portfolio_data = []
    
    def save_etf_portfolio_data(self):
        """Сохранение данных портфеля ETF в файл"""
        try:
            with open('etf_portfolio.json', 'w', encoding='utf-8') as f:
                json.dump(self.etf_portfolio_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения портфеля ETF: {e}")
    
    def close(self):
        """Закрытие окна портфеля ETF"""
        self.save_etf_portfolio_data()
        self.window.destroy()