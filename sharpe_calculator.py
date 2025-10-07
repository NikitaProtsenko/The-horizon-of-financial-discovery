# sharpe_calculator.py
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import json

class SharpeCalculator:
    """
    Калькулятор коэффициента Шарпа для анализа эффективности портфеля
    """
    
    def __init__(self, parent, data_handler=None):
        self.parent = parent
        self.data_handler = data_handler
        self.window = tk.Toplevel(parent)
        self.window.title("Калькулятор коэффициента Шарпа")
        self.window.geometry("1000x700")
        self.window.minsize(800, 600)
        
        # Данные для расчета
        self.portfolio_data = []
        self.historical_data = {}
        self.sharpe_ratio = 0
        self.risk_free_rate = 7.5  # Безрисковая ставка по умолчанию (% годовых)
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных портфеля если есть
        self.load_portfolio_data()
        
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    def create_widgets(self):
        """Создание элементов интерфейса калькулятора Шарпа"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Калькулятор коэффициента Шарпа", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Параметры расчета", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Безрисковая ставка
        rate_frame = ttk.Frame(control_frame)
        rate_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rate_frame, text="Безрисковая ставка (% годовых):").pack(side=tk.LEFT)
        self.risk_free_var = tk.StringVar(value=str(self.risk_free_rate))
        rate_entry = ttk.Entry(rate_frame, textvariable=self.risk_free_var, width=10)
        rate_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(rate_frame, text="%").pack(side=tk.LEFT)
        
        # Период расчета
        period_frame = ttk.Frame(control_frame)
        period_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(period_frame, text="Период анализа:").pack(side=tk.LEFT)
        self.period_var = tk.StringVar(value="365")
        period_combo = ttk.Combobox(period_frame, textvariable=self.period_var,
                                   values=["30", "90", "180", "365", "730"], width=10)
        period_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(period_frame, text="дней").pack(side=tk.LEFT)
        
        # Кнопки управления
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Загрузить данные портфеля", 
                  command=self.load_portfolio_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Рассчитать коэффициент Шарпа", 
                  command=self.calculate_sharpe).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить исторические данные", 
                  command=self.update_historical_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт отчета", 
                  command=self.export_report).pack(side=tk.RIGHT, padx=5)
        
        # Результаты расчета
        results_frame = ttk.LabelFrame(main_frame, text="Результаты расчета", padding="10")
        results_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Показатели
        metrics_frame = ttk.Frame(results_frame)
        metrics_frame.pack(fill=tk.X, pady=5)
        
        self.sharpe_label = ttk.Label(metrics_frame, 
                                     text="Коэффициент Шарпа: -", 
                                     font=("Arial", 12, "bold"))
        self.sharpe_label.pack(side=tk.LEFT, padx=10)
        
        self.return_label = ttk.Label(metrics_frame, 
                                     text="Средняя доходность: -", 
                                     font=("Arial", 10))
        self.return_label.pack(side=tk.LEFT, padx=10)
        
        self.volatility_label = ttk.Label(metrics_frame, 
                                         text="Волатильность: -", 
                                         font=("Arial", 10))
        self.volatility_label.pack(side=tk.LEFT, padx=10)
        
        # График доходности
        chart_frame = ttk.LabelFrame(main_frame, text="График доходности портфеля", padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.create_returns_chart(chart_frame)
        
        # Детальная информация
        details_frame = ttk.LabelFrame(main_frame, text="Детальная информация по активам", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_details_table(details_frame)
    
    def create_returns_chart(self, parent):
        """Создание графика доходности"""
        self.returns_fig, self.returns_ax = plt.subplots(figsize=(10, 4), dpi=100)
        self.returns_ax.set_title('Доходность портфеля', fontsize=14, fontweight='bold', pad=20)
        self.returns_ax.set_xlabel('Дата', fontsize=10)
        self.returns_ax.set_ylabel('Доходность (%)', fontsize=10)
        self.returns_ax.grid(True, alpha=0.3)
        
        self.returns_canvas = FigureCanvasTkAgg(self.returns_fig, parent)
        self.returns_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_details_table(self, parent):
        """Создание таблицы с детальной информацией"""
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ticker", "weight", "return", "volatility", "sharpe", "correlation")
        
        self.details_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=8)
        
        headers = {
            "ticker": "Тикер",
            "weight": "Вес в портфеле (%)",
            "return": "Доходность (%)",
            "volatility": "Волатильность (%)",
            "sharpe": "Коэф. Шарпа",
            "correlation": "Корреляция"
        }
        
        for col in columns:
            self.details_tree.heading(col, text=headers[col])
            self.details_tree.column(col, width=120, minwidth=100)
        
        v_scroll = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.details_tree.yview)
        h_scroll = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.details_tree.xview)
        self.details_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.details_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
    
    def load_portfolio_data(self):
        """Загрузка данных портфеля из файла"""
        try:
            if hasattr(self.parent, 'portfolio_data'):
                self.portfolio_data = self.parent.portfolio_data
            else:
                # Пытаемся загрузить из файла
                import os
                if os.path.exists('portfolio_data.json'):
                    with open('portfolio_data.json', 'r', encoding='utf-8') as f:
                        self.portfolio_data = json.load(f)
            
            messagebox.showinfo("Успех", f"Загружено {len(self.portfolio_data)} активов из портфеля")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные портфеля: {e}")
            self.portfolio_data = []
    
    def get_historical_prices(self, ticker, days=365):
        """Получение исторических цен для тикера"""
        try:
            # Используем MOEX API для получения исторических данных
            url = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            url += f"?from={from_date}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                history_data = data['history']['data']
                
                prices = []
                dates = []
                
                for point in reversed(history_data):  # В хронологическом порядке
                    try:
                        date_str = point[1]  # TRADEDATE
                        close_price = point[11]  # CLOSE
                        
                        if date_str and close_price:
                            trade_date = datetime.strptime(date_str, '%Y-%m-%d')
                            prices.append(float(close_price))
                            dates.append(trade_date)
                    except:
                        continue
                
                return dates, prices
                
        except Exception as e:
            print(f"Ошибка получения исторических данных для {ticker}: {e}")
        
        return [], []
    
    def update_historical_data(self):
        """Обновление исторических данных для всех активов в портфеле"""
        if not self.portfolio_data:
            messagebox.showwarning("Внимание", "Портфель пуст")
            return
        
        progress_window = tk.Toplevel(self.window)
        progress_window.title("Обновление данных")
        progress_window.geometry("300x120")
        progress_window.transient(self.window)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Обновление исторических данных...").pack(pady=10)
        progress = ttk.Progressbar(progress_window, mode='determinate', maximum=len(self.portfolio_data))
        progress.pack(pady=10, padx=20, fill=tk.X)
        
        status_label = ttk.Label(progress_window, text="")
        status_label.pack()
        
        def update_data():
            self.historical_data = {}
            updated_count = 0
            
            for i, stock in enumerate(self.portfolio_data):
                ticker = stock['ticker']
                status_label.config(text=f"Обработка {ticker}...")
                progress['value'] = i + 1
                progress_window.update()
                
                days = int(self.period_var.get())
                dates, prices = self.get_historical_prices(ticker, days)
                
                if dates and prices:
                    self.historical_data[ticker] = {
                        'dates': dates,
                        'prices': prices,
                        'returns': self.calculate_returns(prices)
                    }
                    updated_count += 1
            
            self.window.after(0, lambda: finish_update(updated_count))
        
        def finish_update(updated_count):
            progress_window.destroy()
            messagebox.showinfo("Обновление", 
                              f"Данные обновлены для {updated_count} из {len(self.portfolio_data)} активов")
        
        import threading
        thread = threading.Thread(target=update_data)
        thread.daemon = True
        thread.start()
    
    def calculate_returns(self, prices):
        """Расчет дневной доходности на основе цен"""
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            daily_return = (prices[i] - prices[i-1]) / prices[i-1] * 100
            returns.append(daily_return)
        
        return returns
    
    def calculate_sharpe(self):
        """Расчет коэффициента Шарпа для портфеля"""
        if not self.portfolio_data or not self.historical_data:
            messagebox.showwarning("Внимание", 
                                 "Нет данных для расчета. Загрузите портфель и обновите исторические данные.")
            return
        
        try:
            risk_free_rate = float(self.risk_free_var.get())
            period_days = int(self.period_var.get())
            
            # Расчет доходности портфеля
            portfolio_returns = self.calculate_portfolio_returns()
            
            if not portfolio_returns:
                messagebox.showerror("Ошибка", "Не удалось рассчитать доходность портфеля")
                return
            
            # Расчет коэффициента Шарпа
            avg_return = np.mean(portfolio_returns)
            std_return = np.std(portfolio_returns)
            
            # Годовая доходность и волатильность
            annual_return = avg_return * 252  # 252 торговых дня в году
            annual_volatility = std_return * np.sqrt(252)
            
            # Коэффициент Шарпа (годовой)
            if annual_volatility != 0:
                self.sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
            else:
                self.sharpe_ratio = 0
            
            # Обновление интерфейса
            self.update_results_display(annual_return, annual_volatility)
            self.update_returns_chart(portfolio_returns)
            self.update_details_table(portfolio_returns)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте корректность введенных параметров")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчета: {e}")
    
    def calculate_portfolio_returns(self):
        """Расчет доходности портфеля"""
        # Находим общие даты для всех активов
        common_dates = None
        for ticker, data in self.historical_data.items():
            if common_dates is None:
                common_dates = set(data['dates'])
            else:
                common_dates = common_dates.intersection(set(data['dates']))
        
        if not common_dates:
            return []
        
        common_dates = sorted(common_dates)
        
        # Расчет весов портфеля
        total_value = sum(stock.get('current_value', 0) for stock in self.portfolio_data)
        weights = {}
        for stock in self.portfolio_data:
            ticker = stock['ticker']
            if total_value > 0:
                weights[ticker] = stock.get('current_value', 0) / total_value
            else:
                weights[ticker] = 0
        
        # Расчет дневной доходности портфеля
        portfolio_returns = []
        
        for i in range(1, len(common_dates)):
            daily_return = 0
            for ticker, data in self.historical_data.items():
                # Находим индекс даты в данных актива
                try:
                    date_idx = data['dates'].index(common_dates[i])
                    prev_date_idx = data['dates'].index(common_dates[i-1])
                    
                    if (date_idx < len(data['returns']) and 
                        prev_date_idx < len(data['returns'])):
                        asset_return = data['returns'][date_idx]
                        daily_return += weights.get(ticker, 0) * asset_return
                except ValueError:
                    continue
            
            portfolio_returns.append(daily_return)
        
        return portfolio_returns
    
    def update_results_display(self, annual_return, annual_volatility):
        """Обновление отображения результатов"""
        sharpe_color = "green" if self.sharpe_ratio > 1 else "orange" if self.sharpe_ratio > 0 else "red"
        
        self.sharpe_label.config(
            text=f"Коэффициент Шарпа: {self.sharpe_ratio:.2f}",
            foreground=sharpe_color
        )
        
        self.return_label.config(
            text=f"Средняя доходность: {annual_return:.2f}% годовых"
        )
        
        self.volatility_label.config(
            text=f"Волатильность: {annual_volatility:.2f}% годовых"
        )
    
    def update_returns_chart(self, portfolio_returns):
        """Обновление графика доходности"""
        self.returns_ax.clear()
        
        # Кумулятивная доходность
        cumulative_returns = [100]  # Начальная стоимость 100
        for ret in portfolio_returns:
            cumulative_returns.append(cumulative_returns[-1] * (1 + ret/100))
        
        self.returns_ax.plot(range(len(cumulative_returns)), cumulative_returns, 
                           linewidth=2, color='blue')
        
        self.returns_ax.set_title('Доходность портфеля', fontsize=14, fontweight='bold', pad=20)
        self.returns_ax.set_xlabel('Дни', fontsize=10)
        self.returns_ax.set_ylabel('Стоимость портфеля (база=100)', fontsize=10)
        self.returns_ax.grid(True, alpha=0.3)
        self.returns_ax.legend([f'Портфель (Sharpe: {self.sharpe_ratio:.2f})'])
        
        self.returns_canvas.draw_idle()
    
    def update_details_table(self, portfolio_returns):
        """Обновление таблицы с детальной информацией"""
        # Очищаем таблицу
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
        
        total_value = sum(stock.get('current_value', 0) for stock in self.portfolio_data)
        
        for stock in self.portfolio_data:
            ticker = stock['ticker']
            weight = (stock.get('current_value', 0) / total_value * 100) if total_value > 0 else 0
            
            if ticker in self.historical_data:
                asset_returns = self.historical_data[ticker]['returns']
                if asset_returns:
                    asset_avg_return = np.mean(asset_returns) * 252  # Годовая доходность
                    asset_volatility = np.std(asset_returns) * np.sqrt(252)
                    
                    if asset_volatility != 0:
                        asset_sharpe = (asset_avg_return - float(self.risk_free_var.get())) / asset_volatility
                    else:
                        asset_sharpe = 0
                    
                    # Расчет корреляции с портфелем
                    if len(asset_returns) == len(portfolio_returns):
                        correlation = np.corrcoef(asset_returns, portfolio_returns)[0,1]
                    else:
                        correlation = 0
                    
                    self.details_tree.insert("", tk.END, values=(
                        ticker,
                        f"{weight:.1f}%",
                        f"{asset_avg_return:.2f}%",
                        f"{asset_volatility:.2f}%",
                        f"{asset_sharpe:.2f}",
                        f"{correlation:.2f}"
                    ))
    
    def export_report(self):
        """Экспорт отчета в CSV"""
        try:
            if not self.portfolio_data:
                messagebox.showwarning("Экспорт", "Нет данных для экспорта")
                return
            
            filename = f"sharpe_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                import csv
                writer = csv.writer(file, delimiter=';')
                
                # Заголовок отчета
                writer.writerow(["Отчет по коэффициенту Шарпа"])
                writer.writerow([f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}"])
                writer.writerow([f"Безрисковая ставка: {self.risk_free_var.get()}%"])
                writer.writerow([f"Период анализа: {self.period_var.get()} дней"])
                writer.writerow([])
                
                # Основные показатели
                writer.writerow(["ОСНОВНЫЕ ПОКАЗАТЕЛИ"])
                writer.writerow(["Коэффициент Шарпа", f"{self.sharpe_ratio:.2f}"])
                
                # Детали по активам
                writer.writerow([])
                writer.writerow(["ДЕТАЛИ ПО АКТИВАМ"])
                writer.writerow(["Тикер", "Вес (%)", "Доходность (%)", "Волатильность (%)", 
                               "Коэф. Шарпа", "Корреляция"])
                
                for item in self.details_tree.get_children():
                    values = self.details_tree.item(item, "values")
                    writer.writerow(values)
            
            messagebox.showinfo("Экспорт", f"Отчет экспортирован в файл:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать отчет: {e}")
    
    def focus(self):
        """Активация окна"""
        self.window.focus_force()
    
    def close(self):
        """Закрытие окна"""
        self.window.destroy()