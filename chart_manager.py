# chart_manager.py
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib.widgets import Cursor
import matplotlib.transforms as transforms

class ChartManager:
    """
    Класс для управления графиками и их отображением.
    Обеспечивает функциональность масштабирования, панорамирования и обновления графиков.
    """
    
    def __init__(self):
        # Данные для внутридневного графика
        self.intraday_dates = []
        self.intraday_prices = []
        self.daily_data = []
        
        # Переменные для управления зумом
        self.zoom_stack_intraday = []  # Стек состояний масштаба для внутридневного графика
        self.zoom_stack_daily = []     # Стек состояний масштаба для дневного графика
        self.zoom_active = False       # Флаг активного масштабирования
        self.zoom_start = None         # Начальная точка выделения
        self.zoom_end = None           # Конечная точка выделения
        self.rect = None               # Прямоугольник выделения
        
    def create_intraday_chart(self, parent):
        """Создание внутридневного графика"""
        # Создание фигуры и осей
        self.fig_intraday, self.ax_intraday = plt.subplots(figsize=(12, 6))
        
        # Настраиваем layout перед созданием canvas
        self.fig_intraday.subplots_adjust(bottom=0.15, top=0.95, left=0.08, right=0.95)
        
        # Создание canvas для Tkinter
        self.canvas_intraday = FigureCanvasTkAgg(self.fig_intraday, parent)
        self.canvas_intraday.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        # Добавляем курсор
        self.cursor_intraday = Cursor(self.ax_intraday, useblit=True, color='red', linewidth=1)
        
        # Настраиваем события для мыши
        self.canvas_intraday.mpl_connect('button_press_event', self.on_click_intraday)
        self.canvas_intraday.mpl_connect('button_release_event', self.on_release_intraday)
        self.canvas_intraday.mpl_connect('motion_notify_event', self.on_motion_intraday)
        self.canvas_intraday.mpl_connect('scroll_event', self.on_scroll_intraday)
        
        # Настройка осей графика
        self._configure_chart_axes(self.ax_intraday, 'Внутридневной график SBER (реальное время)')
        
        # Добавляем кнопки управления
        self._add_zoom_controls(self.fig_intraday, self.ax_intraday, 'intraday')
        
    def create_daily_chart(self, parent):
        """Создание дневного графика"""
        # Создание фигуры и осей
        self.fig_daily, self.ax_daily = plt.subplots(figsize=(12, 6))
        
        # Настраиваем layout перед созданием canvas
        self.fig_daily.subplots_adjust(bottom=0.15, top=0.95, left=0.08, right=0.95)
        
        # Создание canvas для Tkinter
        self.canvas_daily = FigureCanvasTkAgg(self.fig_daily, parent)
        self.canvas_daily.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        # Добавляем курсор
        self.cursor_daily = Cursor(self.ax_daily, useblit=True, color='red', linewidth=1)
        
        # Настраиваем события для мыши
        self.canvas_daily.mpl_connect('button_press_event', self.on_click_daily)
        self.canvas_daily.mpl_connect('button_release_event', self.on_release_daily)
        self.canvas_daily.mpl_connect('motion_notify_event', self.on_motion_daily)
        self.canvas_daily.mpl_connect('scroll_event', self.on_scroll_daily)
        
        # Настройка осей графика
        self._configure_chart_axes(self.ax_daily, 'График SBER за торговый день')
        
        # Добавляем кнопки управления
        self._add_zoom_controls(self.fig_daily, self.ax_daily, 'daily')
    
    def _add_zoom_controls(self, fig, ax, chart_type):
        """Добавляет элементы управления зумом на график"""
        import matplotlib.patches as patches
        
        # Создаем кнопки с использованием tkinter вместо matplotlib.widgets.Button
        # Кнопки будут добавлены в интерфейс основного окна
        
        # Сохраняем ссылки на фигуру и оси для использования в методах масштабирования
        if chart_type == 'intraday':
            self.fig_intraday_ref = fig
            self.ax_intraday_ref = ax
        else:
            self.fig_daily_ref = fig
            self.ax_daily_ref = ax
    
    def setup_zoom_buttons(self, button_frame, chart_type):
        """Создает кнопки управления масштабом в основном интерфейсе"""
        import tkinter as tk
        from tkinter import ttk
        
        zoom_frame = ttk.Frame(button_frame)
        zoom_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(zoom_frame, text="Масштаб:").pack(side=tk.LEFT, padx=2)
        
        zoom_in_btn = ttk.Button(zoom_frame, text="+", width=3,
                               command=lambda: self.zoom_in(chart_type))
        zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
        zoom_out_btn = ttk.Button(zoom_frame, text="-", width=3,
                                command=lambda: self.zoom_out(chart_type))
        zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        reset_btn = ttk.Button(zoom_frame, text="Сброс", 
                             command=lambda: self.reset_zoom(chart_type))
        reset_btn.pack(side=tk.LEFT, padx=2)
    
    def on_click_intraday(self, event):
        """Обработчик нажатия мыши для внутридневного графика"""
        if event.inaxes == self.ax_intraday:
            if event.button == 1:  # Левая кнопка мыши
                self.zoom_active = True
                self.zoom_start = (event.xdata, event.ydata)
                # Удаляем предыдущий прямоугольник если есть
                if hasattr(self, 'rect_intraday') and self.rect_intraday:
                    self.rect_intraday.remove()
                    self.rect_intraday = None
    
    def on_release_intraday(self, event):
        """Обработчик отпускания мыши для внутридневного графика"""
        if event.inaxes == self.ax_intraday and self.zoom_active:
            if event.button == 1:  # Левая кнопка мыши
                self.zoom_active = False
                self.zoom_end = (event.xdata, event.ydata)
                
                # Удаляем прямоугольник выделения
                if hasattr(self, 'rect_intraday') and self.rect_intraday:
                    self.rect_intraday.remove()
                    self.rect_intraday = None
                
                # Если область выделения достаточно большая, применяем зум
                if (self.zoom_start and self.zoom_end and 
                    abs(self.zoom_end[0] - self.zoom_start[0]) > 0.1 and
                    abs(self.zoom_end[1] - self.zoom_start[1]) > 0.1):
                    
                    # Сохраняем текущие пределы в стек
                    self.zoom_stack_intraday.append({
                        'xlim': self.ax_intraday.get_xlim(),
                        'ylim': self.ax_intraday.get_ylim()
                    })
                    
                    # Устанавливаем новые пределы
                    x_min = min(self.zoom_start[0], self.zoom_end[0])
                    x_max = max(self.zoom_start[0], self.zoom_end[0])
                    y_min = min(self.zoom_start[1], self.zoom_end[1])
                    y_max = max(self.zoom_start[1], self.zoom_end[1])
                    
                    self.ax_intraday.set_xlim(x_min, x_max)
                    self.ax_intraday.set_ylim(y_min, y_max)
                    self.canvas_intraday.draw()
    
    def on_motion_intraday(self, event):
        """Обработчик движения мыши для внутридневного графика"""
        if event.inaxes == self.ax_intraday and self.zoom_active and self.zoom_start:
            # Удаляем предыдущий прямоугольник
            if hasattr(self, 'rect_intraday') and self.rect_intraday:
                self.rect_intraday.remove()
            
            # Создаем новый прямоугольник выделения
            width = event.xdata - self.zoom_start[0]
            height = event.ydata - self.zoom_start[1]
            
            self.rect_intraday = plt.Rectangle((self.zoom_start[0], self.zoom_start[1]), 
                                             width, height, 
                                             fill=False, edgecolor='red', linewidth=2,
                                             alpha=0.5)
            self.ax_intraday.add_patch(self.rect_intraday)
            self.canvas_intraday.draw()
    
    def on_scroll_intraday(self, event):
        """Обработчик прокрутки колесика мыши для внутридневного графика"""
        if event.inaxes == self.ax_intraday:
            # Сохраняем текущие пределы
            self.zoom_stack_intraday.append({
                'xlim': self.ax_intraday.get_xlim(),
                'ylim': self.ax_intraday.get_ylim()
            })
            
            # Определяем центр масштабирования
            x_center = event.xdata if event.xdata else (self.ax_intraday.get_xlim()[0] + self.ax_intraday.get_xlim()[1]) / 2
            y_center = event.ydata if event.ydata else (self.ax_intraday.get_ylim()[0] + self.ax_intraday.get_ylim()[1]) / 2
            
            # Коэффициент масштабирования
            scale_factor = 1.2 if event.button == 'up' else 0.8
            
            # Получаем текущие пределы
            x_min, x_max = self.ax_intraday.get_xlim()
            y_min, y_max = self.ax_intraday.get_ylim()
            
            # Масштабируем
            new_x_range = (x_max - x_min) * scale_factor
            new_y_range = (y_max - y_min) * scale_factor
            
            # Устанавливаем новые пределы
            self.ax_intraday.set_xlim([x_center - new_x_range/2, x_center + new_x_range/2])
            self.ax_intraday.set_ylim([y_center - new_y_range/2, y_center + new_y_range/2])
            
            self.canvas_intraday.draw()
    
    def on_click_daily(self, event):
        """Обработчик нажатия мыши для дневного графика"""
        if event.inaxes == self.ax_daily:
            if event.button == 1:  # Левая кнопка мыши
                self.zoom_active = True
                self.zoom_start = (event.xdata, event.ydata)
                # Удаляем предыдущий прямоугольник если есть
                if hasattr(self, 'rect_daily') and self.rect_daily:
                    self.rect_daily.remove()
                    self.rect_daily = None
    
    def on_release_daily(self, event):
        """Обработчик отпускания мыши для дневного графика"""
        if event.inaxes == self.ax_daily and self.zoom_active:
            if event.button == 1:  # Левая кнопка мыши
                self.zoom_active = False
                self.zoom_end = (event.xdata, event.ydata)
                
                # Удаляем прямоугольник выделения
                if hasattr(self, 'rect_daily') and self.rect_daily:
                    self.rect_daily.remove()
                    self.rect_daily = None
                
                # Если область выделения достаточно большая, применяем зум
                if (self.zoom_start and self.zoom_end and 
                    abs(self.zoom_end[0] - self.zoom_start[0]) > 0.1 and
                    abs(self.zoom_end[1] - self.zoom_start[1]) > 0.1):
                    
                    # Сохраняем текущие пределы в стек
                    self.zoom_stack_daily.append({
                        'xlim': self.ax_daily.get_xlim(),
                        'ylim': self.ax_daily.get_ylim()
                    })
                    
                    # Устанавливаем новые пределы
                    x_min = min(self.zoom_start[0], self.zoom_end[0])
                    x_max = max(self.zoom_start[0], self.zoom_end[0])
                    y_min = min(self.zoom_start[1], self.zoom_end[1])
                    y_max = max(self.zoom_start[1], self.zoom_end[1])
                    
                    self.ax_daily.set_xlim(x_min, x_max)
                    self.ax_daily.set_ylim(y_min, y_max)
                    self.canvas_daily.draw()
    
    def on_motion_daily(self, event):
        """Обработчик движения мыши для дневного графика"""
        if event.inaxes == self.ax_daily and self.zoom_active and self.zoom_start:
            # Удаляем предыдущий прямоугольник
            if hasattr(self, 'rect_daily') and self.rect_daily:
                self.rect_daily.remove()
            
            # Создаем новый прямоугольник выделения
            width = event.xdata - self.zoom_start[0]
            height = event.ydata - self.zoom_start[1]
            
            self.rect_daily = plt.Rectangle((self.zoom_start[0], self.zoom_start[1]), 
                                          width, height, 
                                          fill=False, edgecolor='red', linewidth=2,
                                          alpha=0.5)
            self.ax_daily.add_patch(self.rect_daily)
            self.canvas_daily.draw()
    
    def on_scroll_daily(self, event):
        """Обработчик прокрутки колесика мыши для дневного графика"""
        if event.inaxes == self.ax_daily:
            # Сохраняем текущие пределы
            self.zoom_stack_daily.append({
                'xlim': self.ax_daily.get_xlim(),
                'ylim': self.ax_daily.get_ylim()
            })
            
            # Определяем центр масштабирования
            x_center = event.xdata if event.xdata else (self.ax_daily.get_xlim()[0] + self.ax_daily.get_xlim()[1]) / 2
            y_center = event.ydata if event.ydata else (self.ax_daily.get_ylim()[0] + self.ax_daily.get_ylim()[1]) / 2
            
            # Коэффициент масштабирования
            scale_factor = 1.2 if event.button == 'up' else 0.8
            
            # Получаем текущие пределы
            x_min, x_max = self.ax_daily.get_xlim()
            y_min, y_max = self.ax_daily.get_ylim()
            
            # Масштабируем
            new_x_range = (x_max - x_min) * scale_factor
            new_y_range = (y_max - y_min) * scale_factor
            
            # Устанавливаем новые пределы
            self.ax_daily.set_xlim([x_center - new_x_range/2, x_center + new_x_range/2])
            self.ax_daily.set_ylim([y_center - new_y_range/2, y_center + new_y_range/2])
            
            self.canvas_daily.draw()
    
    def zoom_in(self, chart_type):
        """Увеличение масштаба"""
        if chart_type == 'intraday':
            ax = self.ax_intraday
            canvas = self.canvas_intraday
            zoom_stack = self.zoom_stack_intraday
        else:
            ax = self.ax_daily
            canvas = self.canvas_daily
            zoom_stack = self.zoom_stack_daily
        
        # Сохраняем текущие пределы
        zoom_stack.append({
            'xlim': ax.get_xlim(),
            'ylim': ax.get_ylim()
        })
        
        # Уменьшаем диапазон осей (увеличение)
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        
        x_range = (x_max - x_min) * 0.7  # Увеличиваем на 30%
        y_range = (y_max - y_min) * 0.7
        
        ax.set_xlim([x_center - x_range/2, x_center + x_range/2])
        ax.set_ylim([y_center - y_range/2, y_center + y_range/2])
        
        canvas.draw()
    
    def zoom_out(self, chart_type):
        """Уменьшение масштаба"""
        if chart_type == 'intraday':
            ax = self.ax_intraday
            canvas = self.canvas_intraday
            zoom_stack = self.zoom_stack_intraday
        else:
            ax = self.ax_daily
            canvas = self.canvas_daily
            zoom_stack = self.zoom_stack_daily
        
        # Сохраняем текущие пределы
        zoom_stack.append({
            'xlim': ax.get_xlim(),
            'ylim': ax.get_ylim()
        })
        
        # Увеличиваем диапазон осей (уменьшение)
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        
        x_range = (x_max - x_min) * 1.3  # Уменьшаем на 30%
        y_range = (y_max - y_min) * 1.3
        
        ax.set_xlim([x_center - x_range/2, x_center + x_range/2])
        ax.set_ylim([y_center - y_range/2, y_center + y_range/2])
        
        canvas.draw()
    
    def reset_zoom(self, chart_type):
        """Сброс масштаба к исходному состоянию"""
        if chart_type == 'intraday':
            ax = self.ax_intraday
            canvas = self.canvas_intraday
            zoom_stack = self.zoom_stack_intraday
        else:
            ax = self.ax_daily
            canvas = self.canvas_daily
            zoom_stack = self.zoom_stack_daily
        
        # Очищаем стек масштабирования
        zoom_stack.clear()
        
        # Автоматически устанавливаем пределы
        ax.relim()
        ax.autoscale_view()
        
        canvas.draw()
    
    def _configure_chart_axes(self, ax, title):
        """Настройка осей графика"""
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Время', fontsize=12)
        ax.set_ylabel('Цена (руб)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Форматирование оси времени
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        
        # Поворачиваем метки времени для лучшей читаемости
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def update_intraday_chart(self):
        """Обновление внутридневного графика"""
        if not self.intraday_dates or not self.intraday_prices:
            return
        
        self.ax_intraday.clear()
        
        # Рисуем график
        self.ax_intraday.plot(self.intraday_dates, self.intraday_prices, 
                             linewidth=2, color='blue', marker='o', markersize=3)
        
        # Настройка осей
        self._configure_chart_axes(self.ax_intraday, 'Внутридневной график SBER (реальное время)')
        
        # Форматирование времени для внутридневного графика
        self.ax_intraday.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax_intraday.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        
        self.canvas_intraday.draw()
    
    def update_daily_chart(self):
        """Обновление дневного графика"""
        if not self.daily_data:
            return
        
        dates = [d for d, p in self.daily_data]
        prices = [p for d, p in self.daily_data]
        
        self.ax_daily.clear()
        
        # Рисуем график
        self.ax_daily.plot(dates, prices, linewidth=2, color='green', marker='o', markersize=3)
        
        # Настройка осей
        self._configure_chart_axes(self.ax_daily, 'График SBER за торговый день')
        
        # Форматирование времени для дневного графика
        self.ax_daily.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax_daily.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        
        self.canvas_daily.draw()
    
    def clear_charts(self):
        """Очистка всех графиков"""
        self.intraday_dates.clear()
        self.intraday_prices.clear()
        self.daily_data.clear()
        
        self.ax_intraday.clear()
        self.ax_daily.clear()
        
        self._configure_chart_axes(self.ax_intraday, 'Внутридневной график SBER (реальное время)')
        self._configure_chart_axes(self.ax_daily, 'График SBER за торговый день')
        
        self.canvas_intraday.draw()
        self.canvas_daily.draw()