# etf_portfolio/etf_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from .etf_manager import ETFPortfolioManager
from .etf_ui import ETFUIComponents
from .etf_transactions import ETFTransactionManager


class ETFPortfolioWindow:
    """
    Главное окно для управления портфелем ETF
    """
    
    def __init__(self, parent, data_handler=None):
        self.parent = parent
        self.data_handler = data_handler
        self.window = tk.Toplevel(parent)
        self.window.title("Мой портфель ETF")
        self.window.geometry("1200x700")
        self.window.minsize(900, 400)
        
        # Инициализация менеджеров
        self.portfolio_manager = ETFPortfolioManager()
        self.transaction_manager = ETFTransactionManager()
        self.ui_components = ETFUIComponents(self.window, self)
        
        # Создание интерфейса
        self.ui_components.create_main_interface()
        
        # Обновление цен при открытии
        self.update_all_prices()
        
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    def add_etf(self):
        """Добавление нового ETF в портфель"""
        input_data = self.ui_components.get_input_values()
        
        if not input_data['ticker'] or not input_data['quantity'] or not input_data['buy_price']:
            messagebox.showerror("Ошибка", "Заполните все обязательные поля")
            return
        
        try:
            quantity = int(input_data['quantity'])
            buy_price = float(input_data['buy_price'])
            dividend_yield = float(input_data['dividend_yield']) if input_data['dividend_yield'] else 0.0
            
            if quantity <= 0 or buy_price <= 0:
                messagebox.showerror("Ошибка", "Количество и цена должны быть положительными")
                return
            
            success, message = self.portfolio_manager.add_etf(
                input_data['ticker'], quantity, buy_price, dividend_yield
            )
            
            if success:
                self._refresh_interface()
                self.transaction_manager.record_transaction(
                    input_data['ticker'], 'buy', quantity, buy_price
                )
                messagebox.showinfo("Успех", message)
            else:
                messagebox.showerror("Ошибка", message)
                
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    def sell_etf(self):
        """Продажа ETF из портфеля"""
        input_data = self.ui_components.get_sell_input_values()
        
        if not input_data['ticker'] or not input_data['quantity'] or not input_data['price']:
            messagebox.showerror("Ошибка", "Заполните все поля для продажи")
            return
        
        try:
            quantity = int(input_data['quantity'])
            price = float(input_data['price'])
            
            if quantity <= 0 or price <= 0:
                messagebox.showerror("Ошибка", "Количество и цена должны быть положительными")
                return
            
            success, message = self.portfolio_manager.sell_etf(
                input_data['ticker'], quantity, price
            )
            
            if success:
                self._refresh_interface()
                self.transaction_manager.record_transaction(
                    input_data['ticker'], 'sell', quantity, price
                )
                messagebox.showinfo("Успех", message)
            else:
                messagebox.showerror("Ошибка", message)
                
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    def update_all_prices(self):
        """Обновление цен всех ETF в портфеле"""
        if not self.portfolio_manager.portfolio_data:
            messagebox.showinfo("Обновление цен", "Портфель ETF пуст")
            return
        
        # Показываем диалог прогресса
        progress_window = self.ui_components.show_progress_dialog("Обновление цен ETF...")
        
        def update_task():
            # Обновляем цены и получаем результаты
            updated_count, total_count = self.portfolio_manager.update_all_prices()
            
            # Закрываем прогресс и обновляем интерфейс
            progress_window.destroy()
            self._refresh_interface()
            
            # Показываем детальный отчет
            if updated_count == total_count:
                messagebox.showinfo("Обновление завершено", 
                                  f"Цены успешно обновлены для всех {total_count} ETF")
            else:
                messagebox.showinfo("Обновление завершено", 
                                  f"Цены обновлены для {updated_count} из {total_count} ETF\n"
                                  f"Не удалось обновить: {total_count - updated_count} ETF")
        
        # Запускаем обновление с задержкой для отображения прогресса
        self.window.after(100, update_task)
    
    def delete_selected(self):
        """Удаление выбранного ETF из портфеля"""
        selected_ticker = self.ui_components.get_selected_ticker()
        if not selected_ticker:
            messagebox.showwarning("Внимание", "Выберите ETF для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", f"Удалить ETF {selected_ticker} из портфеля?"):
            self.portfolio_manager.delete_etf(selected_ticker)
            self._refresh_interface()
            messagebox.showinfo("Успех", f"ETF {selected_ticker} удален из портфеля")
    
    def clear_portfolio(self):
        """Полная очистка портфеля ETF"""
        if not self.portfolio_manager.portfolio_data:
            messagebox.showinfo("Очистка", "Портфель ETF уже пуст")
            return
        
        if messagebox.askyesno("Подтверждение", 
                              "Вы уверены, что хотите полностью очистить портфель ETF?\n"
                              "Все данные будут удалены безвозвратно."):
            self.portfolio_manager.clear_portfolio()
            self._refresh_interface()
            messagebox.showinfo("Успех", "Портфель ETF очищен")
    
    def show_transaction_history(self):
        """Показать историю транзакций ETF"""
        self.transaction_manager.show_transaction_history(self.window)
    
    def show_dividend_calculation(self):
        """Показать расчет дивидендного дохода"""
        portfolio_data = self.portfolio_manager.portfolio_data
        if not portfolio_data:
            messagebox.showwarning("Внимание", "Портфель ETF пуст")
            return
        
        self.ui_components.show_dividend_calculation(portfolio_data)
    
    def export_to_csv(self):
        """Экспорт портфеля ETF в CSV файл"""
        success, message = self.portfolio_manager.export_to_csv()
        if success:
            messagebox.showinfo("Экспорт завершен", message)
        else:
            messagebox.showerror("Ошибка", message)
    
    def show_commission_settings(self):
        """Показать настройки комиссий"""
        self.portfolio_manager.show_commission_settings(self.window)
    
    def _refresh_interface(self):
        """Обновление интерфейса"""
        self.ui_components.refresh_table(self.portfolio_manager.portfolio_data)
        self.ui_components.update_statistics(self.portfolio_manager.portfolio_data)
        self.ui_components.update_sell_ticker_combo(self.portfolio_manager.get_tickers())
    
    def close(self):
        """Закрытие окна портфеля ETF"""
        self.portfolio_manager.save_portfolio_data()
        self.window.destroy()