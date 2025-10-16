# portfolio/portfolio_manager.py
import json
import os
import requests
from datetime import datetime
from tkinter import messagebox
import threading
from commission_manager import CommissionManager
from .transaction_manager import TransactionManager
from .dividend_manager import DividendManager

class PortfolioManager:
    def __init__(self, data_handler=None, parent=None):
        """
        Инициализация менеджера портфеля.
        
        Args:
            data_handler: обработчик данных для API
            parent: родительское окно для CommissionManager
        """
        self.data_handler = data_handler
        self.parent = parent
        self.commission_manager = CommissionManager(parent)
        self.transaction_manager = TransactionManager(self)
        self.dividend_manager = DividendManager(self)
        
        # Данные
        self.portfolio_data = []
        self.imoex_data = []
        
        # Загрузка данных при инициализации
        self.load_portfolio_data()
    
    def load_portfolio_data(self):
        """Загрузка данных портфеля из JSON файла"""
        try:
            if os.path.exists('portfolio_data.json'):
                with open('portfolio_data.json', 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Обеспечиваем обратную совместимость
                    for stock in loaded_data:
                        if 'total_cost' not in stock:
                            stock['total_cost'] = stock['quantity'] * stock['buy_price'] + stock.get('commission', 0)
                        if 'commission' not in stock:
                            stock['commission'] = 0
                    self.portfolio_data = loaded_data
        except Exception as e:
            print(f"Ошибка загрузки портфеля: {e}")
            self.portfolio_data = []
    
    def save_portfolio_data(self):
        """Сохранение данных портфеля в JSON файл"""
        try:
            with open('portfolio_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.portfolio_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения портфеля: {e}")
    
    def add_stock(self, ticker, quantity_str, buy_price_str):
        """
        Добавление акции в портфель.
        
        Args:
            ticker: тикер акции
            quantity_str: количество в виде строки
            buy_price_str: цена покупки в виде строки
        """
        ticker = ticker.strip().upper()
        
        if not ticker or not quantity_str or not buy_price_str:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        
        try:
            quantity = int(quantity_str)
            buy_price = float(buy_price_str)
            
            if quantity <= 0 or buy_price <= 0:
                messagebox.showerror("Ошибка", "Количество и цена должны быть положительными")
                return
            
            # Расчет комиссий
            commission = self.calculate_commission_costs(quantity, buy_price)
            total_cost = quantity * buy_price + commission
            
            # Проверяем, есть ли уже такая акция
            existing_stock = None
            for stock in self.portfolio_data:
                if stock['ticker'] == ticker:
                    existing_stock = stock
                    break
            
            if existing_stock:
                # Спрашиваем пользователя, что делать с существующей акцией
                choice = messagebox.askyesnocancel(
                    "Акция уже в портфеле", 
                    f"Акция {ticker} уже есть в портфеле.\n\n"
                    f"Текущее количество: {existing_stock['quantity']}\n"
                    f"Новое количество: {quantity}\n\n"
                    f"ДА - добавить к существующему количеству\n"
                    f"НЕТ - заменить количество\n"
                    f"ОТМЕНА - не добавлять"
                )
                
                if choice is None:  # Отмена
                    return
                elif choice:  # Да - добавить к существующему
                    total_quantity = existing_stock['quantity'] + quantity
                    total_investment = existing_stock['total_cost'] + total_cost
                    average_price = (total_investment - self.calculate_commission_costs(total_quantity, 0)) / total_quantity
                    
                    existing_stock['quantity'] = total_quantity
                    existing_stock['buy_price'] = average_price
                    existing_stock['commission'] = existing_stock.get('commission', 0) + commission
                    existing_stock['total_cost'] = total_investment
                else:  # Нет - заменить количество и цену
                    existing_stock['quantity'] = quantity
                    existing_stock['buy_price'] = buy_price
                    existing_stock['commission'] = commission
                    existing_stock['total_cost'] = total_cost
                
                # Регистрируем операцию покупки
                self.transaction_manager.record_transaction(ticker, 'buy', quantity, buy_price)
                
                # Обновляем данные акции
                self.update_stock_price(existing_stock)
                messagebox.showinfo("Успех", f"Акция {ticker} обновлена в портфеле")
                return
            
            # Добавляем новую акцию
            stock_data = {
                'ticker': ticker,
                'quantity': quantity,
                'buy_price': buy_price,
                'commission': commission,
                'total_cost': total_cost,
                'added_date': datetime.now().isoformat()
            }
            
            # Регистрируем операцию покупки
            self.transaction_manager.record_transaction(ticker, 'buy', quantity, buy_price)
            
            # Получаем текущую цену и название
            self.update_stock_price(stock_data)
            self.portfolio_data.append(stock_data)
            
            messagebox.showinfo("Успех", f"Акция {ticker} добавлена в портфель")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    def sell_stock(self, ticker, quantity_str, price_str):
        """
        Продажа акции из портфеля.
        
        Args:
            ticker: тикер акции
            quantity_str: количество для продажи в виде строки
            price_str: цена продажи в виде строки
        """
        ticker = ticker.strip().upper()
        
        if not ticker or not quantity_str or not price_str:
            messagebox.showerror("Ошибка", "Заполните все поля для продажи")
            return
        
        try:
            quantity_to_sell = int(quantity_str)
            sell_price = float(price_str)
            
            if quantity_to_sell <= 0 or sell_price <= 0:
                messagebox.showerror("Ошибка", "Количество и цена должны быть положительными")
                return
            
            # Ищем акцию в портфеле
            stock_to_sell = None
            for stock in self.portfolio_data:
                if stock['ticker'] == ticker:
                    stock_to_sell = stock
                    break
            
            if not stock_to_sell:
                messagebox.showerror("Ошибка", f"Акция {ticker} не найдена в портфеле")
                return
            
            current_quantity = stock_to_sell['quantity']
            
            if quantity_to_sell > current_quantity:
                messagebox.showerror("Ошибка", 
                                   f"Недостаточно акций для продажи. Доступно: {current_quantity}")
                return
            
            # Расчет комиссий при продаже
            sell_amount = quantity_to_sell * sell_price
            commission_calc = self.commission_manager.calculate_sell_commission(sell_amount)
            total_commission = commission_calc['total_commission']
            
            # Расчет налога
            buy_price_per_share = stock_to_sell['total_cost'] / stock_to_sell['quantity']
            tax = self.commission_manager.calculate_tax(
                buy_price_per_share * quantity_to_sell, 
                sell_amount, 
                quantity_to_sell
            )
            
            # Чистая выручка от продажи
            net_proceeds = sell_amount - total_commission - tax
            
            # Подтверждение продажи
            confirm_msg = (f"Подтвердите продажу {quantity_to_sell} акций {ticker} "
                          f"по цене {sell_price:.2f} руб?\n\n"
                          f"Выручка от продажи: {sell_amount:.2f} руб\n"
                          f"Комиссии: {total_commission:.2f} руб\n"
                          f"Налог: {tax:.2f} руб\n"
                          f"Чистая выручка: {net_proceeds:.2f} руб")
            
            if not messagebox.askyesno("Подтверждение продажи", confirm_msg):
                return
            
            # Регистрируем операцию продажи
            self.transaction_manager.record_transaction(ticker, 'sell', quantity_to_sell, sell_price)
            
            # Обновляем количество акций
            if quantity_to_sell == current_quantity:
                # Продали все акции - удаляем из портфеля
                self.portfolio_data.remove(stock_to_sell)
                messagebox.showinfo("Успех", f"Все акции {ticker} проданы и удалены из портфеля")
            else:
                # Продали часть акций - обновляем количество
                stock_to_sell['quantity'] = current_quantity - quantity_to_sell
                # Пересчитываем значения
                self.calculate_stock_values(stock_to_sell)
                messagebox.showinfo("Успех", 
                                  f"Продано {quantity_to_sell} акций {ticker}. "
                                  f"Осталось: {stock_to_sell['quantity']}")
            
            # Сохраняем изменения
            self.save_portfolio_data()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    def calculate_commission_costs(self, quantity, price):
        """
        Расчет комиссий при покупке.
        
        Args:
            quantity: количество акций
            price: цена акции
            
        Returns:
            float: сумма комиссий
        """
        total_amount = quantity * price
        commission_calc = self.commission_manager.calculate_buy_commission(total_amount)
        return commission_calc['total_commission']
    
    def update_stock_price(self, stock_data):
        """
        Обновление текущей цены акции с MOEX.
        
        Args:
            stock_data: данные акции
            
        Returns:
            bool: успешно ли обновлена цена
        """
        try:
            ticker = stock_data['ticker']
            
            # Используем data_handler если он доступен
            if self.data_handler:
                original_ticker = self.data_handler.ticker
                self.data_handler.set_ticker(ticker)
                data = self.data_handler.get_stock_data()
                self.data_handler.set_ticker(original_ticker)
                
                if data['success']:
                    stock_data['current_price'] = data['price']
                    stock_data['name'] = ticker
                    self.calculate_stock_values(stock_data)
                    return True
            else:
                # Альтернативный способ получения данных
                url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    market_data = data['marketdata']['data']
                    
                    if market_data:
                        stock_info = market_data[0]
                        current_price = stock_info[12]  # LAST цена
                        
                        if current_price is None:
                            current_price = stock_info[3]  # LCURRENTPRICE
                        
                        if current_price is not None:
                            stock_data['current_price'] = current_price
                            
                            # Получаем название акции
                            securities_data = data['securities']['data']
                            if securities_data:
                                stock_data['name'] = securities_data[0][2]  # SHORTNAME
                            
                            self.calculate_stock_values(stock_data)
                            return True
            
            # Если не удалось получить данные, используем цену покупки
            stock_data['current_price'] = stock_data['buy_price']
            stock_data['name'] = ticker
            self.calculate_stock_values(stock_data)
            return False
            
        except Exception as e:
            print(f"Ошибка получения цены для {stock_data['ticker']}: {e}")
            stock_data['current_price'] = stock_data['buy_price']
            stock_data['name'] = stock_data['ticker']
            self.calculate_stock_values(stock_data)
            return False
    
    def calculate_stock_values(self, stock_data):
        """
        Расчет стоимости и прибыли для акции.
        
        Args:
            stock_data: данные акции для расчета
        """
        try:
            quantity = stock_data['quantity']
            current_price = stock_data.get('current_price', stock_data['buy_price'])
            
            # Правильный расчет общей стоимости покупки (включая комиссии)
            if 'total_cost' not in stock_data:
                purchase_cost = quantity * stock_data['buy_price']
                commission = stock_data.get('commission', 0)
                stock_data['total_cost'] = purchase_cost + commission
            
            # Текущая стоимость
            stock_data['current_value'] = quantity * current_price
            
            # КАПИТАЛЬНАЯ ПРИБЫЛЬ = (Текущая стоимость - Стоимость покупки)
            capital_gain = stock_data['current_value'] - (quantity * stock_data['buy_price'])
            
            # ДИВИДЕНДНЫЙ ДОХОД (уже полученные деньги)
            dividend_income = stock_data.get('dividend_income', 0)
            
            # ОБЩАЯ ПРИБЫЛЬ = Капитальная прибыль + Дивидендный доход - Комиссии
            total_profit = capital_gain + dividend_income - stock_data.get('commission', 0)
            
            # Расчет в процентах
            if stock_data['total_cost'] > 0:
                capital_gain_percent = (capital_gain / stock_data['total_cost']) * 100
                dividend_yield = (dividend_income / stock_data['total_cost']) * 100
                total_profit_percent = (total_profit / stock_data['total_cost']) * 100
            else:
                capital_gain_percent = 0
                dividend_yield = 0
                total_profit_percent = 0
            
            # Сохраняем все показатели
            stock_data['capital_gain'] = capital_gain
            stock_data['dividend_income'] = dividend_income
            stock_data['total_profit'] = total_profit
            stock_data['capital_gain_percent'] = capital_gain_percent
            stock_data['dividend_yield'] = dividend_yield
            stock_data['total_profit_percent'] = total_profit_percent
            
        except KeyError as e:
            print(f"Ошибка расчета значений для акции {stock_data.get('ticker', 'unknown')}: {e}")
            stock_data['current_value'] = 0
            stock_data['capital_gain'] = 0
            stock_data['dividend_income'] = 0
            stock_data['total_profit'] = 0
            stock_data['capital_gain_percent'] = 0
            stock_data['dividend_yield'] = 0
            stock_data['total_profit_percent'] = 0
    
    def update_all_prices(self):
        """Обновление цен для всех акций в портфеле"""
        if not self.portfolio_data:
            messagebox.showinfo("Информация", "Портфель пуст")
            return
        
        updated_count = 0
        for stock in self.portfolio_data:
            if self.update_stock_price(stock):
                updated_count += 1
        
        if updated_count > 0:
            self.save_portfolio_data()
        
        messagebox.showinfo("Обновление", 
                          f"Цены обновлены для {updated_count} из {len(self.portfolio_data)} акций")
    
    def load_imoex_data(self):
        """Загрузка данных индекса Мосбиржи"""
        try:
            url = "https://iss.moex.com/iss/engines/stock/markets/index/boards/SNDX/securities/IMOEX.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                market_data = data['marketdata']['data']
                
                if market_data:
                    imoex_info = market_data[0]
                    current_value = imoex_info[12]  # LAST цена
                    
                    if current_value is not None:
                        self.imoex_data.append({
                            'time': datetime.now(),
                            'value': current_value
                        })
        except Exception as e:
            print(f"Ошибка загрузки данных IMOEX: {e}")
    
    def show_index_comparison(self, parent_window):
        """Показать сравнение портфеля с индексом Мосбиржи"""
        if not self.portfolio_data:
            messagebox.showwarning("Внимание", "Портфель пуст")
            return
        
        # Импортируем здесь чтобы избежать циклических импортов
        from .comparison_manager import ComparisonManager
        comparison_manager = ComparisonManager(self)
        comparison_manager.show_index_comparison(parent_window)
    
    def delete_selected(self, selected_items, tree):
        """Удаление выбранной акции из портфеля"""
        if not selected_items:
            messagebox.showwarning("Внимание", "Выберите акцию для удаления")
            return
        
        for item in selected_items:
            values = tree.item(item, "values")
            ticker = values[0]
            
            # Удаляем из данных
            self.portfolio_data = [s for s in self.portfolio_data if s['ticker'] != ticker]
        
        self.save_portfolio_data()
        messagebox.showinfo("Успех", "Акции удалены из портфеля")
    
    def clear_portfolio(self):
        """Очистка всего портфеля"""
        if not self.portfolio_data:
            return
        
        if messagebox.askyesno("Подтверждение", "Очистить весь портфель?"):
            self.portfolio_data.clear()
            self.save_portfolio_data()
    
    def export_to_csv(self):
        """Экспорт портфеля в CSV"""
        try:
            if not self.portfolio_data:
                messagebox.showwarning("Экспорт", "Портфель пуст")
                return
            
            filename = f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                
                # Заголовки
                headers = ["Тикер", "Название", "Количество", "Цена покупки", "Комиссия",
                          "Общая стоимость", "Текущая цена", "Текущая стоимость",
                          "Прибыль", "Прибыль %"]
                writer.writerow(headers)
                
                # Данные
                for stock in self.portfolio_data:
                    writer.writerow([
                        stock['ticker'],
                        stock.get('name', ''),
                        stock['quantity'],
                        f"{stock['buy_price']:.2f}",
                        f"{stock.get('commission', 0):.2f}",
                        f"{stock.get('total_cost', 0):.2f}",
                        f"{stock.get('current_price', 0):.2f}",
                        f"{stock.get('current_value', 0):.2f}",
                        f"{stock.get('profit', 0):.2f}",
                        f"{stock.get('profit_percent', 0):.2f}%"
                    ])
            
            messagebox.showinfo("Экспорт", f"Портфель экспортирован в файл:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать портфель: {e}")
    
    def get_portfolio_statistics(self):
        """
        Получение статистики портфеля.
        
        Returns:
            dict: словарь со статистикой
        """
        total_cost = sum(stock.get('total_cost', 0) for stock in self.portfolio_data)
        total_current_value = sum(stock.get('current_value', 0) for stock in self.portfolio_data)
        
        # ПРАВИЛЬНЫЙ расчет капитальной прибыли (только изменение цены)
        total_invested = sum(stock['quantity'] * stock['buy_price'] for stock in self.portfolio_data)
        total_capital_gain = total_current_value - total_invested
        
        total_dividends = sum(stock.get('dividend_income', 0) for stock in self.portfolio_data)
        total_commissions = sum(stock.get('commission', 0) for stock in self.portfolio_data)
        
        # ОБЩАЯ ПРИБЫЛЬ = Капитальная прибыль + Дивиденды - Комиссии
        total_profit = total_capital_gain + total_dividends - total_commissions
        
        if total_cost > 0:
            total_profit_percent = (total_profit / total_cost) * 100
            capital_gain_percent = (total_capital_gain / total_cost) * 100
            dividend_yield = (total_dividends / total_cost) * 100
            commission_percent = (total_commissions / total_cost) * 100
        else:
            total_profit_percent = 0
            capital_gain_percent = 0
            dividend_yield = 0
            commission_percent = 0
        
        return {
            'total_cost': total_cost,
            'total_current_value': total_current_value,
            'total_capital_gain': total_capital_gain,
            'total_dividends': total_dividends,
            'total_commissions': total_commissions,
            'total_profit': total_profit,
            'total_profit_percent': total_profit_percent,
            'capital_gain_percent': capital_gain_percent,
            'dividend_yield': dividend_yield,
            'commission_percent': commission_percent
        }