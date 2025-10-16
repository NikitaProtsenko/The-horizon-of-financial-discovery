# etf_portfolio/etf_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class ETFUIComponents:
    """
    Компоненты пользовательского интерфейса для портфеля ETF
    """
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        
        # Переменные для ввода
        self.ticker_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.buy_price_var = tk.StringVar()
        self.dividend_yield_var = tk.StringVar(value="0")
        self.sell_ticker_var = tk.StringVar()
        self.sell_quantity_var = tk.StringVar()
        self.sell_price_var = tk.StringVar()
        
        self.tree = None
        self.stats_label = None
        self.sell_ticker_combo = None
    
    def create_main_interface(self):
        """Создание основного интерфейса"""
        main_frame = ttk.Frame(self.parent, padding="10")
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
        self.ticker_entry = ttk.Entry(input_frame, textvariable=self.ticker_var, width=12)
        self.ticker_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Количество:").pack(side=tk.LEFT, padx=2)
        self.quantity_entry = ttk.Entry(input_frame, textvariable=self.quantity_var, width=10)
        self.quantity_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Цена покупки:").pack(side=tk.LEFT, padx=2)
        self.buy_price_entry = ttk.Entry(input_frame, textvariable=self.buy_price_var, width=10)
        self.buy_price_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Дивидендная yield (%):").pack(side=tk.LEFT, padx=2)
        self.dividend_yield_entry = ttk.Entry(input_frame, textvariable=self.dividend_yield_var, width=8)
        self.dividend_yield_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(input_frame, text="Купить/Добавить", 
                  command=self.controller.add_etf).pack(side=tk.LEFT, padx=10)
        
        # Панель управления - продажа ETF
        sell_frame = ttk.LabelFrame(main_frame, text="Продажа ETF", padding="10")
        sell_frame.pack(fill=tk.X, pady=(0, 10))
        
        sell_input_frame = ttk.Frame(sell_frame)
        sell_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sell_input_frame, text="Тикер ETF:").pack(side=tk.LEFT, padx=2)
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
                  command=self.controller.sell_etf).pack(side=tk.LEFT, padx=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Настройки комиссий", 
                  command=self.controller.show_commission_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Расчет дивидендного дохода", 
                  command=self.controller.show_dividend_calculation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить все цены", 
                  command=self.controller.update_all_prices).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить выбранное", 
                  command=self.controller.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить портфель", 
                  command=self.controller.clear_portfolio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт в CSV", 
                  command=self.controller.export_to_csv).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="История операций", 
                  command=self.controller.show_transaction_history).pack(side=tk.RIGHT, padx=5)
        
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
    
    def create_etf_portfolio_table(self, parent):
        """Создание таблицы портфеля ETF"""
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
    
    def get_input_values(self):
        """Получение значений из полей ввода"""
        return {
            'ticker': self.ticker_var.get(),
            'quantity': self.quantity_var.get(),
            'buy_price': self.buy_price_var.get(),
            'dividend_yield': self.dividend_yield_var.get()
        }
    
    def get_sell_input_values(self):
        """Получение значений из полей продажи"""
        return {
            'ticker': self.sell_ticker_var.get(),
            'quantity': self.sell_quantity_var.get(),
            'price': self.sell_price_var.get()
        }
    
    def get_selected_ticker(self):
        """Получение выбранного тикера из таблицы"""
        if self.tree:
            selection = self.tree.selection()
            if selection:
                item = selection[0]
                values = self.tree.item(item)['values']
                return values[0]
        return None
    
    def refresh_table(self, portfolio_data):
        """Обновление данных в таблице"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполняем данными
        for etf in portfolio_data:
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
    
    def update_statistics(self, portfolio_data):
        """Обновление статистики портфеля ETF"""
        total_cost = sum(etf.get('total_cost', 0) for etf in portfolio_data)
        total_current_value = sum(etf.get('current_value', 0) for etf in portfolio_data)
        total_profit = total_current_value - total_cost
        total_annual_dividend = sum(etf.get('annual_dividend', 0) for etf in portfolio_data)
        
        if total_cost > 0:
            total_profit_percent = (total_profit / total_cost) * 100
        else:
            total_profit_percent = 0
        
        profit_color = "green" if total_profit >= 0 else "red"
        
        stats_text = (f"Общая стоимость: {total_current_value:,.2f} руб | "
                     f"Прибыль: {total_profit:,.2f} руб ({total_profit_percent:.2f}%) | "
                     f"Годовой дивидендный доход: {total_annual_dividend:,.2f} руб")
        
        self.stats_label.config(text=stats_text, foreground=profit_color)
    
    def update_sell_ticker_combo(self, tickers):
        """Обновление списка тикеров ETF для продажи"""
        self.sell_ticker_combo['values'] = tickers
        if tickers:
            self.sell_ticker_combo.set(tickers[0])
    
    def show_dividend_calculation(self, portfolio_data):
        """Показать расчет дивидендного дохода"""
        dividend_window = tk.Toplevel(self.parent)
        dividend_window.title("Расчет дивидендного дохода")
        dividend_window.geometry("600x500")
        
        main_frame = ttk.Frame(dividend_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Расчет дивидендного дохода по портфелю ETF", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Общая статистика дивидендов
        total_annual_dividend = sum(etf.get('annual_dividend', 0) for etf in portfolio_data)
        total_current_value = sum(etf.get('current_value', 0) for etf in portfolio_data)
        
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
        for etf in portfolio_data:
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
    
    def show_progress_dialog(self, message):
        """Показать диалог прогресса"""
        progress_window = tk.Toplevel(self.parent)
        progress_window.title("Обновление цен")
        progress_window.geometry("300x100")
        progress_window.transient(self.parent)
        progress_window.grab_set()
        progress_window.resizable(False, False)
        
        # Центрируем окно
        progress_window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - progress_window.winfo_width()) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - progress_window.winfo_height()) // 2
        progress_window.geometry(f"+{x}+{y}")
        
        ttk.Label(progress_window, text=message, 
                 font=("Arial", 10)).pack(pady=10)
        
        progress = ttk.Progressbar(progress_window, mode='indeterminate')
        progress.pack(fill=tk.X, padx=20, pady=5)
        progress.start()
        
        return progress_window