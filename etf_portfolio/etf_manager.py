# etf_portfolio/etf_manager.py
import json
import os
from datetime import datetime
import requests
from commission_manager import CommissionManager


class ETFPortfolioManager:
    """
    Менеджер для работы с данными портфеля ETF
    """
    
    def __init__(self):
        self.portfolio_data = []
        self.commission_manager = CommissionManager(None)
        self.load_portfolio_data()
    
    def load_portfolio_data(self):
        """Загрузка данных портфеля ETF из файла"""
        try:
            if os.path.exists('etf_portfolio.json'):
                with open('etf_portfolio.json', 'r', encoding='utf-8') as f:
                    self.portfolio_data = json.load(f)
                    
                # Убедимся, что все ETF имеют правильные расчеты
                for etf in self.portfolio_data:
                    self.calculate_etf_values(etf)
        except Exception as e:
            print(f"Ошибка загрузки портфеля ETF: {e}")
            self.portfolio_data = []
    
    def save_portfolio_data(self):
        """Сохранение данных портфеля ETF в файл"""
        try:
            with open('etf_portfolio.json', 'w', encoding='utf-8') as f:
                json.dump(self.portfolio_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения портфеля ETF: {e}")
    
    def get_tickers(self):
        """Получение списка тикеров"""
        return [etf['ticker'] for etf in self.portfolio_data]
    
    def add_etf(self, ticker, quantity, buy_price, dividend_yield):
        """Добавление ETF в портфель"""
        try:
            # Расчет комиссий
            commission = self.calculate_commission_costs(quantity, buy_price)
            total_cost = quantity * buy_price + commission
            
            # Проверяем, есть ли уже такой ETF
            existing_etf = None
            for etf in self.portfolio_data:
                if etf['ticker'] == ticker:
                    existing_etf = etf
                    break
            
            if existing_etf:
                # Обновляем существующий ETF
                total_quantity = existing_etf['quantity'] + quantity
                total_investment = existing_etf['total_cost'] + total_cost
                average_price = (total_investment - self.calculate_commission_costs(total_quantity, 0)) / total_quantity
                
                # Обновляем среднюю дивидендную доходность
                current_dividend = existing_etf.get('dividend_yield', 0)
                weighted_dividend = ((existing_etf['quantity'] * current_dividend) + 
                                   (quantity * dividend_yield)) / total_quantity
                
                existing_etf['quantity'] = total_quantity
                existing_etf['buy_price'] = average_price
                existing_etf['commission'] = existing_etf.get('commission', 0) + commission
                existing_etf['total_cost'] = total_investment
                existing_etf['dividend_yield'] = weighted_dividend
                
                # Обновляем данные ETF
                self.update_etf_price(existing_etf)
                return True, f"ETF {ticker} обновлен в портфеле"
            
            else:
                # Добавляем новый ETF
                etf_data = {
                    'ticker': ticker,
                    'quantity': quantity,
                    'buy_price': buy_price,
                    'commission': commission,
                    'total_cost': total_cost,
                    'dividend_yield': dividend_yield,
                    'added_date': datetime.now().isoformat()
                }
                
                # Получаем текущую цену и название
                self.update_etf_price(etf_data)
                self.portfolio_data.append(etf_data)
                return True, f"ETF {ticker} добавлен в портфель"
                
        except Exception as e:
            return False, f"Ошибка при добавлении ETF: {e}"
    
    def sell_etf(self, ticker, quantity, price):
        """Продажа ETF из портфеля"""
        try:
            # Ищем ETF в портфеле
            etf_to_sell = None
            for etf in self.portfolio_data:
                if etf['ticker'] == ticker:
                    etf_to_sell = etf
                    break
            
            if not etf_to_sell:
                return False, f"ETF {ticker} не найден в портфеле"
            
            current_quantity = etf_to_sell['quantity']
            
            if quantity > current_quantity:
                return False, f"Недостаточно ETF для продажи. Доступно: {current_quantity}"
            
            # Обновляем количество ETF
            if quantity == current_quantity:
                # Продали все ETF - удаляем из портфеля
                self.portfolio_data.remove(etf_to_sell)
                return True, f"Все ETF {ticker} проданы и удалены из портфеля"
            else:
                # Продали часть ETF - обновляем количество
                etf_to_sell['quantity'] = current_quantity - quantity
                # Пересчитываем значения
                self.calculate_etf_values(etf_to_sell)
                return True, f"Продано {quantity} ETF {ticker}. Осталось: {etf_to_sell['quantity']}"
                
        except Exception as e:
            return False, f"Ошибка при продаже ETF: {e}"
    
    def update_etf_price(self, etf_data):
        """Обновление текущей цены ETF с MOEX"""
        try:
            ticker = etf_data['ticker']
            
            # Альтернативный способ получения данных
            url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQTF/securities/{ticker}.json"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                market_data = data['marketdata']['data']
                
                if market_data:
                    etf_info = market_data[0]
                    current_price = etf_info[12]  # LAST цена
                    
                    if current_price is None:
                        current_price = etf_info[3]  # LCURRENTPRICE
                    
                    if current_price is not None:
                        etf_data['current_price'] = current_price
                        
                        # Получаем название ETF
                        securities_data = data['securities']['data']
                        if securities_data:
                            etf_data['name'] = securities_data[0][2]  # SHORTNAME
                        
                        # Пересчитываем значения
                        self.calculate_etf_values(etf_data)
                        return True
            
            # Если не удалось получить данные, используем цену покупки
            etf_data['current_price'] = etf_data['buy_price']
            etf_data['name'] = ticker
            self.calculate_etf_values(etf_data)
            return False
            
        except Exception as e:
            print(f"Ошибка получения цены для {etf_data['ticker']}: {e}")
            etf_data['current_price'] = etf_data['buy_price']
            etf_data['name'] = etf_data['ticker']
            self.calculate_etf_values(etf_data)
            return False
    
    def update_all_prices(self):
        """Обновление цен всех ETF в портфеле с подсчетом результатов"""
        updated_count = 0
        total_count = len(self.portfolio_data)
        for etf in self.portfolio_data:
            if self.update_etf_price(etf):
                updated_count += 1
        
        return updated_count, total_count
    
    def delete_etf(self, ticker):
        """Удаление ETF из портфеля"""
        self.portfolio_data = [etf for etf in self.portfolio_data if etf['ticker'] != ticker]
        self.save_portfolio_data()
    
    def clear_portfolio(self):
        """Очистка портфеля"""
        self.portfolio_data = []
        self.save_portfolio_data()
    
    def calculate_commission_costs(self, quantity, price):
        """Расчет комиссий при покупке"""
        total_amount = quantity * price
        commission_calc = self.commission_manager.calculate_buy_commission(total_amount)
        return commission_calc['total_commission']
    
    def calculate_etf_values(self, etf_data):
        """Расчет стоимости, прибыли и дивидендного дохода для ETF"""
        try:
            quantity = etf_data['quantity']
            current_price = etf_data.get('current_price', etf_data['buy_price'])
            dividend_yield = etf_data.get('dividend_yield', 0)
            
            # Инициализируем необходимые поля если их нет
            if 'total_cost' not in etf_data:
                etf_data['total_cost'] = quantity * etf_data['buy_price'] + etf_data.get('commission', 0)
            
            etf_data['current_value'] = quantity * current_price
            etf_data['profit'] = etf_data['current_value'] - etf_data['total_cost']
            
            if etf_data['total_cost'] > 0:
                etf_data['profit_percent'] = (etf_data['profit'] / etf_data['total_cost']) * 100
            else:
                etf_data['profit_percent'] = 0
            
            # Расчет годового дивидендного дохода
            etf_data['annual_dividend'] = etf_data['current_value'] * (dividend_yield / 100)
            
        except KeyError as e:
            print(f"Ошибка расчета значений для ETF {etf_data.get('ticker', 'unknown')}: {e}")
            # Устанавливаем значения по умолчанию
            etf_data['current_value'] = 0
            etf_data['profit'] = 0
            etf_data['profit_percent'] = 0
            etf_data['annual_dividend'] = 0
    
    def export_to_csv(self):
        """Экспорт портфеля ETF в CSV файл"""
        try:
            if not self.portfolio_data:
                return False, "Портфель ETF пуст"
            
            filename = f"etf_portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', encoding='utf-8') as f:
                # Заголовок
                f.write("Тикер;Название;Количество;Цена покупки;Комиссия;Общая стоимость;"
                       "Текущая цена;Текущая стоимость;Див. yield (%);Годовой дивиденд;"
                       "Прибыль;Прибыль %\n")
                
                # Данные
                for etf in self.portfolio_data:
                    f.write(f"{etf['ticker']};"
                           f"{etf.get('name', '')};"
                           f"{etf['quantity']};"
                           f"{etf['buy_price']:.2f};"
                           f"{etf.get('commission', 0):.2f};"
                           f"{etf.get('total_cost', 0):.2f};"
                           f"{etf.get('current_price', 0):.2f};"
                           f"{etf.get('current_value', 0):.2f};"
                           f"{etf.get('dividend_yield', 0):.2f};"
                           f"{etf.get('annual_dividend', 0):.2f};"
                           f"{etf.get('profit', 0):.2f};"
                           f"{etf.get('profit_percent', 0):.2f}\n")
            
            return True, f"Портфель ETF экспортирован в файл:\n{filename}"
            
        except Exception as e:
            return False, f"Не удалось экспортировать данные: {e}"
    
    def show_commission_settings(self, parent):
        """Показать настройки комиссий"""
        self.commission_manager.show_commission_settings()