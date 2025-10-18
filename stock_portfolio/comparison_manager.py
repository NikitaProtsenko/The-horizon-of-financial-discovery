# Менеджер сравнения - сравнение портфеля с индексом Мосбиржи
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox, ttk
import tkinter as tk
import random

class ComparisonManager:
    """
    Управление сравнением портфеля с индексом Мосбиржи.
    """
    
    def __init__(self, portfolio_manager):
        """
        Инициализация менеджера сравнения.
        
        Args:
            portfolio_manager: ссылка на менеджер портфеля
            portfolio_window: ссылка на главное окно портфеля
        """
        self.portfolio_manager = portfolio_manager

    def show_index_comparison(self, parent_window):
        """Показать сравнение с индексом с получением цен открытия акций"""
        if not self.portfolio_manager.portfolio_data:
            messagebox.showwarning("Внимание", "Портфель пуст")
            return
        
        # Создаем окно прогресса
        progress_window = tk.Toplevel(parent_window)
        progress_window.title("Получение данных...")
        progress_window.geometry("300x100")
        progress_window.transient(parent_window)
        
        ttk.Label(progress_window, text="Получение цен открытия акций...").pack(pady=10)
        progress = ttk.Progressbar(progress_window, mode='indeterminate')
        progress.pack(pady=10, padx=20, fill=tk.X)
        progress.start()
        
        def calculate_comparison():
            # Получаем данные IMOEX
            imoex_data = self.get_imoex_detailed_data()
            
            # Рассчитываем стоимость портфеля на открытии и сейчас
            portfolio_open_value = 0
            portfolio_current_value = 0
            detailed_stocks = []
            
            for stock in self.portfolio_manager.portfolio_data:
                quantity = stock['quantity']
                
                # Получаем цену открытия для каждой акции
                open_price = self.get_stock_open_price(stock['ticker'])
                current_price = stock.get('current_price', stock['buy_price'])
                
                stock_open_value = quantity * open_price
                stock_current_value = quantity * current_price
                stock_return = ((current_price - open_price) / open_price * 100) if open_price > 0 else 0
                
                portfolio_open_value += stock_open_value
                portfolio_current_value += stock_current_value
                
                detailed_stocks.append({
                    'ticker': stock['ticker'],
                    'open_price': open_price,
                    'current_price': current_price,
                    'return': stock_return
                })
            
            # Расчет доходности портфеля за сегодня
            if portfolio_open_value > 0:
                portfolio_return = ((portfolio_current_value - portfolio_open_value) / portfolio_open_value) * 100
            else:
                portfolio_return = 0
            
            imoex_return = imoex_data['change_percent']
            
            # Закрываем прогресс и показываем результаты
            parent_window.after(0, lambda: show_results(
                portfolio_return, imoex_return, 
                portfolio_open_value, portfolio_current_value,
                imoex_data, detailed_stocks
            ))
        
        def show_results(portfolio_return, imoex_return, portfolio_open_value, 
                        portfolio_current_value, imoex_data, detailed_stocks):
            progress.stop()
            progress_window.destroy()
            
            # Создаем окно результатов
            comparison_window = tk.Toplevel(parent_window)
            comparison_window.title("Сравнение с IMOEX - доходность за сегодня")
            comparison_window.geometry("900x900")
            
            main_frame = ttk.Frame(comparison_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Сравнение с индексом Мосбиржи", 
                     font=("Arial", 14, "bold")).pack(pady=(0, 15))
            
            ttk.Label(main_frame, text="Доходность за текущий торговый день", 
                     font=("Arial", 11, "bold"), foreground="blue").pack(pady=(0, 10))
            
            # Детальная статистика
            stats_frame = ttk.LabelFrame(main_frame, text="Общая статистика", padding="10")
            stats_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Создаем сетку для статистики
            stats_grid = ttk.Frame(stats_frame)
            stats_grid.pack(fill=tk.X)
            
            # Заголовки
            ttk.Label(stats_grid, text="", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
            ttk.Label(stats_grid, text="На открытии", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5, pady=2)
            ttk.Label(stats_grid, text="Текущая", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5, pady=2)
            ttk.Label(stats_grid, text="Изменение", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5, pady=2)
            
            # Данные портфеля
            ttk.Label(stats_grid, text="Портфель", font=("Arial", 9, "bold")).grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
            ttk.Label(stats_grid, text=f"{portfolio_open_value:,.2f} руб").grid(row=1, column=1, padx=5, pady=2)
            ttk.Label(stats_grid, text=f"{portfolio_current_value:,.2f} руб").grid(row=1, column=2, padx=5, pady=2)
            
            portfolio_color = "green" if portfolio_return >= 0 else "red"
            portfolio_change = portfolio_current_value - portfolio_open_value
            ttk.Label(stats_grid, text=f"{portfolio_change:+,.2f} руб ({portfolio_return:+.2f}%)", 
                     foreground=portfolio_color, font=("Arial", 9, "bold")).grid(row=1, column=3, padx=5, pady=2)
            
            # Данные индекса
            ttk.Label(stats_grid, text="Индекс IMOEX", font=("Arial", 9, "bold")).grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
            ttk.Label(stats_grid, text=f"{imoex_data['open']:.2f}").grid(row=2, column=1, padx=5, pady=2)
            ttk.Label(stats_grid, text=f"{imoex_data['current']:.2f}").grid(row=2, column=2, padx=5, pady=2)
            
            imoex_color = "green" if imoex_data['change_percent'] >= 0 else "red"
            imoex_change = imoex_data['current'] - imoex_data['open']
            ttk.Label(stats_grid, text=f"{imoex_change:+.2f} ({imoex_data['change_percent']:+.2f}%)", 
                     foreground=imoex_color, font=("Arial", 9, "bold")).grid(row=2, column=3, padx=5, pady=2)
            
            # Разница
            difference = portfolio_return - imoex_data['change_percent']
            difference_color = "green" if difference >= 0 else "red"
            ttk.Label(stats_grid, text="Разница", font=("Arial", 9, "bold")).grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
            ttk.Label(stats_grid, text="", foreground=difference_color, font=("Arial", 9, "bold")).grid(row=3, column=1, padx=5, pady=2)
            ttk.Label(stats_grid, text="", foreground=difference_color, font=("Arial", 9, "bold")).grid(row=3, column=2, padx=5, pady=2)
            ttk.Label(stats_grid, text=f"{difference:+.2f}%", 
                     foreground=difference_color, font=("Arial", 9, "bold")).grid(row=3, column=3, padx=5, pady=2)
            
            # Детали по акциям
            if len(detailed_stocks) > 0:
                details_frame = ttk.LabelFrame(main_frame, text="Детали по акциям", padding="10")
                details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
                
                # Таблица
                columns = ("ticker", "open_price", "current_price", "return")
                tree = ttk.Treeview(details_frame, columns=columns, show="headings", height=6)
                
                headers = {
                    "ticker": "Тикер",
                    "open_price": "Цена открытия",
                    "current_price": "Текущая цена", 
                    "return": "Изменение %"
                }
                
                for col in columns:
                    tree.heading(col, text=headers[col])
                    if col == "ticker":
                        tree.column(col, width=80, minwidth=70)
                    else:
                        tree.column(col, width=100, minwidth=90)
                
                # Заполняем данными
                for stock in detailed_stocks:
                    return_color = "green" if stock['return'] >= 0 else "red"
                    tree.insert("", tk.END, values=(
                        stock['ticker'],
                        f"{stock['open_price']:.2f}",
                        f"{stock['current_price']:.2f}",
                        f"{stock['return']:+.2f}%"
                    ))
                
                # Прокрутка
                v_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscrollcommand=v_scroll.set)
                
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            # График сравнения
            chart_frame = ttk.LabelFrame(main_frame, text="Визуальное сравнение", padding="10")
            chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            fig, ax = plt.subplots(figsize=(8, 4), dpi=80)
            
            categories = ['Ваш портфель', 'Индекс IMOEX']
            returns = [portfolio_return, imoex_return]
            
            colors = ['#2E8B57' if portfolio_return >= 0 else '#DC143C', 
                      '#1E90FF' if imoex_return >= 0 else '#FF8C00']
            
            bars = ax.bar(categories, returns, color=colors, alpha=0.7)
            ax.set_ylabel('Доходность (%)')
            ax.set_title('Сравнение доходности за сегодня')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Подписи значений
            for bar, value in zip(bars, returns):
                height = bar.get_height()
                va = 'bottom' if height >= 0 else 'top'
                y_offset = 0.5 if height >= 0 else -0.8
                ax.text(bar.get_x() + bar.get_width()/2, height + y_offset,
                       f'{value:+.2f}%', ha='center', va=va, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
            
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Кнопка закрытия
            ttk.Button(main_frame, text="Закрыть", 
                      command=comparison_window.destroy).pack(pady=10)
        
        # Запускаем в отдельном потоке
        import threading
        thread = threading.Thread(target=calculate_comparison)
        thread.daemon = True
        thread.start() 
   

    def get_stock_open_price(self, ticker):
        """Получить цену открытия для одной акции"""
        try:
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                market_data = data['marketdata']['data']
                
                if market_data and market_data[0]:
                    open_price = market_data[0][9]  # OPEN price (индекс 9)
                    if open_price is not None:
                        return float(open_price)
                    
                    # Если цена открытия не доступна, используем цену закрытия предыдущего дня
                    prev_close = market_data[0][11]  # PREVADMITTEDQUOTE
                    if prev_close is not None:
                        return float(prev_close)
        except:
            pass
        
        # Если не получилось, используем текущую цену из портфеля
        for stock in self.portfolio_manager.portfolio_data:
            if stock['ticker'] == ticker:
                return stock.get('current_price', stock['buy_price'])
        
        return 0

    def get_imoex_detailed_data(self):
        """Получение детальных данных IMOEX (открытие и текущая цена)"""
        try:
            url = "https://iss.moex.com/iss/engines/stock/markets/index/boards/SNDX/securities/IMOEX.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                market_data = data['marketdata']['data']
                
                if market_data and market_data[0]:
                    open_price = market_data[0][2]  # OPEN
                    current_price = market_data[0][4] or market_data[0][3]  # LAST или LCURRENTPRICE
                    
                    if open_price and current_price:
                        change_percent = ((current_price - open_price) / open_price) * 100
                        return {
                            'open': float(open_price),
                            'current': float(current_price),
                            'change_percent': change_percent
                        }
        except:
            pass
        
        # Запасные данные
        return {'open': 3200, 'current': 3220, 'change_percent': 0.62}