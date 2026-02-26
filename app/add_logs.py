import logging
import structlog

log = structlog.get_logger()

def news_log(news_id, from_cache):
    source = 'database'
    if from_cache:
        source = 'cache'
    log.info("news_get", news_id=news_id, source=source)
    return

def user_log(username, from_cache):
    source = 'database'
    if from_cache:
        source = 'cache'
    log.info(f"user_taken", username=username, source=source)
    return

def send_email_log(username, news_id):
    log.info(f"one_news_notification", username=username, news_id=news_id)
    return

def weekly_report_log(username):
    log.info("week_report", username=username)
    return