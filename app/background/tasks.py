from celery import Celery
from ..add_redis import get_sync_redis
from ..database import get_sync_session
import time
from celery.schedules import crontab
from ..add_logs import send_email_log, weekly_report_log
from sqlalchemy import text
from datetime import datetime, timedelta
from ..metrics import NOTIFICATION_SENT

celery_app = Celery(
    'email_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    'weekly-news-digest': {
        'task': 'tasks.weekly_notification',
        'schedule': crontab(hour=22, minute=0, day_of_week=0),  # воскресенье, 22:00
    },
}

def smtp_logic(email, message):
    time.sleep(0.5)
    pass

@celery_app.task(name='tasks.send_news_notification',
                 bind=True,
                 max_retries=3,
                 retry_backoff_max=30,
                 retry_jitter=True,    
                 autoretry_for=(Exception,),   
                 retry_backoff=True)          
def send_news_notification(self, email_list, fresh_news):
    email_send = 0
    redis = get_sync_redis()
    message = f"Breaking News: {fresh_news['header']}"
    for email in email_list:
        key = f"sent:news:{fresh_news['id']}:{email}"
        sent = redis.get(key)
        if sent:
            continue
        try:
            smtp_logic(email, message)
            redis.setex(key, 86400, "True")
            send_email_log(email, fresh_news['id'])
            email_send += 1
            NOTIFICATION_SENT.labels(type='create', status='success').inc()
        except Exception as e:
            NOTIFICATION_SENT.labels(type='create', status='fail').inc()
            print(f"Error {e} for {email}")
    return email_send


@celery_app.task(name='tasks.weekly_notification',
                 bind=True,
                 max_retries=3,
                 retry_backoff_max=60,
                 retry_jitter=True,   
                 autoretry_for=(Exception,),   
                 retry_backoff=True)
def weekly_notification(self):
    email_send = 0
    redis = get_sync_redis()
    with get_sync_session() as db:
        today = datetime.now().date()
        week_num = today.isocalendar()[1]
        week_ago = today - timedelta(days=7)

        news_result = db.execute(
            text("SELECT header FROM news WHERE date >= :week_ago"),
            {"week_ago": week_ago}
        )
        news_headers = [row[0] for row in news_result]
        
        emails_result = db.execute(
            text("SELECT email FROM users WHERE is_active = true")
        )
        email_list = [row[0] for row in emails_result]

        message = f'See all news from last week: {news_headers}'
        for email in email_list:
            key = f'sent:week:{week_num}:{email}'
            sent = redis.get(key)
            if sent:
                continue
            try:
                smtp_logic(email, message)
                redis.setex(key, 86400, "True")
                weekly_report_log(email)
                email_send += 1
                NOTIFICATION_SENT.labels(type='weekly', status='success')
            except Exception as e:
                NOTIFICATION_SENT.labels(type='weekly', status='error')
                print(f"Error {e} for {email}")
    return email_send