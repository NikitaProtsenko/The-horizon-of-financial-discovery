# etf_portfolio/etf_transactions.py
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


class ETFTransactionManager:
    """
    Менеджер для работы с транзакциями ETF
    """
    
    def __init__(self):
        self.history_file = 'etf_transaction_history.json'
    
    def record_transaction(self, ticker, operation, quantity, price):
        """Запись операции в историю транзакций ETF"""
        try:
            # Загружаем существующую историю
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
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
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Ошибка сохранения истории транзакций ETF: {e}")
    
    def show_transaction_history(self, parent_window):
        """Показать историю транзакций ETF"""
        try:
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            if not history:
                messagebox.showinfo("История операций", "История операций ETF пуста")
                return
            
            # Создаем окно истории
            history_window = tk.Toplevel(parent_window)
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
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                messagebox.showinfo("Успех", "История операций ETF очищена")
                parent_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось очистить историю: {e}")