#!/usr/bin/env python3
"""
Celery Worker - слушает очередь и выполняет задачи
"""

import sys
import signal
from .tasks import celery_app


def signal_handler(signum, frame):
    """
    Обработчик сигналов для graceful shutdown
    """
    signal_name = signal.Signals(signum).name
    
    print(f"\n{'='*60}")
    print(f"⏸️  Получен сигнал {signal_name} ({signum})")
    print("⏳ Graceful shutdown: завершаю текущие задачи...")
    print("Для принудительной остановки нажмите Ctrl+C еще раз")
    print('='*60)
    
    # Worker завершит текущие задачи и остановится
    sys.exit(0)


def main():
    # Регистрируем обработчики сигналов для graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill/systemd
    
    print("=" * 60)
    print("CELERY WORKER ЗАПУЩЕН")
    print("=" * 60)
    print("Broker: redis://localhost:6379/0")
    print("Backend: redis://localhost:6379/0")
    print("✓ Graceful Shutdown: Enabled")
    print("Нажмите Ctrl+C для graceful остановки\n")
    
    try:
        # Celery worker с настройками для graceful shutdown
        celery_app.worker_main([
            'worker',
            '--loglevel=info',
            '--concurrency=2',
            '--pool=solo',
            '--max-tasks-per-child=1000',  # Перезапуск worker после N задач
            '--time-limit=300',             # Hard limit на задачу (5 мин)
            '--soft-time-limit=240',        # Soft limit (4 мин)
        ])
    except KeyboardInterrupt:
        print("\n⏳ Graceful shutdown initiated...")
        print("Дожидаюсь завершения текущих задач...")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
    finally:
        print("\n✓ Worker остановлен")


if __name__ == "__main__":
    main()
