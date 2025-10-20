# portfolio/main_window.py
import tkinter as tk
from .portfolio_stock_manager import PortfolioManager
from .ui_components import UIComponents
from .chart_manager import ChartManager

class PortfolioWindow:
    def __init__(self, parent, data_handler=None):
        self.parent = parent
        self.data_handler = data_handler
        self.window = tk.Toplevel(parent)
        self.window.title("Мой портфель акций")
        self.window.geometry("1300x700")
        self.window.minsize(1000, 500)
        
        # Менеджеры
        self.portfolio_manager = PortfolioManager(data_handler, self.window)
        self.ui_components = UIComponents(self.window, self.portfolio_manager, self)
        self.chart_manager = ChartManager(self.portfolio_manager)
        # Создание интерфейса
        self.ui_components.create_widgets()
        
        # Обновление цен при открытии
        self.portfolio_manager.update_all_prices()
        self.portfolio_manager.load_imoex_data()
        
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    # Методы для вызова из UI
    def add_stock(self):
        """Добавление акции через менеджер и обновление UI"""
        self.portfolio_manager.add_stock(
            self.ui_components.ticker_var.get(),
            self.ui_components.quantity_var.get(),
            self.ui_components.buy_price_var.get()
        )
        self.ui_components.refresh_table()
        self.ui_components.update_statistics()
        self.ui_components.update_sell_ticker_combo()
    
    def sell_stock(self):
        """Продажа акции через менеджер и обновление UI"""
        self.portfolio_manager.sell_stock(
            self.ui_components.sell_ticker_var.get(),
            self.ui_components.sell_quantity_var.get(),
            self.ui_components.sell_price_var.get()
        )
        self.ui_components.refresh_table()
        self.ui_components.update_statistics()
        self.ui_components.update_sell_ticker_combo()
    
    def update_all_prices(self):
        """Обновление всех цен и обновление UI"""
        self.portfolio_manager.update_all_prices()
        self.ui_components.refresh_table()
        self.ui_components.update_statistics()
    
    def show_index_comparison(self):
        """Показать сравнение с индексом"""
        from .comparison_manager import ComparisonManager
        comparison_manager = ComparisonManager(self.portfolio_manager)
        comparison_manager.show_index_comparison(self.window)
    
    def show_transaction_history(self):
        """Показать историю транзакций"""
        self.portfolio_manager.transaction_manager.show_transaction_history(self.window)
    
    def add_dividend_payment(self):
        """Добавить дивидендную выплату"""
        self.portfolio_manager.dividend_manager.add_dividend_payment(self.window)
        self.ui_components.refresh_table()
        self.ui_components.update_statistics()
    
    def show_dividend_history(self):
        """Показать историю дивидендов"""
        self.portfolio_manager.dividend_manager.show_dividend_history(self.window)
    
    def delete_selected(self):
        """Удалить выбранные акции"""
        selected_items = self.ui_components.tree.selection()
        self.portfolio_manager.delete_selected(selected_items, self.ui_components.tree)
        self.ui_components.refresh_table()
        self.ui_components.update_statistics()
        self.ui_components.update_sell_ticker_combo()
    
    def clear_portfolio(self):
        """Очистить весь портфель"""
        self.portfolio_manager.clear_portfolio()
        self.ui_components.refresh_table()
        self.ui_components.update_statistics()
        self.ui_components.update_sell_ticker_combo()
    
    def export_to_csv(self):
        """Экспорт портфеля в CSV"""
        self.portfolio_manager.export_to_csv()
    
    def focus(self):
        """Активировать окно"""
        self.window.focus_force()
    def show_portfolio_charts(self):
        """Показать графики распределения портфеля"""
        self.chart_manager.show_portfolio_allocation(self.window)
    
    def close(self):
        """Закрытие окна с сохранением данных"""
        self.portfolio_manager.save_portfolio_data()
        self.window.destroy()