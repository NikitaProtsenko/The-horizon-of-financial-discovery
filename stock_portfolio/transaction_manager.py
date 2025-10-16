# Менеджер транзакций - история операций покупки/продажи
import json
import os
from datetime import datetime
from tkinter import messagebox, ttk
import tkinter as tk

class TransactionManager:
    """
    Управление историей транзакций: запись, отображение, очистка операций.
    """
    
    def __init__(self, portfolio_manager):
        """
        Инициализация менеджера транзакций.
        
        Args:
            portfolio_manager: ссылка на менеджер портфеля
        """
        self.portfolio_manager = portfolio_manager
        self.transaction_history = []
        self.load_transaction_history()
    
    def load_transaction_history(self):
        """Загрузка истории транзакций из JSON файла"""
        try:
            if os.path.exists('transaction_history.json'):
                with open('transaction_history.json', 'r', encoding='utf-8') as f:
                    self.transaction_history = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки истории транзакций: {e}")
            self.transaction_history = []
    
    def save_transaction_history(self):
        """Сохранение истории транзакций в JSON файл"""
        try:
            with open('transaction_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.transaction_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории транзакций: {e}")
    
    def record_transaction(self, ticker, operation, quantity, price):
        """
        Запись транзакции в историю.
        
        Args:
            ticker: тикер акции
            operation: тип операции ('buy' или 'sell')
            quantity: количество акций
            price: цена за акцию
        """
        try:
            # Создаем запись о транзакции
            transaction = {
                'date': datetime.now().isoformat(),
                'ticker': ticker,
                'operation': operation,
                'quantity': quantity,
                'price': price,
                'total': quantity * price
            }
            
            # Добавляем в историю
            self.transaction_history.append(transaction)
            
            # Сохраняем историю
            self.save_transaction_history()
                
        except Exception as e:
            print(f"Ошибка сохранения истории транзакций: {e}")
    
    def show_transaction_history(self, parent_window):
        """Показать историю транзакций"""
        try:
            if not self.transaction_history:
                from tkinter import messagebox
                messagebox.showinfo("История операций", "История операций пуста")
                return
            
            # Создаем окно истории
            history_window = tk.Toplevel(parent_window)  # Используем переданный parent_window
            history_window.title("История операций")
            history_window.geometry("800x400")
            
            # Основной фрейм
            table_frame = ttk.Frame(history_window, padding="10")
            table_frame.pack(fill=tk.BOTH, expand=True)
            
            # Колонки таблицы
            columns = ("date", "ticker", "operation", "quantity", "price", "total")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
            
            # Заголовки колонок
            headers = {
                "date": "Дата и время",
                "ticker": "Тикер",
                "operation": "Операция",
                "quantity": "Количество",
                "price": "Цена",
                "total": "Сумма"
            }
            
            for col in columns:
                tree.heading(col, text=headers[col])
                tree.column(col, width=120, minwidth=100)
            
            # Заполняем данными (последние 100 операций)
            for transaction in reversed(self.transaction_history[-100:]):
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
            
            # Кнопки управления
            button_frame = ttk.Frame(history_window)
            button_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(button_frame, text="Очистить историю", 
                      command=lambda: self.clear_transaction_history(history_window)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Закрыть", 
                      command=history_window.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю операций: {e}")
    
    def clear_transaction_history(self, parent_window):
        """
        Очистка всей истории транзакций.
        
        Args:
            parent_window: родительское окно для закрытия
        """
        if messagebox.askyesno("Подтверждение", "Очистить всю историю операций?"):
            try:
                self.transaction_history.clear()
                self.save_transaction_history()
                messagebox.showinfo("Успех", "История операций очищена")
                parent_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось очистить историю: {e}")
    
    def get_recent_transactions(self, limit=100):
        """
        Получение последних транзакций.
        
        Args:
            limit: количество последних транзакций
            
        Returns:
            list: список последних транзакций
        """
        return list(reversed(self.transaction_history[-limit:]))