# stock_monitor.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from data_handler import DataHandler
from chart_manager import ChartManager
from calculator_window import CalculatorWindow
from commission_manager import CommissionManager
from etf_portfolio_window import ETFPortfolioWindow
class StockMonitor:
    """
    Основной класс приложения для мониторинга акций.
    Содержит графический интерфейс и логику обновления данных.
    """
    
    def __init__(self, root):
        # Инициализация главного окна
        self.root = root
        self.root.title("Монитор акций")
        self.root.geometry("1400x800")
        
        # Инициализация компонентов
        self.current_ticker = "SBER"  # Тикер по умолчанию
        self.data_handler = DataHandler(self.current_ticker)
        self.chart_manager = ChartManager()
        self.calculator_windows = []  # Список открытых окон калькулятора
        self.update_interval = 5  # Интервал обновления в секундах
        self.auto_update = True   # Флаг автообновления
        
        # Создание интерфейса
        self.create_menu()        # Создание верхнего меню
        self.create_widgets()     # Создание основных виджетов
        self.load_daily_data()    # Загрузка исторических данных
        self.update_data()        # Запуск обновления данных
        
    def create_menu(self):
        """Создание верхнего меню для навигации между окнами"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
    
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сменить тикер", command=self.change_ticker)
        file_menu.add_command(label="Портфель акций", command=self.open_portfolio)
        file_menu.add_command(label="Портфель ETF", command=self.open_etf_portfolio)
        file_menu.add_command(label="Калькулятор IBO", command=self.open_calculator)
        file_menu.add_command(label="Калькулятор Шарпа", command=self.open_sharpe_calculator)
        file_menu.add_command(label="Настройки комиссий", command=self.open_commission_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Вид"
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Внутридневной график", 
                             command=lambda: self.show_tab(0))
        view_menu.add_command(label="График за день", 
                             command=lambda: self.show_tab(1))
        
        # Меню "Настройки"
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(label="Интервал обновления", 
                                command=self.change_interval_dialog)
        
        # Меню "Окна" (для управления несколькими окнами)
        self.windows_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Окна", menu=self.windows_menu)
        self.windows_menu.add_command(label="Основное окно", 
                                     command=self.focus_main_window)
        self.windows_menu.add_separator()
        self.windows_menu.add_command(label="Закрыть все калькуляторы", 
                                     command=self.close_all_calculators)
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
   
    
    def open_commission_settings(self):
        """Открытие настроек комиссий"""
        if hasattr(self, 'portfolio_window') and self.portfolio_window:
            self.portfolio_window.commission_manager.show_commission_settings()
        else:
            # Создаем временный менеджер комиссий
            temp_manager = CommissionManager(self.root)
            temp_manager.show_commission_settings()
        
    def change_ticker(self):
        """Смена тикера акции"""
        new_ticker = simpledialog.askstring("Смена тикера", 
                                          "Введите новый тикер акции:",
                                          initialvalue=self.current_ticker)
        if new_ticker and new_ticker.strip():
            new_ticker = new_ticker.strip().upper()
            if new_ticker != self.current_ticker:
                self.current_ticker = new_ticker
                self.data_handler.set_ticker(new_ticker)
                
                # Обновляем заголовок
                self.root.title(f"Монитор акций - {self.current_ticker}")
                
                # Очищаем графики и загружаем новые данные
                self.chart_manager.clear_charts()
                self.load_daily_data()
                self.manual_update()
                
                messagebox.showinfo("Успех", f"Тикер изменен на {self.current_ticker}")
    
    def open_calculator(self):
        """Создание нового окна калькулятора"""
        calculator = CalculatorWindow(self.root, self.data_handler)
        self.calculator_windows.append(calculator)
        self.update_windows_menu()
        
    def update_windows_menu(self):
        """Обновление меню окон"""
        # Очищаем текущее меню окон (кроме первых двух пунктов)
        self.windows_menu.delete(2, tk.END)
        
        # Добавляем пункты для каждого открытого калькулятора
        for i, calculator in enumerate(self.calculator_windows):
            self.windows_menu.add_command(
                label=f"Калькулятор {i+1}", 
                command=calculator.focus
            )
        
    def focus_main_window(self):
        """Активация главного окна"""
        self.root.focus_force()
        
    def close_all_calculators(self):
        """Закрытие всех окон калькулятора"""
        for calculator in self.calculator_windows[:]:
            calculator.close()
        self.calculator_windows.clear()
        self.update_windows_menu()
            
    def show_about(self):
        """Показать информацию о программе"""
        messagebox.showinfo("О программе", 
                           "Монитор акций\n\n"
                           "Версия 2.0\n"
                           "Приложение для отслеживания акций Московской биржи\n"
                           "с графиками в реальном времени и калькулятором стоимости.")
    
    def show_tab(self, tab_index):
        """Показать указанную вкладку"""
        self.notebook.select(tab_index)
        
    def change_interval_dialog(self):
        """Диалог изменения интервала обновления"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Настройка интервала")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Выберите интервал обновления (секунды):").pack(pady=10)
        
        interval_var = tk.StringVar(value=str(self.update_interval))
        interval_combo = ttk.Combobox(dialog, textvariable=interval_var,
                                     values=["1", "5", "10", "15", "30", "60"], width=10)
        interval_combo.pack(pady=5)
        
        def apply_interval():
            try:
                new_interval = int(interval_var.get())
                if 1 <= new_interval <= 300:  # Ограничение от 1 до 300 секунд
                    self.update_interval = new_interval
                    self.auto_update_status.config(
                        text=f"Автообновление: ВКЛ (каждые {self.update_interval} сек)"
                    )
                    # Перезапускаем автообновление если оно активно
                    if self.auto_update:
                        self.toggle_auto_update()
                        self.toggle_auto_update()
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Интервал должен быть от 1 до 300 секунд")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")
        
        ttk.Button(dialog, text="Применить", command=apply_interval).pack(pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)
    
    def create_widgets(self):
        """Создание основных элементов интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок и выбор тикера
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=tk.W+tk.E)
        
        title_label = ttk.Label(header_frame, text=f"График акций", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Поле для быстрой смены тикера
        ticker_frame = ttk.Frame(header_frame)
        ticker_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(ticker_frame, text="Тикер:").pack(side=tk.LEFT)
        self.ticker_var = tk.StringVar(value=self.current_ticker)
        ticker_entry = ttk.Entry(ticker_frame, textvariable=self.ticker_var, width=8)
        ticker_entry.pack(side=tk.LEFT, padx=5)
        ticker_entry.bind('<Return>', self.on_ticker_change)
        
        ttk.Button(ticker_frame, text="Обновить", 
                  command=self.on_ticker_change).pack(side=tk.LEFT)
        
        # Время сервера
        self.time_label = ttk.Label(main_frame, text="", font=("Arial", 10))
        self.time_label.grid(row=1, column=0, columnspan=3)
        
        # Статус торгов
        self.status_label = ttk.Label(main_frame, text="Проверка статуса торгов...", 
                                     font=("Arial", 12))
        self.status_label.grid(row=2, column=0, columnspan=3, pady=(0, 5))
        
        # Информация о последней цене
        self.price_label = ttk.Label(main_frame, text="Цена: -", font=("Arial", 14, "bold"))
        self.price_label.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # Статистика
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.change_label = ttk.Label(stats_frame, text="Изменение: -", font=("Arial", 10))
        self.change_label.pack(side=tk.LEFT, padx=10)
        
        self.change_percent_label = ttk.Label(stats_frame, text="Изменение %: -", font=("Arial", 10))
        self.change_percent_label.pack(side=tk.LEFT, padx=10)
        
        self.volume_label = ttk.Label(stats_frame, text="Объем: -", font=("Arial", 10))
        self.volume_label.pack(side=tk.LEFT, padx=10)
        
        self.high_label = ttk.Label(stats_frame, text="Макс: -", font=("Arial", 10))
        self.high_label.pack(side=tk.LEFT, padx=10)
        
        self.low_label = ttk.Label(stats_frame, text="Мин: -", font=("Arial", 10))
        self.low_label.pack(side=tk.LEFT, padx=10)
        
        # Создание вкладок для графиков
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=5, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Вкладка внутридневного графика
        intraday_frame = ttk.Frame(self.notebook)
        self.notebook.add(intraday_frame, text="Внутридневной график")
        self.chart_manager.create_intraday_chart(intraday_frame)
        
        # Вкладка графика за день
        daily_frame = ttk.Frame(self.notebook)
        self.notebook.add(daily_frame, text="График за день")
        self.chart_manager.create_daily_chart(daily_frame)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Обновить", 
                  command=self.manual_update).pack(side=tk.LEFT, padx=5)
        
        self.auto_update_btn = ttk.Button(button_frame, text="Автообновление ВКЛ", 
                                         command=self.toggle_auto_update)
        self.auto_update_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Экспорт данных", 
                  command=self.export_data).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Очистить график", 
                  command=self.clear_chart).pack(side=tk.LEFT, padx=5)
                  
        #ttk.Button(button_frame, text="Мой портфель", 
        #          command=self.open_portfolio).pack(side=tk.LEFT, padx=5)
        # Кнопка открытия калькулятора
        #ttk.Button(button_frame, text="Калькулятор стоимости", 
        #          command=self.open_calculator).pack(side=tk.LEFT, padx=5)
                  
        #ttk.Button(button_frame, text="Портфель ETF", 
        #          command=self.open_etf_portfolio).pack(side=tk.LEFT, padx=5)
        
        #ttk.Button(button_frame, text="Коэффициент Шарпа", command=self.open_sharpe_calculator).pack(side=tk.LEFT, padx=5)
        # Добавляем кнопки управления масштабом для каждой вкладки
        self.chart_manager.setup_zoom_buttons(button_frame, 'intraday')
        self.chart_manager.setup_zoom_buttons(button_frame, 'daily')
        
        # Настройка интервала обновления
        interval_frame = ttk.Frame(button_frame)
        interval_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(interval_frame, text="Интервал:").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="5")
        interval_combo = ttk.Combobox(interval_frame, textvariable=self.interval_var,
                                     values=["5", "10", "15", "30", "60"], width=5)
        interval_combo.pack(side=tk.LEFT, padx=5)
        interval_combo.bind('<<ComboboxSelected>>', self.change_interval)
        
        # Статус автообновления
        self.auto_update_status = ttk.Label(main_frame, text=f"Автообновление: ВКЛ (каждые {self.update_interval} сек)")
        self.auto_update_status.grid(row=7, column=0, columnspan=3)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
    def open_etf_portfolio(self):
        """Открытие окна портфеля ETF"""
        try:
            # Проверяем, существует ли уже окно портфеля ETF
            if hasattr(self, 'etf_portfolio_window') and self.etf_portfolio_window.window.winfo_exists():
                self.etf_portfolio_window.window.lift()  # Поднимаем окно на передний план
                self.etf_portfolio_window.window.focus_force()  # Даем фокус
            else:
                # Создаем новое окно портфеля ETF
                self.etf_portfolio_window = ETFPortfolioWindow(self.root, self.data_handler)
        except Exception as e:
            print(f"Ошибка открытия портфеля ETF: {e}")
            # Создаем новое окно в случае ошибки
            self.etf_portfolio_window = ETFPortfolioWindow(self.root, self.data_handler)
        
    def on_ticker_change(self, event=None):
        """Обработчик смены тикера"""
        new_ticker = self.ticker_var.get().strip().upper()
        if new_ticker and new_ticker != self.current_ticker:
            self.current_ticker = new_ticker
            self.data_handler.set_ticker(new_ticker)
            self.root.title(f"Монитор акций - {self.current_ticker}")
            
            # Очищаем графики и загружаем новые данные
            self.chart_manager.clear_charts()
            self.load_daily_data()
            self.manual_update()
    
    def load_daily_data(self):
        """Загрузка сохраненных данных и создание предыдущих точек графика"""
        try:
            filename = f"{self.current_ticker.lower()}_daily_data.json"
            with open(filename, 'r') as f:
                saved_data = json.load(f)
                saved_date = datetime.fromisoformat(saved_data['date'])
                today = self.data_handler.get_moscow_time().date()
                
                if saved_date.date() == today:
                    # Загружаем сохраненные данные за сегодня
                    self.chart_manager.daily_data = [(datetime.fromisoformat(d), p) for d, p in saved_data['prices']]
                    self.chart_manager.intraday_dates = [d for d, p in self.chart_manager.daily_data[-50:]]
                    self.chart_manager.intraday_prices = [p for d, p in self.chart_manager.daily_data[-50:]]
                    print(f"Загружены сохраненные данные за сегодня для {self.current_ticker}")
                    
                    # Обновляем графики с загруженными данными
                    self.chart_manager.update_intraday_chart()
                    self.chart_manager.update_daily_chart()
                    return
        except FileNotFoundError:
            print(f"Файл с сохраненными данными для {self.current_ticker} не найден, создаем новые данные")
        except Exception as e:
            print(f"Ошибка загрузки данных для {self.current_ticker}: {e}")
        
        # Если сохраненных данных нет или они за другой день, создаем начальные данные
        self.create_initial_chart_data()
    
    def create_initial_chart_data(self):
        """Создание начальных данных для графика с предыдущими ценами"""
        current_time = self.data_handler.get_moscow_time()
        
        # Получаем текущую цену для создания исторических данных
        data = self.data_handler.get_stock_data()
        current_price = data['price']
        
        # Создаем данные за последние 2 часа с интервалом в 5 минут
        start_time = current_time - timedelta(hours=2)
        
        # Если есть исторические данные, используем их для создания реалистичного графика
        if 'open' in data and data['open'] is not None:
            open_price = data['open']
            low_price = data.get('low', open_price * 0.995)
            high_price = data.get('high', open_price * 1.005)
        else:
            # Используем текущую цену как базовую
            open_price = current_price * 0.99  # Предполагаем, что открытие было немного ниже
            low_price = current_price * 0.985
            high_price = current_price * 1.01
        
        # Создаем реалистичные колебания цен
        import random
        self.chart_manager.daily_data = []
        
        # Начальная цена (открытие)
        price = open_price
        
        # Генерируем точки для графика за последние 2 часа
        for i in range(24):  # 24 точки за 2 часа (каждые 5 минут)
            point_time = start_time + timedelta(minutes=i * 5)
            
            # Случайное изменение цены в пределах дневного диапазона
            price_change = random.uniform(-0.1, 0.1)  # Небольшие колебания
            price = price * (1 + price_change)
            
            # Ограничиваем цену дневным диапазоном
            price = max(low_price, min(high_price, price))
            
            self.chart_manager.daily_data.append((point_time, price))
        
        # Добавляем текущую точку
        self.chart_manager.daily_data.append((current_time, current_price))
        
        # Обновляем внутридневные данные (последние 50 точек)
        self.chart_manager.intraday_dates = [d for d, p in self.chart_manager.daily_data[-50:]]
        self.chart_manager.intraday_prices = [p for d, p in self.chart_manager.daily_data[-50:]]
        
        # Сохраняем сгенерированные данные
        self.save_daily_data()
        
        # Обновляем графики
        self.chart_manager.update_intraday_chart()
        self.chart_manager.update_daily_chart()
        
        print(f"Созданы начальные данные графика с предыдущими ценами для {self.current_ticker}")
    
    def save_daily_data(self):
        """Сохранение дневных данных в JSON файл"""
        try:
            filename = f"{self.current_ticker.lower()}_daily_data.json"
            data_to_save = {
                'date': self.data_handler.get_moscow_time().date().isoformat(),
                'ticker': self.current_ticker,
                'prices': [(d.isoformat(), p) for d, p in self.chart_manager.daily_data]
            }
            with open(filename, 'w') as f:
                json.dump(data_to_save, f)
        except Exception as e:
            print(f"Ошибка сохранения данных для {self.current_ticker}: {e}")
    
    def get_stock_data(self):
        """Получение данных об акциях"""
        return self.data_handler.get_stock_data()
    
    def update_data(self):
        """Запуск потока для автоматического обновления данных"""
        def update_thread():
            while self.auto_update:
                try:
                    data = self.get_stock_data()
                    if data['success']:
                        self.root.after(0, self.update_interface, data)
                    time.sleep(self.update_interval)
                except Exception as e:
                    print(f"Ошибка в потоке обновления: {e}")
                    time.sleep(self.update_interval)
        
        self.update_thread = threading.Thread(target=update_thread, daemon=True)
        self.update_thread.start()
    
    def update_interface(self, data):
        """Обновление интерфейса с новыми данными"""
        current_time = data['time']
        price = data['price']
        
        # Обновляем время
        time_text = f"Московское время: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.time_label.config(text=time_text)
        
        # Проверяем статус торгов
        is_market_open = self.data_handler.check_market_hours(current_time)
        
        # Обновляем статус
        status_text = "✅ Торги открыты" if is_market_open else "❌ Торги закрыты"
        status_color = "green" if is_market_open else "red"
        self.status_label.config(text=status_text, foreground=status_color)
        
        # Обновляем цену и статистику
        source_info = ""
        if data.get('is_historical'):
            source_info = " (исторические данные)"
        elif data.get('is_fallback'):
            source_info = " (фиксированные данные)"
        
        price_text = f"Цена {self.current_ticker}: {price:.2f} руб{source_info}"
        self.price_label.config(text=price_text)
        
        # Обновляем изменение цены
        change_abs = data.get('change_absolute', 0)
        change_percent = data.get('change_percent', 0)
        
        change_color = "green" if change_abs >= 0 else "red"
        change_sign = "+" if change_abs >= 0 else ""
        
        change_text = f"Изменение: {change_sign}{change_abs:.2f} руб"
        change_percent_text = f"Изменение %: {change_sign}{change_percent:.2f}%"
        
        self.change_label.config(text=change_text, foreground=change_color)
        self.change_percent_label.config(text=change_percent_text, foreground=change_color)
        
        # Остальная статистика
        volume_text = f"Объем: {data.get('volume', 0):,.0f} руб".replace(',', ' ')
        self.volume_label.config(text=volume_text)
        
        self.high_label.config(text=f"Макс: {data.get('high', 0):.2f}")
        self.low_label.config(text=f"Мин: {data.get('low', 0):.2f}")
        
        # Добавляем данные только если торги открыты ИЛИ это первая точка
        if is_market_open or len(self.chart_manager.daily_data) == 0:
            current_time = self.data_handler.get_moscow_time()
            
            # Для внутридневного графика
            self.chart_manager.intraday_dates.append(current_time)
            self.chart_manager.intraday_prices.append(price)
            
            # Ограничиваем внутридневные данные
            if len(self.chart_manager.intraday_dates) > 100:
                self.chart_manager.intraday_dates = self.chart_manager.intraday_dates[-100:]
                self.chart_manager.intraday_prices = self.chart_manager.intraday_prices[-100:]
            
            # Для графика за весь день
            self.chart_manager.daily_data.append((current_time, price))
            
            # Сохраняем данные
            self.save_daily_data()
            
            # Обновляем графики
            self.chart_manager.update_intraday_chart()
            self.chart_manager.update_daily_chart()
    
    def manual_update(self):
        """Ручное обновление данных"""
        try:
            data = self.get_stock_data()
            if data['success']:
                self.update_interface(data)
                messagebox.showinfo("Обновление", f"Данные для {self.current_ticker} успешно обновлены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")
    
    def clear_chart(self):
        """Очистка графиков"""
        self.chart_manager.clear_charts()
        messagebox.showinfo("Очистка", "Графики очищены!")
    
    def toggle_auto_update(self):
        """Включение/выключение автообновления"""
        self.auto_update = not self.auto_update
        
        if self.auto_update:
            self.auto_update_btn.config(text="Автообновление ВКЛ")
            self.auto_update_status.config(text=f"Автообновление: ВКЛ (каждые {self.update_interval} сек)")
            self.update_data()
        else:
            self.auto_update_btn.config(text="Автообновление ВЫКЛ")
            self.auto_update_status.config(text="Автообновление: ВЫКЛ")
    
    def change_interval(self, event=None):
        """Изменение интервала обновления"""
        try:
            new_interval = int(self.interval_var.get())
            if new_interval != self.update_interval:
                self.update_interval = new_interval
                self.auto_update_status.config(text=f"Автообновление: ВКЛ (каждые {self.update_interval} сек)")
                
                if self.auto_update:
                    self.toggle_auto_update()
                    self.toggle_auto_update()
        except ValueError:
            pass
    
    def export_data(self):
        """Экспорт данных в CSV"""
        try:
            if self.chart_manager.daily_data:
                df = pd.DataFrame({
                    'DateTime': [d for d, p in self.chart_manager.daily_data],
                    'Price': [p for d, p in self.chart_manager.daily_data]
                })
                
                filename = f"{self.current_ticker.lower()}_daily_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                messagebox.showinfo("Экспорт", f"Данные экспортированы в файл: {filename}")
            else:
                messagebox.showwarning("Экспорт", "Нет данных для экспорта")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")
    
    def open_portfolio(self):
        """Открытие окна портфеля акций"""
        from portfolio_window import PortfolioWindow
        PortfolioWindow(self.root, self.data_handler)

    def open_sharpe_calculator(self):
        """Создание калькулятора коэффициента Шарпа"""
        from sharpe_calculator import SharpeCalculator
        SharpeCalculator(self.root, self.data_handler)
def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = StockMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()