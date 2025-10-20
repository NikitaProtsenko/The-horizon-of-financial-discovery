# portfolio/ui_components.py
import tkinter as tk
from tkinter import ttk

class UIComponents:
    def __init__(self, parent_window, portfolio_manager, portfolio_window):
        self.window = parent_window
        self.portfolio_manager = portfolio_manager
        self.portfolio_window = portfolio_window  # Сохраняем ссылку на PortfolioWindow
        self.tree = None
        self.stats_label = None
        self.menu_bar = None
        
        # Переменные для ввода
        self.ticker_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.buy_price_var = tk.StringVar()
        self.sell_ticker_var = tk.StringVar()
        self.sell_quantity_var = tk.StringVar()
        self.sell_price_var = tk.StringVar()
        
        # Комбобокс для продажи
        self.sell_ticker_combo = None
    
    def create_widgets(self):
        """
        Создание всех элементов интерфейса портфеля.
        """
        # Создаем меню первым
        self.create_menu_bar()
        
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создание всех секций интерфейса
        self.create_header(main_frame)
        self.create_buy_section(main_frame)
        self.create_sell_section(main_frame)
        self.create_table(main_frame)
        self.create_statistics(main_frame)
        
        # Обновление статистики при запуске
        self.update_statistics()
    
    def create_menu_bar(self):
        """
        Создание меню сверху вместо кнопок.
        """
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)
        
        # Меню "Операции"
        operations_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Операции", menu=operations_menu)
        operations_menu.add_command(label="Купить/Добавить", command=self.portfolio_window.add_stock)
        operations_menu.add_command(label="Продать", command=self.portfolio_window.sell_stock)
        operations_menu.add_separator()
        operations_menu.add_command(label="Добавить дивиденды", command=lambda: self.portfolio_window.add_dividend_payment())
        
        # Меню "Управление"
        management_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Управление", menu=management_menu)
        management_menu.add_command(label="Удалить выбранное", command=self.portfolio_window.delete_selected)
        management_menu.add_command(label="Очистить портфель", command=self.portfolio_window.clear_portfolio)
        management_menu.add_separator()
        management_menu.add_command(label="Настройки комиссий", command=self.portfolio_manager.commission_manager.show_commission_settings)
        
        # Меню "Аналитика"
        analytics_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Аналитика", menu=analytics_menu)
        analytics_menu.add_command(label="Обновить все цены", command=self.portfolio_window.update_all_prices)
        analytics_menu.add_command(label="Сравнить с IMOEX", command=lambda: self.portfolio_window.show_index_comparison())
        analytics_menu.add_command(label="Графики портфеля", command=lambda: self.portfolio_window.show_portfolio_charts())
        
        # Меню "Отчеты"
        reports_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Отчеты", menu=reports_menu)
        reports_menu.add_command(label="История операций", command=lambda: self.portfolio_window.show_transaction_history())
        reports_menu.add_command(label="История дивидендов", command=lambda: self.portfolio_window.show_dividend_history())
        reports_menu.add_separator()
        reports_menu.add_command(label="Экспорт в CSV", command=self.portfolio_window.export_to_csv)
    
    def create_header(self, parent):
        """
        Создание заголовка окна.
        
        Args:
            parent: родительский контейнер
        """
        title_label = ttk.Label(parent, 
                               text="Мой портфель акций", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
    
    def create_buy_section(self, parent):
        """
        Создание секции покупки акций.
        
        Args:
            parent: родительский контейнер
        """
        add_frame = ttk.LabelFrame(parent, text="Добавление акций", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        # Поле ввода тикера
        ttk.Label(input_frame, text="Тикер:").pack(side=tk.LEFT, padx=2)
        self.ticker_entry = ttk.Entry(input_frame, textvariable=self.ticker_var, width=10)
        self.ticker_entry.pack(side=tk.LEFT, padx=2)
        
        # Поле ввода количества
        ttk.Label(input_frame, text="Количество:").pack(side=tk.LEFT, padx=2)
        self.quantity_entry = ttk.Entry(input_frame, textvariable=self.quantity_var, width=10)
        self.quantity_entry.pack(side=tk.LEFT, padx=2)
        
        # Поле ввода цены покупки
        ttk.Label(input_frame, text="Цена покупки:").pack(side=tk.LEFT, padx=2)
        self.buy_price_entry = ttk.Entry(input_frame, textvariable=self.buy_price_var, width=10)
        self.buy_price_entry.pack(side=tk.LEFT, padx=2)
        
        # Кнопка покупки
        ttk.Button(input_frame, text="Купить", 
                  command=self.portfolio_window.add_stock).pack(side=tk.LEFT, padx=10)
    
    def create_sell_section(self, parent):
        """
        Создание секции продажи акций.
        
        Args:
            parent: родительский контейнер
        """
        sell_frame = ttk.LabelFrame(parent, text="Продажа акций", padding="10")
        sell_frame.pack(fill=tk.X, pady=(0, 10))
        
        sell_input_frame = ttk.Frame(sell_frame)
        sell_input_frame.pack(fill=tk.X, pady=5)
        
        # Комбобокс выбора тикера для продажи
        ttk.Label(sell_input_frame, text="Тикер:").pack(side=tk.LEFT, padx=2)
        self.sell_ticker_combo = ttk.Combobox(sell_input_frame, textvariable=self.sell_ticker_var, 
                                             width=10, state="readonly")
        self.sell_ticker_combo.pack(side=tk.LEFT, padx=2)
        
        # Поле ввода количества для продажи
        ttk.Label(sell_input_frame, text="Количество для продажи:").pack(side=tk.LEFT, padx=2)
        self.sell_quantity_entry = ttk.Entry(sell_input_frame, textvariable=self.sell_quantity_var, width=10)
        self.sell_quantity_entry.pack(side=tk.LEFT, padx=2)
        
        # Поле ввода цены продажи
        ttk.Label(sell_input_frame, text="Цена продажи:").pack(side=tk.LEFT, padx=2)
        self.sell_price_entry = ttk.Entry(sell_input_frame, textvariable=self.sell_price_var, width=10)
        self.sell_price_entry.pack(side=tk.LEFT, padx=2)
        
        # Кнопка продажи
        ttk.Button(sell_input_frame, text="Продать", 
                  command=self.portfolio_window.sell_stock).pack(side=tk.LEFT, padx=10)
        
        # Обновляем комбобокс при создании
        self.update_sell_ticker_combo()
    
    def create_table(self, parent):
        """
        Создание таблицы для отображения портфеля.
        
        Args:
            parent: родительский контейнер
        """
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Создание Treeview с колонками для дивидендов
        columns = ("ticker", "name", "quantity", "buy_price", "commission", 
                  "total_cost", "current_price", "current_value", 
                  "capital_gain", "dividend_income", "total_profit", "profit_percent")
        
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        headers = {
            "ticker": "Тикер",
            "name": "Название",
            "quantity": "Кол-во",
            "buy_price": "Цена покупки",
            "commission": "Комиссия",
            "total_cost": "Общая стоимость",
            "current_price": "Текущая цена",
            "current_value": "Текущая стоимость",
            "capital_gain": "Прибыль по цене",
            "dividend_income": "Дивиденды",
            "total_profit": "Общая прибыль",
            "profit_percent": "Доходность %"
        }
        
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=90, minwidth=80)
        
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
    
    def create_statistics(self, parent):
        """
        Создание блока статистики портфеля.
        
        Args:
            parent: родительский контейнер
        """
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X)
        
        self.stats_label = ttk.Label(stats_frame, 
                                    text="Общая стоимость: 0.00 руб | Прибыль: 0.00 руб (0.00%)",
                                    font=("Arial", 10, "bold"))
        self.stats_label.pack()
    
    def refresh_table(self):
        """
        Обновление данных в таблице с правильным расчетом прибыли.
        """
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполняем данными
        for stock in self.portfolio_manager.portfolio_data:
            # Убедимся, что все расчеты выполнены
            self.portfolio_manager.calculate_stock_values(stock)
            
            # Получаем рассчитанные значения
            capital_gain = stock.get('capital_gain', 0)
            dividend_income = stock.get('dividend_income', 0)
            total_profit = stock.get('total_profit', 0)
            total_profit_percent = stock.get('total_profit_percent', 0)
            
            item = self.tree.insert("", tk.END, values=(
                stock['ticker'],
                stock.get('name', ''),
                stock['quantity'],
                f"{stock['buy_price']:.2f}",
                f"{stock.get('commission', 0):.2f}",
                f"{stock.get('total_cost', 0):.2f}",
                f"{stock.get('current_price', 0):.2f}",
                f"{stock.get('current_value', 0):.2f}",
                f"{capital_gain:+.2f}",
                f"{dividend_income:+.2f}",
                f"{total_profit:+.2f}",
                f"{total_profit_percent:+.2f}%"
            ))
            
            # Устанавливаем теги для цветового оформления
            profit_tags = []
            if capital_gain >= 0:
                profit_tags.append('capital_gain_positive')
            else:
                profit_tags.append('capital_gain_negative')
                
            if total_profit >= 0:
                profit_tags.append('total_profit_positive')
            else:
                profit_tags.append('total_profit_negative')
            
            if profit_tags:
                self.tree.item(item, tags=profit_tags)
    
    def update_statistics(self):
        """
        Обновление статистики портфеля с правильным расчетом.
        """
        stats = self.portfolio_manager.get_portfolio_statistics()
        
        profit_color = "green" if stats['total_profit'] >= 0 else "red"
        
        stats_text = (f"Общая стоимость: {stats['total_current_value']:,.2f} руб | "
                     f"Капитальная прибыль: {stats['total_capital_gain']:+,.2f} руб ({stats['capital_gain_percent']:+.2f}%) | "
                     f"Дивиденды: {stats['total_dividends']:+,.2f} руб ({stats['dividend_yield']:+.2f}%) | "
                     f"Комиссии: {stats['total_commissions']:,.2f} руб ({stats['commission_percent']:.2f}%) | "
                     f"Общая прибыль: {stats['total_profit']:+,.2f} руб ({stats['total_profit_percent']:+.2f}%)")
        
        self.stats_label.config(text=stats_text, foreground=profit_color)
    
    def update_sell_ticker_combo(self):
        """
        Обновление списка тикеров для продажи.
        """
        tickers = [stock['ticker'] for stock in self.portfolio_manager.portfolio_data]
        self.sell_ticker_combo['values'] = tickers
        if tickers:
            self.sell_ticker_combo.set(tickers[0])
    
    def clear_input_fields(self):
        """
        Очистка полей ввода после операций.
        """
        self.ticker_var.set("")
        self.quantity_var.set("")
        self.buy_price_var.set("")
        self.sell_quantity_var.set("")
        self.sell_price_var.set("")
        self.ticker_entry.focus()