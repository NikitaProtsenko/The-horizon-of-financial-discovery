# Менеджер дивидендов - управление дивидендными выплатами
import json
import os
from datetime import datetime
from tkinter import messagebox, ttk
import tkinter as tk

class DividendManager:
    """
    Управление дивидендными выплатами: добавление, история, расчеты.
    """
    
    def __init__(self, portfolio_manager):
        """
        Инициализация менеджера дивидендов.
        
        Args:
            portfolio_manager: ссылка на менеджер портфеля
        """
        self.portfolio_manager = portfolio_manager
        self.dividend_history = []
        self.load_dividend_history()
    
    def load_dividend_history(self):
        """Загрузка истории дивидендов из JSON файла"""
        try:
            if os.path.exists('dividends_history.json'):
                with open('dividends_history.json', 'r', encoding='utf-8') as f:
                    self.dividend_history = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки истории дивидендов: {e}")
            self.dividend_history = []
    
    def save_dividend_history(self):
        """Сохранение истории дивидендов в JSON файл"""
        try:
            with open('dividends_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.dividend_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории дивидендов: {e}")
    
    def add_dividend_payment(self, parent_window):
        """
        Отображение диалога добавления дивидендной выплаты.
        
        Args:
            parent_window: родительское окно
        """
        dividend_window = tk.Toplevel(parent_window)
        dividend_window.title("Добавление дивидендной выплаты")
        dividend_window.geometry("450x350")
        dividend_window.transient(parent_window)
        dividend_window.grab_set()

        main_frame = ttk.Frame(dividend_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Добавление дивидендной выплаты", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 15))

        # Выбор тикера
        ticker_frame = ttk.Frame(main_frame)
        ticker_frame.pack(fill=tk.X, pady=5)
        ttk.Label(ticker_frame, text="Тикер:").pack(side=tk.LEFT)
        dividend_ticker_var = tk.StringVar()
        dividend_ticker_combo = ttk.Combobox(ticker_frame, textvariable=dividend_ticker_var, 
                                            width=10, state="readonly")
        dividend_ticker_combo.pack(side=tk.LEFT, padx=5)
        
        # Заполняем список тикеров из портфеля
        tickers = [stock['ticker'] for stock in self.portfolio_manager.portfolio_data]
        dividend_ticker_combo['values'] = tickers
        if tickers:
            dividend_ticker_combo.set(tickers[0])

        # Количество акций для дивидендов
        quantity_frame = ttk.Frame(main_frame)
        quantity_frame.pack(fill=tk.X, pady=5)
        ttk.Label(quantity_frame, text="Количество акций:").pack(side=tk.LEFT)
        dividend_quantity_var = tk.StringVar()
        dividend_quantity_entry = ttk.Entry(quantity_frame, textvariable=dividend_quantity_var, width=12)
        dividend_quantity_entry.pack(side=tk.LEFT, padx=5)
        
        # Кнопка для использования всех акций
        def use_all_shares():
            ticker = dividend_ticker_var.get()
            if ticker:
                stock = next((s for s in self.portfolio_manager.portfolio_data if s['ticker'] == ticker), None)
                if stock:
                    dividend_quantity_var.set(str(stock['quantity']))
        
        ttk.Button(quantity_frame, text="Все акции", 
                  command=use_all_shares, width=8).pack(side=tk.LEFT, padx=5)

        # Информация о доступных акциях
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=2)
        available_shares_label = ttk.Label(info_frame, text="В портфеле: 0 акций", 
                                               font=("Arial", 8), foreground="gray")
        available_shares_label.pack()

        # Дата выплаты
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_frame, text="Дата выплаты:").pack(side=tk.LEFT)
        dividend_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        dividend_date_entry = ttk.Entry(date_frame, textvariable=dividend_date_var, width=12)
        dividend_date_entry.pack(side=tk.LEFT, padx=5)

        # Сумма дивиденда на акцию
        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(fill=tk.X, pady=5)
        ttk.Label(amount_frame, text="Дивиденд на акцию (руб):").pack(side=tk.LEFT)
        dividend_amount_var = tk.StringVar()
        dividend_amount_entry = ttk.Entry(amount_frame, textvariable=dividend_amount_var, width=12)
        dividend_amount_entry.pack(side=tk.LEFT, padx=5)

        # Налог на дивиденды
        tax_frame = ttk.Frame(main_frame)
        tax_frame.pack(fill=tk.X, pady=5)
        ttk.Label(tax_frame, text="Налог на дивиденды (%):").pack(side=tk.LEFT)
        dividend_tax_var = tk.StringVar(value="13")
        dividend_tax_entry = ttk.Entry(tax_frame, textvariable=dividend_tax_var, width=12)
        dividend_tax_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(tax_frame, text="%").pack(side=tk.LEFT)

        # Расчет итогов
        calc_frame = ttk.LabelFrame(main_frame, text="Расчет выплаты", padding="10")
        calc_frame.pack(fill=tk.X, pady=10)
        
        total_dividends_label = ttk.Label(calc_frame, text="Всего дивидендов: 0.00 руб")
        total_dividends_label.pack(anchor=tk.W)
        
        tax_amount_label = ttk.Label(calc_frame, text="Сумма налога: 0.00 руб")
        tax_amount_label.pack(anchor=tk.W)
        
        after_tax_label = ttk.Label(calc_frame, text="Чистая выплата: 0.00 руб", 
                                   font=("Arial", 10, "bold"))
        after_tax_label.pack(anchor=tk.W)

        def update_available_shares():
            """Обновление информации о доступных акциях"""
            ticker = dividend_ticker_var.get()
            if ticker:
                stock = next((s for s in self.portfolio_manager.portfolio_data if s['ticker'] == ticker), None)
                if stock:
                    available_shares_label.config(
                        text=f"В портфеле: {stock['quantity']} акций (доступно для дивидендов)"
                    )
                else:
                    available_shares_label.config(text="Акция не найдена в портфеле")
            else:
                available_shares_label.config(text="Выберите тикер")

        def calculate_dividends():
            """Расчет дивидендов"""
            try:
                ticker = dividend_ticker_var.get()
                quantity = int(dividend_quantity_var.get() or 0)
                amount_per_share = float(dividend_amount_var.get() or 0)
                tax_rate = float(dividend_tax_var.get() or 0)
                
                # Проверяем, что количество не превышает доступное
                if ticker:
                    stock = next((s for s in self.portfolio_manager.portfolio_data if s['ticker'] == ticker), None)
                    if stock and quantity > stock['quantity']:
                        total_dividends_label.config(
                            text=f"Ошибка: запрошено {quantity} акций, доступно {stock['quantity']}",
                            foreground="red"
                        )
                        return
                
                if quantity > 0 and amount_per_share > 0:
                    total_dividends = quantity * amount_per_share
                    tax_amount = total_dividends * (tax_rate / 100)
                    net_dividends = total_dividends - tax_amount
                    
                    total_dividends_label.config(
                        text=f"Всего дивидендов: {total_dividends:.2f} руб", 
                        foreground="black"
                    )
                    tax_amount_label.config(text=f"Сумма налога: {tax_amount:.2f} руб")
                    after_tax_label.config(text=f"Чистая выплата: {net_dividends:.2f} руб")
                else:
                    total_dividends_label.config(text="Всего дивидендов: 0.00 руб")
                    tax_amount_label.config(text="Сумма налога: 0.00 руб")
                    after_tax_label.config(text="Чистая выплата: 0.00 руб")
                    
            except ValueError:
                total_dividends_label.config(text="Всего дивидендов: 0.00 руб")
                tax_amount_label.config(text="Сумма налога: 0.00 руб")
                after_tax_label.config(text="Чистая выплата: 0.00 руб")

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        def save_dividend():
            """Сохранение дивидендной выплаты"""
            try:
                ticker = dividend_ticker_var.get()
                quantity = int(dividend_quantity_var.get() or 0)
                amount_per_share = float(dividend_amount_var.get() or 0)
                tax_rate = float(dividend_tax_var.get() or 13)
                payment_date = dividend_date_var.get()

                if not ticker or quantity <= 0 or amount_per_share <= 0:
                    messagebox.showerror("Ошибка", "Заполните все поля корректно")
                    return

                # Проверяем доступное количество акций
                stock = next((s for s in self.portfolio_manager.portfolio_data if s['ticker'] == ticker), None)
                if not stock:
                    messagebox.showerror("Ошибка", f"Акция {ticker} не найдена в портфеле")
                    return

                if quantity > stock['quantity']:
                    messagebox.showerror("Ошибка", 
                                       f"Недостаточно акций. Запрошено: {quantity}, доступно: {stock['quantity']}")
                    return

                # Расчет выплаты
                total_dividends = quantity * amount_per_share
                tax_amount = total_dividends * (tax_rate / 100)
                net_dividends = total_dividends - tax_amount

                # Создаем запись о дивидендах
                dividend_data = {
                    'ticker': ticker,
                    'date': payment_date,
                    'quantity': quantity,
                    'amount_per_share': amount_per_share,
                    'total_amount': total_dividends,
                    'tax_rate': tax_rate,
                    'tax_amount': tax_amount,
                    'net_amount': net_dividends,
                    'total_shares_in_portfolio': stock['quantity']
                }

                # Сохраняем в историю дивидендов
                self.save_dividend_payment(dividend_data)

                # Обновляем статистику портфеля
                self.update_portfolio_with_dividend(ticker, net_dividends, quantity)

                messagebox.showinfo("Успех", 
                                  f"Дивиденды по {ticker} добавлены:\n"
                                  f"Акции: {quantity} шт.\n"
                                  f"Чистая выплата: {net_dividends:.2f} руб")
                dividend_window.destroy()

            except ValueError as e:
                messagebox.showerror("Ошибка", f"Некорректные данные: {e}")

        ttk.Button(button_frame, text="Рассчитать", 
                  command=calculate_dividends).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить", 
                  command=save_dividend).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=dividend_window.destroy).pack(side=tk.RIGHT, padx=5)

        # Авторасчет при изменении значений
        dividend_ticker_var.trace('w', lambda *args: [update_available_shares(), calculate_dividends()])
        dividend_quantity_var.trace('w', lambda *args: calculate_dividends())
        dividend_amount_var.trace('w', lambda *args: calculate_dividends())
        dividend_tax_var.trace('w', lambda *args: calculate_dividends())

        # Инициализация
        update_available_shares()
        calculate_dividends()

    def save_dividend_payment(self, dividend_data):
        """
        Сохранение дивидендной выплаты в историю.
        
        Args:
            dividend_data: данные о дивидендной выплате
        """
        try:
            self.dividend_history.append(dividend_data)
            self.save_dividend_history()
                
        except Exception as e:
            print(f"Ошибка сохранения дивидендов: {e}")

    def update_portfolio_with_dividend(self, ticker, dividend_amount, dividend_quantity):
        """
        Обновление портфеля с учетом полученных дивидендов.
        
        Args:
            ticker: тикер акции
            dividend_amount: сумма дивидендов
            dividend_quantity: количество акций с дивидендами
        """
        # Добавляем поле для учета дивидендов в данные акции
        for stock in self.portfolio_manager.portfolio_data:
            if stock['ticker'] == ticker:
                if 'dividend_income' not in stock:
                    stock['dividend_income'] = 0
                if 'dividend_transactions' not in stock:
                    stock['dividend_transactions'] = []
                
                # Добавляем общую сумму дивидендов
                stock['dividend_income'] += dividend_amount
                
                # Сохраняем информацию о транзакции
                dividend_transaction = {
                    'date': datetime.now().isoformat(),
                    'quantity': dividend_quantity,
                    'amount': dividend_amount,
                    'type': 'dividend'
                }
                stock['dividend_transactions'].append(dividend_transaction)
                
                # Пересчитываем общую доходность
                self.portfolio_manager.calculate_stock_values(stock)
                break
        
        self.portfolio_manager.save_portfolio_data()

    def show_dividend_history(self, parent_window):
        """Показать историю дивидендов"""
        try:
            if not self.dividend_history:
                from tkinter import messagebox
                messagebox.showinfo("История дивидендов", "История дивидендных выплат пуста")
                return
            
            history_window = tk.Toplevel(parent_window)  # Используем переданный parent_window
            history_window.title("История дивидендных выплат")
            history_window.geometry("1000x500")
            
            main_frame = ttk.Frame(history_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="История дивидендных выплат", 
                     font=("Arial", 14, "bold")).pack(pady=(0, 10))
            
            # Таблица истории
            table_frame = ttk.Frame(main_frame)
            table_frame.pack(fill=tk.BOTH, expand=True)
            
            columns = ("date", "ticker", "quantity", "total_shares", "amount_per_share", 
                      "total_amount", "tax_amount", "net_amount")
            
            tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
            
            headers = {
                "date": "Дата выплаты",
                "ticker": "Тикер",
                "quantity": "Акций с дивидендами",
                "total_shares": "Всего в портфеле",
                "amount_per_share": "Дивиденд на акцию",
                "total_amount": "Общая сумма",
                "tax_amount": "Налог",
                "net_amount": "Чистая сумма"
            }
            
            for col in columns:
                tree.heading(col, text=headers[col])
                if col in ["quantity", "total_shares"]:
                    tree.column(col, width=120, minwidth=100, anchor=tk.CENTER)
                else:
                    tree.column(col, width=110, minwidth=90)
            
            # Заполняем данными
            total_dividends = 0
            total_tax = 0
            total_net = 0
            total_shares_with_dividends = 0
            
            for dividend in reversed(self.dividend_history):
                quantity = dividend['quantity']
                total_shares = dividend.get('total_shares_in_portfolio', quantity)
                percentage = (quantity / total_shares * 100) if total_shares > 0 else 100
                
                tree.insert("", tk.END, values=(
                    dividend['date'],
                    dividend['ticker'],
                    f"{quantity} шт. ({percentage:.1f}%)",
                    f"{total_shares} шт.",
                    f"{dividend['amount_per_share']:.2f} руб",
                    f"{dividend['total_amount']:.2f} руб",
                    f"{dividend['tax_amount']:.2f} руб",
                    f"{dividend['net_amount']:.2f} руб"
                ))
                
                total_dividends += dividend['total_amount']
                total_tax += dividend['tax_amount']
                total_net += dividend['net_amount']
                total_shares_with_dividends += quantity
            
            # Прокрутка
            v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
            h_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
            
            tree.grid(row=0, column=0, sticky="nsew")
            v_scroll.grid(row=0, column=1, sticky="ns")
            h_scroll.grid(row=1, column=0, sticky="ew")
            
            table_frame.columnconfigure(0, weight=1)
            table_frame.rowconfigure(0, weight=1)
            
            # Итоговая статистика
            stats_frame = ttk.Frame(main_frame)
            stats_frame.pack(fill=tk.X, pady=10)
            
            stats_text = (f"Всего выплат: {len(self.dividend_history)} | "
                         f"Акций с дивидендами: {total_shares_with_dividends} шт. | "
                         f"Общая сумма: {total_dividends:.2f} руб | "
                         f"Налоги: {total_tax:.2f} руб | "
                         f"Чистый доход: {total_net:.2f} руб")
            
            ttk.Label(stats_frame, text=stats_text, font=("Arial", 10, "bold")).pack()
            
            # Кнопки
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            ttk.Button(button_frame, text="Экспорт в CSV", 
                      command=lambda: self.export_dividends_to_csv(self.dividend_history)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Закрыть", 
                      command=history_window.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю дивидендов: {e}")

    def export_dividends_to_csv(self, dividends_data):
        """
        Экспорт истории дивидендов в CSV.
        
        Args:
            dividends_data: данные дивидендов для экспорта
        """
        try:
            if not dividends_data:
                messagebox.showwarning("Экспорт", "Нет данных для экспорта")
                return
            
            filename = f"dividends_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                
                headers = ["Дата выплаты", "Тикер", "Количество акций", "Дивиденд на акцию",
                          "Общая сумма", "Налоговая ставка", "Сумма налога", "Чистая сумма"]
                writer.writerow(headers)
                
                for dividend in dividends_data:
                    writer.writerow([
                        dividend['date'],
                        dividend['ticker'],
                        dividend['quantity'],
                        f"{dividend['amount_per_share']:.2f}",
                        f"{dividend['total_amount']:.2f}",
                        f"{dividend['tax_rate']:.2f}%",
                        f"{dividend['tax_amount']:.2f}",
                        f"{dividend['net_amount']:.2f}"
                    ])
            
            messagebox.showinfo("Экспорт", f"История дивидендов экспортирована в файл:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать историю дивидендов: {e}")