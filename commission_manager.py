# commission_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
class CommissionManager:
    """
    Менеджер комиссий для учета торговых издержек
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.commission_data = {
            'broker_commission': 0.05,  # Комиссия брокера в %
            'exchange_commission': 0.01,  # Комиссия биржи в %
            'min_commission': 0.0,  # Минимальная комиссия в руб
            'tax_rate': 13.0,  # Налог на доход в %
            'other_costs': 0.0  # Прочие расходы в руб за сделку
        }
        
        self.load_commission_data()
    
    def load_commission_data(self):
        """Загрузка настроек комиссий из файла"""
        try:
            if os.path.exists('commission_settings.json'):
                with open('commission_settings.json', 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    self.commission_data.update(saved_data)
        except Exception as e:
            print(f"Ошибка загрузки настроек комиссий: {e}")
    
    def save_commission_data(self):
        """Сохранение настроек комиссий в файл"""
        try:
            with open('commission_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.commission_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек комиссий: {e}")
    
    def calculate_buy_commission(self, amount):
        """Расчет комиссий при покупке"""
        broker_commission = max(
            amount * (self.commission_data['broker_commission'] / 100),
            self.commission_data['min_commission']
        )
        exchange_commission = amount * (self.commission_data['exchange_commission'] / 100)
        total_commission = broker_commission + exchange_commission + self.commission_data['other_costs']
        
        return {
            'broker_commission': broker_commission,
            'exchange_commission': exchange_commission,
            'other_costs': self.commission_data['other_costs'],
            'total_commission': total_commission,
            'total_with_commission': amount + total_commission
        }
    
    def calculate_sell_commission(self, amount):
        """Расчет комиссий при продаже"""
        commission_calc = self.calculate_buy_commission(amount)
        
        # Добавляем расчет налога
        # Налог рассчитывается отдельно при фактической продаже
        return commission_calc
    
    def calculate_tax(self, buy_amount, sell_amount, quantity=1):
        """Расчет налога на доход"""
        profit = sell_amount - buy_amount
        if profit > 0:
            tax = profit * (self.commission_data['tax_rate'] / 100)
        else:
            tax = 0
        
        return tax
    
    def show_commission_settings(self):
        """Показать окно настроек комиссий"""
        settings_window = tk.Toplevel(self.parent)
        settings_window.title("Настройки комиссий и налогов")
        settings_window.geometry("500x500")
        settings_window.minsize(400, 350)
        
        main_frame = ttk.Frame(settings_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Настройки комиссий и налогов", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Поля для ввода комиссий
        entries = {}
        
        commission_frame = ttk.LabelFrame(main_frame, text="Торговые комиссии", padding="10")
        commission_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Комиссия брокера
        row_frame = ttk.Frame(commission_frame)
        row_frame.pack(fill=tk.X, pady=5)
        ttk.Label(row_frame, text="Комиссия брокера (%):", width=20).pack(side=tk.LEFT)
        broker_var = tk.StringVar(value=str(self.commission_data['broker_commission']))
        broker_entry = ttk.Entry(row_frame, textvariable=broker_var, width=10)
        broker_entry.pack(side=tk.LEFT)
        ttk.Label(row_frame, text="%").pack(side=tk.LEFT, padx=(5, 0))
        entries['broker_commission'] = broker_var
        
        # Комиссия биржи
        row_frame = ttk.Frame(commission_frame)
        row_frame.pack(fill=tk.X, pady=5)
        ttk.Label(row_frame, text="Комиссия биржи (%):", width=20).pack(side=tk.LEFT)
        exchange_var = tk.StringVar(value=str(self.commission_data['exchange_commission']))
        exchange_entry = ttk.Entry(row_frame, textvariable=exchange_var, width=10)
        exchange_entry.pack(side=tk.LEFT)
        ttk.Label(row_frame, text="%").pack(side=tk.LEFT, padx=(5, 0))
        entries['exchange_commission'] = exchange_var
        
        # Минимальная комиссия
        row_frame = ttk.Frame(commission_frame)
        row_frame.pack(fill=tk.X, pady=5)
        ttk.Label(row_frame, text="Мин. комиссия (руб):", width=20).pack(side=tk.LEFT)
        min_commission_var = tk.StringVar(value=str(self.commission_data['min_commission']))
        min_commission_entry = ttk.Entry(row_frame, textvariable=min_commission_var, width=10)
        min_commission_entry.pack(side=tk.LEFT)
        ttk.Label(row_frame, text="руб").pack(side=tk.LEFT, padx=(5, 0))
        entries['min_commission'] = min_commission_var
        
        # Прочие расходы
        row_frame = ttk.Frame(commission_frame)
        row_frame.pack(fill=tk.X, pady=5)
        ttk.Label(row_frame, text="Прочие расходы (руб):", width=20).pack(side=tk.LEFT)
        other_costs_var = tk.StringVar(value=str(self.commission_data['other_costs']))
        other_costs_entry = ttk.Entry(row_frame, textvariable=other_costs_var, width=10)
        other_costs_entry.pack(side=tk.LEFT)
        ttk.Label(row_frame, text="руб за сделку").pack(side=tk.LEFT, padx=(5, 0))
        entries['other_costs'] = other_costs_var
        
        # Налоговые настройки
        tax_frame = ttk.LabelFrame(main_frame, text="Налоговые настройки", padding="10")
        tax_frame.pack(fill=tk.X, pady=(0, 10))
        
        row_frame = ttk.Frame(tax_frame)
        row_frame.pack(fill=tk.X, pady=5)
        ttk.Label(row_frame, text="Налог на доход (%):", width=20).pack(side=tk.LEFT)
        tax_var = tk.StringVar(value=str(self.commission_data['tax_rate']))
        tax_entry = ttk.Entry(row_frame, textvariable=tax_var, width=10)
        tax_entry.pack(side=tk.LEFT)
        ttk.Label(row_frame, text="%").pack(side=tk.LEFT, padx=(5, 0))
        entries['tax_rate'] = tax_var
        
        # Пример расчета
        example_frame = ttk.LabelFrame(main_frame, text="Пример расчета", padding="10")
        example_frame.pack(fill=tk.X, pady=(0, 15))
        
        example_text = ("Пример для сделки на 10,000 руб:\n"
                       "Комиссия брокера: 5 руб\n"
                       "Комиссия биржи: 1 руб\n"
                       "Прочие расходы: 0 руб\n"
                       "Итого комиссий: 6 руб")
        
        example_label = ttk.Label(example_frame, text=example_text, justify=tk.LEFT)
        example_label.pack()
        
        def update_example():
            try:
                amount = 10000
                broker_comm = float(entries['broker_commission'].get()) / 100 * amount
                exchange_comm = float(entries['exchange_commission'].get()) / 100 * amount
                min_comm = float(entries['min_commission'].get())
                other_costs = float(entries['other_costs'].get())
                
                broker_comm = max(broker_comm, min_comm)
                total_comm = broker_comm + exchange_comm + other_costs
                
                example_text = (f"Пример для сделки на {amount:,.0f} руб:\n"
                              f"Комиссия брокера: {broker_comm:.2f} руб\n"
                              f"Комиссия биржи: {exchange_comm:.2f} руб\n"
                              f"Прочие расходы: {other_costs:.2f} руб\n"
                              f"Итого комиссий: {total_comm:.2f} руб")
                
                example_label.config(text=example_text)
            except:
                pass
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def save_settings():
            try:
                for key, var in entries.items():
                    value = float(var.get())
                    if key in ['broker_commission', 'exchange_commission', 'tax_rate']:
                        if value < 0 or value > 100:
                            raise ValueError(f"{key} должен быть между 0 и 100")
                    elif value < 0:
                        raise ValueError(f"{key} не может быть отрицательным")
                    
                    self.commission_data[key] = value
                
                self.save_commission_data()
                update_example()
                messagebox.showinfo("Успех", "Настройки комиссий сохранены!")
                
            except ValueError as e:
                messagebox.showerror("Ошибка", f"Некорректное значение: {e}")
        
        def reset_to_default():
            default_data = {
                'broker_commission': 0.05,
                'exchange_commission': 0.01,
                'min_commission': 0.0,
                'tax_rate': 13.0,
                'other_costs': 0.0
            }
            
            for key, value in default_data.items():
                entries[key].set(str(value))
            
            self.commission_data = default_data.copy()
            update_example()
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сбросить по умолчанию", 
                  command=reset_to_default).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Закрыть", 
                  command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Обновляем пример при изменении значений
        for var in entries.values():
            var.trace('w', lambda *args: update_example())
        
        update_example()
