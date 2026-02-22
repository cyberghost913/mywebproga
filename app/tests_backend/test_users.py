import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.users.service import UsersService
from app.users.models import User
from app.users.schemas import UserCreate

@pytest.mark.asyncio
class TestUsersService:
    """Тесты для сервиса пользователей"""
    
    @pytest_asyncio.fixture
    async def mock_db_session(self):
        """Фикстура для мока сессии БД"""
        db_mock = AsyncMock()
        return db_mock
    
    @pytest_asyncio.fixture
    async def users_service(self, mock_db_session):
        """Фикстура для создания сервиса с моком БД"""
        service = UsersService(db=mock_db_session)
        return service
    
    @pytest_asyncio.fixture
    def mock_current_user(self):
        """Фикстура для мока текущего пользователя"""
        user = MagicMock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.is_admin = False
        return user
    
    async def test_get_users(self, users_service, mock_db_session):
        """Тест получения всех пользователей"""
        # Создаем мок результата запроса
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            MagicMock(id=1, username="user1"),
            MagicMock(id=2, username="user2"),
        ]
        mock_db_session.execute.return_value = mock_result
        
        # Вызываем метод
        users = await users_service.get_users()
        
        # Проверяем
        assert len(users) == 2
        assert users[0].username == "user1"
        assert users[1].username == "user2"
        mock_db_session.execute.assert_called_once()
    
    async def test_get_user_success(self, users_service, mock_db_session, mock_current_user):
        """Тест получения пользователя по ID (успех)"""
        # Мокаем check_user_permission
        with patch('app.users.service.check_user_permission') as mock_check:
            mock_check.return_value = None
            
            # Создаем мок результата запроса
            mock_result = MagicMock()
            mock_user = MagicMock(spec=User)
            mock_user.id = 1
            mock_user.username = "testuser"
            mock_result.scalar_one.return_value = mock_user
            mock_db_session.execute.return_value = mock_result
            
            # Вызываем метод
            user = await users_service.get_user(user_id=1, current_user=mock_current_user)
            
            # Проверяем
            assert user.id == 1
            assert user.username == "testuser"
            mock_check.assert_called_once_with(1, mock_current_user)
            mock_db_session.execute.assert_called_once()
    
    async def test_get_user_not_found(self, users_service, mock_db_session, mock_current_user):
        """Тест получения пользователя по ID (не найден)"""
        # Мокаем check_user_permission
        with patch('app.users.service.check_user_permission') as mock_check:
            mock_check.return_value = None
            
            # Создаем мок, который вызовет исключение при scalar_one()
            mock_result = MagicMock()
            mock_result.scalar_one.side_effect = Exception("No row found")
            mock_db_session.execute.return_value = mock_result
            
            # Ожидаем исключение
            with pytest.raises(Exception):
                await users_service.get_user(user_id=999, current_user=mock_current_user)
            
            mock_check.assert_called_once_with(999, mock_current_user)
    
    async def test_edit_user_success(self, users_service, mock_db_session, mock_current_user):
        """Тест редактирования пользователя (успех)"""
        # Мокаем check_user_permission
        with patch('app.users.service.check_user_permission') as mock_check:
            mock_check.return_value = None
            
            # Создаем мок пользователя
            mock_user = MagicMock(spec=User)
            mock_user.id = 1
            mock_user.username = "oldname"
            mock_user.email = "old@example.com"
            
            # Мокаем первый execute (поиск пользователя)
            mock_result1 = MagicMock()
            mock_result1.scalar_one_or_none.return_value = mock_user
            mock_db_session.execute.side_effect = [mock_result1, MagicMock()]
            
            # Создаем данные для обновления
            user_data = MagicMock(spec=UserCreate)
            user_data.model_dump.return_value = {
                "username": "newname",
                "email": "new@example.com"
            }
            
            # Вызываем метод
            result = await users_service.edit_user(
                user_id=1,
                user_data=user_data,
                current_user=mock_current_user
            )
            
            # Проверяем
            mock_check.assert_called_once_with(1, mock_current_user)
            assert mock_db_session.execute.call_count == 2
            mock_db_session.commit.assert_called_once()
            
            # Проверяем, что поля обновились
            assert mock_user.username == "newname"
            assert mock_user.email == "new@example.com"
    
    async def test_edit_user_not_found(self, users_service, mock_db_session, mock_current_user):
        """Тест редактирования пользователя (не найден)"""
        # Мокаем check_user_permission (не должен вызываться если пользователь не найден)
        with patch('app.users.service.check_user_permission') as mock_check:
            # Мокаем первый execute (пользователь не найден)
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db_session.execute.return_value = mock_result
            
            # Создаем данные для обновления
            user_data = MagicMock(spec=UserCreate)
            
            # Вызываем метод
            result = await users_service.edit_user(
                user_id=999,
                user_data=user_data,
                current_user=mock_current_user
            )
            
            # Проверяем
            assert result is None
            mock_check.assert_not_called()
            mock_db_session.execute.assert_called_once()
            mock_db_session.commit.assert_not_called()
    
    async def test_remove_user_success(self, users_service, mock_db_session, mock_current_user):
        """Тест удаления пользователя (успех)"""
        # Мокаем check_user_permission
        with patch('app.users.service.check_user_permission') as mock_check:
            mock_check.return_value = None
            
            # Вызываем метод
            result = await users_service.remove_user(
                user_id=1,
                current_user=mock_current_user
            )
            
            # Проверяем
            assert result == {"message": "user with id:1 was deleted"}
            mock_check.assert_called_once_with(1, mock_current_user)
            mock_db_session.execute.assert_called_once()
            mock_db_session.commit.assert_called_once()
    
    async def test_remove_user_with_permission_check(self, users_service, mock_db_session):
        """Тест удаления пользователя с проверкой прав"""
        # Создаем мок пользователя-админа
        admin_user = MagicMock(spec=User)
        admin_user.id = 999
        admin_user.is_admin = True
        
        # Мокаем check_user_permission (должен вызываться)
        with patch('app.users.service.check_user_permission') as mock_check:
            mock_check.return_value = None
            
            # Вызываем метод
            await users_service.remove_user(
                user_id=1,
                current_user=admin_user
            )
            
            # Проверяем
            mock_check.assert_called_once_with(1, admin_user)
    
    async def test_get_user_with_admin_access(self, users_service, mock_db_session):
        """Тест получения пользователя с правами админа"""
        # Создаем мок админа
        admin_user = MagicMock(spec=User)
        admin_user.id = 999
        admin_user.is_admin = True
        
        with patch('app.users.service.check_user_permission') as mock_check:
            mock_check.return_value = None
            
            # Мокаем результат запроса
            mock_result = MagicMock()
            mock_user = MagicMock(spec=User)
            mock_user.id = 1
            mock_user.username = "targetuser"
            mock_result.scalar_one.return_value = mock_user
            mock_db_session.execute.return_value = mock_result
            
            # Админ пытается получить другого пользователя
            user = await users_service.get_user(
                user_id=1,
                current_user=admin_user
            )
            
            # Проверяем
            assert user.id == 1
            assert user.username == "targetuser"
            mock_check.assert_called_once_with(1, admin_user)