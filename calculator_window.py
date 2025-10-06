# calculator_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime

class CalculatorWindow:
    """
    Окно калькулятора стоимости акций с таблицей для расчетов.
    Позволяет рассчитывать показатели для IBO.
    """
    
    def __init__(self, parent, stock_name=""):
        """
        Инициализация окна калькулятора.
        
        Args:
            parent: Родительское окно
            stock_name: Название облигации 
        """
        self.parent = parent
        self.stock_name = stock_name
        
        # Создание окна
        self.window = tk.Toplevel(parent)
        self.window.title(f"Калькулятор для IBO")
        self.window.geometry("900x600")
        self.window.minsize(700, 400)
        
        # Инициализация переменных
        self.stats_label = None
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обработчик закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    def create_widgets(self):
        """Создание элементов интерфейса калькулятора"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text=f"Калькулятор для IBO", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Информационная панель
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_label = ttk.Label(info_frame, 
                                   text="Дважды щелкните по ячейке для редактирования. Купоны указываются в % от цены акции.", 
                                   font=("Arial", 9), foreground="gray")
        self.info_label.pack(side=tk.LEFT)
        
        # Таблица для ввода данных
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Создание таблицы
        self.create_table(table_frame)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Добавить строку", 
                  command=self.add_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить строку", 
                  command=self.delete_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Рассчитать все", 
                  command=self.calculate_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить все", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт в CSV", 
                  command=self.export_to_csv).pack(side=tk.RIGHT, padx=5)
        
        # Статистика
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, 
                                    text="Всего позиций: 0 | Общий месячный доход: 0.00 руб", 
                                    font=("Arial", 9, "bold"))
        self.stats_label.pack()
        
        # Первоначальное обновление статистики
        self.update_statistics()
    
    def create_table(self, parent):
        """Создание таблицы с изменяемыми ячейками"""
        # Создание фрейма с прокруткой
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Создание Treeview (таблицы)
        columns = ("quantity", "price", "cost", "tax", "min_coupon", 
                  "max_coupon", "income_min", "income_max")
        
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        headers = {
            "quantity": "Кол-во",
            "price": "Цена покупки (руб)",
            "cost": "Стоимость (руб)",
            "tax": "Налог (%)",
            "min_coupon": "Мин купон (%)",
            "max_coupon": "Макс купон (%)",
            "income_min": "Доход в месяц мин. (руб)",
            "income_max": "Доход в месяц макс. (руб)"
        }
        
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=110, minwidth=90)
        
        # Добавление прокрутки
        v_scroll = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Размещение элементов
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        # Настройка весов для растягивания
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        
        # Привязка событий для редактирования
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Добавляем начальную строку
        self.add_row()
    
    def add_row(self):
        """Добавление новой строки в таблицу"""
        # Значения по умолчанию (купон в %)
        default_values = ("100", "0.00", "0.00", "13", "0.5", "1.0", "0.00", "0.00")
        self.tree.insert("", tk.END, values=default_values)
        
        # Пересчитываем статистику (только если stats_label уже создан)
        if hasattr(self, 'stats_label') and self.stats_label:
            self.update_statistics()
    
    def delete_row(self):
        """Удаление выбранной строки из таблицы"""
        selected = self.tree.selection()
        if selected:
            for item in selected:
                self.tree.delete(item)
            self.update_statistics()
        else:
            messagebox.showwarning("Внимание", "Выберите строку для удаления")
    
    def on_double_click(self, event):
        """Обработчик двойного клика для редактирования ячеек"""
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if not item:
            return
            
        col_index = int(column[1:]) - 1
        
        # Определяем, какие столбцы можно редактировать
        editable_columns = [0, 1, 3, 4, 5]  # quantity, price, tax, min_coupon, max_coupon
        
        if col_index in editable_columns:
            self.edit_cell(item, column)
    
    def edit_cell(self, item, column):
        """Редактирование ячейки таблицы"""
        # Получаем текущее значение
        col_index = int(column[1:]) - 1
        current_value = self.tree.item(item, "values")[col_index]
        
        # Создаем окно редактирования
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Редактирование")
        edit_window.geometry("300x120")
        edit_window.transient(self.window)
        edit_window.grab_set()
        edit_window.resizable(False, False)
        
        # Центрируем окно
        edit_window.transient(self.window)
        edit_window.geometry("+%d+%d" % (
            self.window.winfo_rootx() + 50,
            self.window.winfo_rooty() + 50
        ))
        
        ttk.Label(edit_window, text="Введите новое значение:").pack(pady=5)
        
        entry_var = tk.StringVar(value=current_value)
        entry = ttk.Entry(edit_window, textvariable=entry_var, width=20)
        entry.pack(pady=5)
        entry.focus()
        entry.select_range(0, tk.END)
        
        def save_edit():
            new_value = entry_var.get().strip()
            if not new_value:
                messagebox.showwarning("Ошибка", "Значение не может быть пустым")
                return
                
            try:
                # Проверяем, что значение числовое
                float_value = float(new_value)
                if float_value < 0:
                    messagebox.showwarning("Ошибка", "Значение не может быть отрицательным")
                    return
                    
                # Обновляем значение в таблице
                values = list(self.tree.item(item, "values"))
                values[col_index] = new_value
                self.tree.item(item, values=values)
                
                # Пересчитываем зависимые значения
                self.calculate_row_values(item)
                self.update_statistics()
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите числовое значение")
        
        def cancel_edit():
            edit_window.destroy()
        
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Сохранить", command=save_edit).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Отмена", command=cancel_edit).pack(side=tk.RIGHT, padx=10)
        
        # Сохраняем при нажатии Enter
        entry.bind("<Return>", lambda e: save_edit())
        entry.bind("<Escape>", lambda e: cancel_edit())
        
        # Обработка закрытия окна
        edit_window.protocol("WM_DELETE_WINDOW", cancel_edit)
    
    def calculate_row_values(self, item):
        """Пересчет значений для строки - доход в месяц: (кол-во * купон_в_рублях) - налог"""
        values = list(self.tree.item(item, "values"))
        
        try:
            # Парсим значения
            quantity = float(values[0]) if values[0] else 0
            price = float(values[1]) if values[1] else 0
            tax_rate = float(values[3]) if values[3] else 0
            min_coupon_percent = float(values[4]) if values[4] else 0  # Купон в %
            max_coupon_percent = float(values[5]) if values[5] else 0  # Купон в %
            
            # Расчет стоимости покупки
            cost = quantity * price
            values[2] = f"{cost:.2f}"
            
            # Переводим купоны из % в рубли
            min_coupon_rub = price * (min_coupon_percent / 100)/12
            max_coupon_rub = price * (max_coupon_percent / 100)/12
            
            # Расчет месячного дохода для минимального купона
            # Доход = (кол-во * купон_в_рублях) - налог
            gross_income_min = quantity * min_coupon_rub
            tax_min = gross_income_min * (tax_rate / 100)
            net_income_min = gross_income_min - tax_min
            values[6] = f"{net_income_min:.2f}"
            
            # Расчет месячного дохода для максимального купона
            gross_income_max = quantity * max_coupon_rub
            tax_max = gross_income_max * (tax_rate / 100)
            net_income_max = gross_income_max - tax_max
            values[7] = f"{net_income_max:.2f}"
            
            # Обновляем строку
            self.tree.item(item, values=values)
            
        except ValueError as e:
            print(f"Ошибка расчета: {e}")
    
    def calculate_all(self):
        """Пересчет всех строк в таблице"""
        for item in self.tree.get_children():
            self.calculate_row_values(item)
        self.update_statistics()
        messagebox.showinfo("Расчет", "Все расчеты выполнены!")
    
    def clear_all(self):
        """Очистка всех данных в таблице"""
        if messagebox.askyesno("Подтверждение", "Очистить все данные?"):
            for item in self.tree.get_children():
                self.tree.delete(item)
            # Добавляем пустую строку
            self.add_row()
            self.update_statistics()
    
    def update_statistics(self):
        """Обновление статистики - общий месячный доход"""
        # Проверяем, что stats_label существует
        if not hasattr(self, 'stats_label') or not self.stats_label:
            return
            
        total_positions = len(self.tree.get_children())
        total_income_min = 0.0
        total_income_max = 0.0
        
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            try:
                total_income_min += float(values[6]) if values[6] else 0
                total_income_max += float(values[7]) if values[7] else 0
            except ValueError:
                pass
        
        self.stats_label.config(
            text=f"Всего позиций: {total_positions} | Месячный доход: {total_income_min:.2f} - {total_income_max:.2f} руб"
        )
    
    def export_to_csv(self):
        """Экспорт данных таблицы в CSV файл"""
        try:
            if not self.tree.get_children():
                messagebox.showwarning("Экспорт", "Нет данных для экспорта")
                return
                
            filename = f"income_calculator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                
                # Заголовки
                headers = ["Кол-во", "Цена покупки", "Стоимость покупки", "Налог %", 
                          "Мин купон %", "Макс купон %", "Доход в месяц мин", "Доход в месяц макс"]
                writer.writerow(headers)
                
                # Данные
                for item in self.tree.get_children():
                    values = self.tree.item(item, "values")
                    writer.writerow(values)
            
            messagebox.showinfo("Экспорт", f"Данные экспортированы в файл:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")
    
    def focus(self):
        """Активация окна"""
        self.window.focus_force()
    
    def close(self):
        """Закрытие окна"""
        self.window.destroy()
        if hasattr(self, 'parent') and hasattr(self.parent, 'calculator_windows'):
            if self in self.parent.calculator_windows:
                self.parent.calculator_windows.remove(self)
                if hasattr(self.parent, 'update_windows_menu'):
                    self.parent.update_windows_menu()
