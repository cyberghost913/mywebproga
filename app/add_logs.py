import logging

logging.basicConfig(level=logging.INFO, filename="logs.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

def news_log(news_id, from_cache):
    source = 'database'
    if from_cache:
        source = 'cache'
    logging.info(f"news {news_id} was taken from {source}")
    return

def user_log(username, from_cache):
    source = 'database'
    if from_cache:
        source = 'cache'
    logging.info(f"user {username} was taken from {source}")
    return