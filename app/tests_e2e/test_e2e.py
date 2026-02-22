import re
import pytest
from playwright.sync_api import Page, expect

TEST_USERNAME = "author1"
TEST_PASSWORD = "author1"

def test_complete_news_crud_ui_flow(page: Page):
    
    # ============ ЧАСТЬ 1: ЗАГРУЗКА СТРАНИЦЫ ============
    print("\n" + "="*60)
    print("ШАГ 1: Загрузка главной страницы")
    print("="*60)
    page.goto("http://localhost:5173/")
    expect(page).to_have_title(re.compile(".*"))
    expect(page.get_by_role("link", name="Войти")).to_be_visible()
    print("✓ Страница загружена")
    
    # ============ ЧАСТЬ 2: АВТОРИЗАЦИЯ ============
    print("\n" + "="*60)
    print("ШАГ 2: Авторизация пользователя")
    print("="*60)
    page.get_by_role("link", name="Войти").click()
    page.get_by_role("textbox", name="Логин").fill(TEST_USERNAME)
    page.get_by_role("textbox", name="Пароль").fill(TEST_PASSWORD)
    page.get_by_role("button", name="Войти").click()
    expect(page.get_by_role("link", name=f"Профиль ({TEST_USERNAME})")).to_be_visible(timeout=10000)
    print("✓ Успешная авторизация")
    
    # ============ ЧАСТЬ 3: СОЗДАНИЕ НОВОСТИ ============
    print("\n" + "="*60)
    print("ШАГ 3: Создание новой новости")
    print("="*60)
    page.get_by_role("button", name="Добавить новость").click()
    page.get_by_role("textbox", name="Заголовок").fill("E2E Test News - Создание")
    page.get_by_role("textbox", name="Содержимое").fill("Это новость создана через e2e тест")
    page.get_by_role("button", name="Создать").click()
    expect(page.get_by_role("link", name="E2E Test News - Создание")).to_be_visible(timeout=10000)
    print("✓ Новость создана")
    
    # ============ ЧАСТЬ 4: ЧТЕНИЕ НОВОСТИ ============
    print("\n" + "="*60)
    print("ШАГ 4: Чтение созданной новости")
    print("="*60)
    page.get_by_role("link", name="E2E Test News - Создание").first.click()
    expect(page.get_by_text("E2E Test News - Создание")).to_be_visible()
    expect(page.get_by_text("Это новость создана через e2e тест")).to_be_visible()
    page.get_by_role("link", name="Home").click()
    print("✓ Новость прочитана")
    
    # ============ ЧАСТЬ 5: РЕДАКТИРОВАНИЕ НОВОСТИ ============
    print("\n" + "="*60)
    print("ШАГ 5: Редактирование новости")
    print("="*60)
    page.get_by_role("link", name="E2E Test News - Создание").first.click()
    page.get_by_role("button", name="Редактировать").click()
    page.get_by_role("textbox", name="Заголовок").fill("E2E Test News - Редактирование")
    page.get_by_role("textbox", name="Содержимое").fill("Это новость ОТРЕДАКТИРОВАНА через e2e тест")
    page.get_by_role("button", name="Сохранить").click()
    expect(page.get_by_text("E2E Test News - Редактирование")).to_be_visible(timeout=10000)
    page.get_by_role("link", name="Home").click()
    print("✓ Новость отредактирована")
    
    # ============ ЧАСТЬ 6: УДАЛЕНИЕ НОВОСТИ ============
    print("\n" + "="*60)
    print("ШАГ 6: Удаление новости")
    print("="*60)
    page.get_by_role("link", name="E2E Test News - Редактирование").click()
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Удалить").click()
    expect(page.get_by_role("link", name="E2E Test News - Редактирование")).not_to_be_visible(timeout=10000)
    print("✓ Новость удалена")
    
    # ============ ЧАСТЬ 7: ВЫХОД ИЗ СИСТЕМЫ ============
    print("\n" + "="*60)
    print("ШАГ 7: Выход из системы")
    print("="*60)
    page.get_by_role("link", name=f"Профиль ({TEST_USERNAME})").click()
    page.get_by_role("banner").get_by_role("button", name="Выйти").click()
    expect(page.get_by_role("link", name="Войти")).to_be_visible()
    print("✓ Успешный выход")
    
    print("\n" + "="*60)
    print("✅ E2E ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
    print("Весь UI флоу (создание → чтение → редактирование → удаление) пройден")
    print("="*60)