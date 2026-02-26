import pytest
from unittest.mock import patch, MagicMock
import structlog
from app.add_logs import news_log, user_log, send_email_log, weekly_report_log

class TestLogs:
    """Тесты для модуля логирования"""
    
    def test_news_log_from_database(self):
        """Тестируем логирование новостей из базы данных"""
        with patch('app.add_logs.log') as mock_log:
            # Вызываем функцию с from_cache=False (значит из базы данных)
            news_log(news_id=123, from_cache=False)
            
            # Проверяем, что log.info был вызван с правильными параметрами
            mock_log.info.assert_called_once_with(
                "news_get",
                news_id=123,
                source='database'
            )
    
    def test_news_log_from_cache(self):
        """Тестируем логирование новостей из кэша"""
        with patch('app.add_logs.log') as mock_log:
            # Вызываем функцию с from_cache=True (значит из кэша)
            news_log(news_id=456, from_cache=True)
            
            # Проверяем, что log.info был вызван с правильными параметрами
            mock_log.info.assert_called_once_with(
                "news_get",
                news_id=456,
                source='cache'
            )
    
    def test_user_log_from_database(self):
        """Тестируем логирование пользователей из базы данных"""
        with patch('app.add_logs.log') as mock_log:
            # Вызываем функцию с from_cache=False
            user_log(username="testuser", from_cache=False)
            
            # Проверяем, что log.info был вызван с правильными параметрами
            mock_log.info.assert_called_once_with(
                "user_taken",
                username="testuser",
                source='database'
            )
    
    def test_user_log_from_cache(self):
        """Тестируем логирование пользователей из кэша"""
        with patch('app.add_logs.log') as mock_log:
            # Вызываем функцию с from_cache=True
            user_log(username="cached_user", from_cache=True)
            
            # Проверяем, что log.info был вызван с правильными параметрами
            mock_log.info.assert_called_once_with(
                "user_taken",
                username="cached_user",
                source='cache'
            )
    
    def test_send_email_log(self):
        """Тестируем логирование отправки email"""
        with patch('app.add_logs.log') as mock_log:
            # Вызываем функцию
            send_email_log(username="user123", news_id=789)
            
            # Проверяем, что log.info был вызван с правильными параметрами
            mock_log.info.assert_called_once_with(
                "one_news_notification",
                username="user123",
                news_id=789
            )
    
    def test_weekly_report_log(self):
        """Тестируем логирование еженедельного отчета"""
        with patch('app.add_logs.log') as mock_log:
            # Вызываем функцию
            weekly_report_log(username="weekly_user")
            
            # Проверяем, что log.info был вызван с правильными параметрами
            mock_log.info.assert_called_once_with(
                "week_report",
                username="weekly_user"
            )
    
    def test_all_functions_with_different_values(self):
        """Тестируем все функции с разными значениями параметров"""
        with patch('app.add_logs.log') as mock_log:
            # Тестируем news_log
            news_log(news_id=999, from_cache=False)
            mock_log.info.assert_any_call(
                "news_get",
                news_id=999,
                source='database'
            )
            
            # Тестируем user_log
            user_log(username="different_user", from_cache=True)
            mock_log.info.assert_any_call(
                "user_taken",
                username="different_user",
                source='cache'
            )
            
            # Тестируем send_email_log
            send_email_log(username="email_user", news_id=111)
            mock_log.info.assert_any_call(
                "one_news_notification",
                username="email_user",
                news_id=111
            )
            
            # Тестируем weekly_report_log
            weekly_report_log(username="report_user")
            mock_log.info.assert_any_call(
                "week_report",
                username="report_user"
            )
            
            # Проверяем, что было 4 вызова
            assert mock_log.info.call_count == 4