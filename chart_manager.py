# chart_manager.py
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk

class ChartManager:
    """
    Класс для управления графиками акций.
    Создает и обновляет внутридневные и дневные графики.
    """
    
    def __init__(self):
        # Данные для графиков
        self.intraday_dates = []  # Внутридневные даты
        self.intraday_prices = []  # Внутридневные цены
        self.daily_data = []  # Данные за весь день (дата, цена)
        
        # Графики
        self.intraday_fig = None
        self.intraday_ax = None
        self.intraday_canvas = None
        
        self.daily_fig = None
        self.daily_ax = None
        self.daily_canvas = None
        
        # Настройки графиков
        self.chart_style = 'seaborn-v0_8-whitegrid'  # Стиль графиков
        plt.style.use(self.chart_style)
        
    def create_intraday_chart(self, parent_frame):
        """Создание внутридневного графика"""
        # Создаем фигуру и оси
        self.intraday_fig, self.intraday_ax = plt.subplots(figsize=(10, 4), dpi=100)
        
        # Настройка внешнего вида
        self.intraday_ax.set_title('Внутридневной график цен', fontsize=14, fontweight='bold', pad=20)
        self.intraday_ax.set_xlabel('Время', fontsize=10)
        self.intraday_ax.set_ylabel('Цена (руб)', fontsize=10)
        self.intraday_ax.grid(True, alpha=0.3)
        
        # Форматирование оси времени
        time_format = mdates.DateFormatter('%H:%M')
        self.intraday_ax.xaxis.set_major_formatter(time_format)
        self.intraday_ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        
        # Создаем холст для встраивания в Tkinter
        self.intraday_canvas = FigureCanvasTkAgg(self.intraday_fig, parent_frame)
        self.intraday_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Добавляем панель навигации
        # toolbar = NavigationToolbar2Tk(self.intraday_canvas, parent_frame)
        # toolbar.update()
        
    def create_daily_chart(self, parent_frame):
        """Создание графика за весь день"""
        # Создаем фигуру и оси
        self.daily_fig, self.daily_ax = plt.subplots(figsize=(10, 4), dpi=100)
        
        # Настройка внешнего вида
        self.daily_ax.set_title('График цен за день', fontsize=14, fontweight='bold', pad=20)
        self.daily_ax.set_xlabel('Время', fontsize=10)
        self.daily_ax.set_ylabel('Цена (руб)', fontsize=10)
        self.daily_ax.grid(True, alpha=0.3)
        
        # Форматирование оси времени
        time_format = mdates.DateFormatter('%H:%M')
        self.daily_ax.xaxis.set_major_formatter(time_format)
        self.daily_ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        
        # Создаем холст для встраивания в Tkinter
        self.daily_canvas = FigureCanvasTkAgg(self.daily_fig, parent_frame)
        self.daily_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def update_intraday_chart(self):
        """Обновление внутридневного графика"""
        if not self.intraday_dates or not self.intraday_prices:
            return
            
        self.intraday_ax.clear()
        
        # Рисуем линию графика
        line_color = 'green' if self.intraday_prices[-1] >= self.intraday_prices[0] else 'red'
        self.intraday_ax.plot(self.intraday_dates, self.intraday_prices, 
                             color=line_color, linewidth=2, marker='o', markersize=3)
        
        # Заполнение под графиком
        self.intraday_ax.fill_between(self.intraday_dates, self.intraday_prices, 
                                     alpha=0.3, color=line_color)
        
        # Настройка внешнего вида
        self.intraday_ax.set_title('Внутридневной график цен', fontsize=14, fontweight='bold', pad=20)
        self.intraday_ax.set_xlabel('Время', fontsize=10)
        self.intraday_ax.set_ylabel('Цена (руб)', fontsize=10)
        self.intraday_ax.grid(True, alpha=0.3)
        
        # Форматирование оси времени
        time_format = mdates.DateFormatter('%H:%M')
        self.intraday_ax.xaxis.set_major_formatter(time_format)
        self.intraday_ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        
        # Автомасштабирование
        self.intraday_ax.relim()
        self.intraday_ax.autoscale_view()
        
        # Поворот подписей дат
        plt.setp(self.intraday_ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Обновление холста
        self.intraday_canvas.draw_idle()
        
    def update_daily_chart(self):
        """Обновление графика за весь день"""
        if not self.daily_data:
            return
            
        dates = [d for d, p in self.daily_data]
        prices = [p for d, p in self.daily_data]
        
        self.daily_ax.clear()
        
        # Рисуем линию графика
        line_color = 'blue'
        if len(prices) > 1:
            line_color = 'green' if prices[-1] >= prices[0] else 'red'
            
        self.daily_ax.plot(dates, prices, color=line_color, linewidth=2, marker='o', markersize=2)
        
        # Настройка внешнего вида
        self.daily_ax.set_title('График цен за день', fontsize=14, fontweight='bold', pad=20)
        self.daily_ax.set_xlabel('Время', fontsize=10)
        self.daily_ax.set_ylabel('Цена (руб)', fontsize=10)
        self.daily_ax.grid(True, alpha=0.3)
        
        # Форматирование оси времени
        time_format = mdates.DateFormatter('%H:%M')
        self.daily_ax.xaxis.set_major_formatter(time_format)
        self.daily_ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        
        # Автомасштабирование
        self.daily_ax.relim()
        self.daily_ax.autoscale_view()
        
        # Поворот подписей дат
        plt.setp(self.daily_ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Обновление холста
        self.daily_canvas.draw_idle()
        
    def setup_zoom_buttons(self, parent_frame, chart_type):
        """Настройка кнопок масштабирования для графиков"""
        zoom_frame = ttk.Frame(parent_frame)
        zoom_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(zoom_frame, text=f"{chart_type}:").pack(side=tk.LEFT)
        
        ttk.Button(zoom_frame, text="1ч", 
                  command=lambda: self.zoom_chart(chart_type, '1h')).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="2ч", 
                  command=lambda: self.zoom_chart(chart_type, '2h')).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="4ч", 
                  command=lambda: self.zoom_chart(chart_type, '4h')).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="Весь день", 
                  command=lambda: self.zoom_chart(chart_type, 'all')).pack(side=tk.LEFT, padx=2)
        
    def zoom_chart(self, chart_type, period):
        """Масштабирование графика на указанный период"""
        if chart_type == 'intraday':
            ax = self.intraday_ax
            dates = self.intraday_dates
        else:
            ax = self.daily_ax
            dates = [d for d, p in self.daily_data]
        
        if not dates:
            return
            
        current_time = datetime.now()
        
        if period == '1h':
            start_time = current_time - timedelta(hours=1)
        elif period == '2h':
            start_time = current_time - timedelta(hours=2)
        elif period == '4h':
            start_time = current_time - timedelta(hours=4)
        else:  # 'all'
            start_time = dates[0] if dates else current_time - timedelta(hours=8)
        
        # Фильтруем данные по выбранному периоду
        filtered_dates = [d for d in dates if d >= start_time]
        
        if filtered_dates:
            ax.set_xlim([filtered_dates[0], filtered_dates[-1]])
            
            if chart_type == 'intraday':
                self.intraday_canvas.draw_idle()
            else:
                self.daily_canvas.draw_idle()
        
    def clear_charts(self):
        """Очистка всех графиков"""
        self.intraday_dates.clear()
        self.intraday_prices.clear()
        self.daily_data.clear()
        
        if self.intraday_ax:
            self.intraday_ax.clear()
            self.intraday_ax.set_title('Внутридневной график цен', fontsize=14, fontweight='bold', pad=20)
            self.intraday_ax.set_xlabel('Время', fontsize=10)
            self.intraday_ax.set_ylabel('Цена (руб)', fontsize=10)
            self.intraday_ax.grid(True, alpha=0.3)
            self.intraday_canvas.draw_idle()
        
        if self.daily_ax:
            self.daily_ax.clear()
            self.daily_ax.set_title('График цен за день', fontsize=14, fontweight='bold', pad=20)
            self.daily_ax.set_xlabel('Время', fontsize=10)
            self.daily_ax.set_ylabel('Цена (руб)', fontsize=10)
            self.daily_ax.grid(True, alpha=0.3)
            self.daily_canvas.draw_idle()