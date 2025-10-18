# data_handler.py
import requests
from datetime import datetime, time, timedelta
import pytz
import random

class DataHandler:
    """
    Класс для обработки данных об акциях.
    Получает реальные данные с Московской биржи.
    """
    
    def __init__(self, ticker="SBER"):
        self.ticker = ticker.upper()
        # URL для получения данных об акциях
        self.stock_url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{self.ticker}.json"
        self.moscow_tz = pytz.timezone('Europe/Moscow')
        
        # Переменные для хранения предыдущих данных
        self.previous_price = None
        self.previous_time = None
        
        # Кэш для исторических данных
        self.historical_data = []
        
    def set_ticker(self, ticker):
        """Изменение тикера акции"""
        self.ticker = ticker.upper()
        self.stock_url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{self.ticker}.json"
        # Сбрасываем предыдущие данные при смене тикера
        self.previous_price = None
        self.previous_time = None
        self.historical_data = []
        
    def get_moscow_time(self):
        """Получение текущего московского времени"""
        return datetime.now(self.moscow_tz)
    
    def check_market_hours(self, current_time=None):
        """Проверка, открыты ли сейчас торги на Московской бирже"""
        if current_time is None:
            current_time = self.get_moscow_time()
        
        # Торги на Московской бирже: пн-пт с 7:00 до 19:00
        market_open = time(7, 0)
        market_close = time(19, 0)
        
        current_time_only = current_time.time()
        current_weekday = current_time.weekday()
        is_weekday = current_weekday < 5  # Пн-Пт (0-4)
        
        return (is_weekday and market_open <= current_time_only <= market_close)
    
    def get_real_time_data(self):
        """Получение реальных данных с MOEX в реальном времени"""
        try:
            response = requests.get(self.stock_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Получаем рыночные данные
                market_data = data['marketdata']['data']
                if market_data and market_data[0]:
                    stock_info = market_data[0]
                    
                    # Получаем базовую информацию
                    securities_data = data['securities']['data']
                    security_info = securities_data[0] if securities_data else []
                    
                    # Извлекаем реальные данные (правильные индексы для MOEX API)
                    current_price = stock_info[12] if len(stock_info) > 12 else None  # LAST
                    
                    # Если нет последней цены, используем текущую оценку
                    if current_price is None:
                        current_price = stock_info[3] if len(stock_info) > 3 else None  # LCURRENTPRICE
                    
                    # Получаем другие показатели
                    open_price = stock_info[9] if len(stock_info) > 9 else None  # OPEN
                    high_price = stock_info[10] if len(stock_info) > 10 else None  # HIGH
                    low_price = stock_info[11] if len(stock_info) > 11 else None  # LOW
                    volume = stock_info[27] if len(stock_info) > 27 else 0  # VOLUME
                    
                    # Время обновления
                    update_time = stock_info[34] if len(stock_info) > 34 else None  # SYSTEMTIME
                    
                    if update_time:
                        try:
                            trade_time = datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S')
                            trade_time = self.moscow_tz.localize(trade_time)
                        except:
                            trade_time = self.get_moscow_time()
                    else:
                        trade_time = self.get_moscow_time()
                    
                    # Если текущей цены нет, но есть цена открытия, используем ее
                    if current_price is None and open_price is not None:
                        current_price = open_price
                    
                    # Если все еще нет данных, возвращаем ошибку
                    if current_price is None:
                        return self.get_fallback_data()
                    
                    # Рассчитываем изменения
                    change_absolute = 0
                    change_percent = 0
                    
                    if open_price is not None and open_price != 0:
                        change_absolute = current_price - open_price
                        change_percent = (change_absolute / open_price) * 100
                    
                    # Сохраняем для истории
                    if self.previous_price is not None:
                        self.historical_data.append({
                            'time': trade_time,
                            'price': current_price,
                            'volume': volume
                        })
                    
                    self.previous_price = current_price
                    self.previous_time = trade_time
                    
                    return {
                        'success': True,
                        'ticker': self.ticker,
                        'price': current_price,
                        'time': trade_time,
                        'volume': volume,
                        'change_absolute': change_absolute,
                        'change_percent': change_percent,
                        'high': high_price if high_price else current_price,
                        'low': low_price if low_price else current_price,
                        'open': open_price if open_price else current_price,
                        'is_historical': False,
                        'is_fallback': False,
                        'data_source': 'MOEX Real-time'
                    }
            
            return self.get_fallback_data()
            
        except Exception as e:
            print(f"Ошибка получения реальных данных для {self.ticker}: {e}")
            return self.get_fallback_data()
    
    def get_historical_data(self, days=30):
        """Получение исторических данных за указанное количество дней"""
        try:
            # URL для исторических данных
            hist_url = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{self.ticker}.json?from={(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')}"
            
            response = requests.get(hist_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                historical_points = data['history']['data']
                
                historical_data = []
                for point in historical_points:
                    try:
                        date_str = point[1]  # TRADEDATE
                        close_price = point[11]  # CLOSE
                        
                        if date_str and close_price:
                            trade_date = datetime.strptime(date_str, '%Y-%m-%d')
                            trade_date = self.moscow_tz.localize(trade_date)
                            historical_data.append((trade_date, close_price))
                    except:
                        continue
                
                return historical_data
            
            return []
            
        except Exception as e:
            print(f"Ошибка получения исторических данных для {self.ticker}: {e}")
            return []
    
    def get_stock_data(self):
        """Основной метод получения данных - использует реальные данные"""
        return self.get_real_time_data()
    
    def get_fallback_data(self):
        """Резервные данные только в случае полной недоступности MOEX"""
        current_time = self.get_moscow_time()
        
        # Используем предыдущую цену если есть, иначе базовую
        if self.previous_price is None:
            base_price = 280.0
        else:
            base_price = self.previous_price
        
        return {
            'success': False,
            'ticker': self.ticker,
            'price': base_price,
            'time': current_time,
            'volume': 0,
            'change_absolute': 0,
            'change_percent': 0,
            'high': base_price,
            'low': base_price,
            'open': base_price,
            'is_historical': False,
            'is_fallback': True,
            'data_source': 'Fallback'
        }