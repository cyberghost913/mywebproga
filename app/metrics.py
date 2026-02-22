from prometheus_client import Counter, REGISTRY
from fastapi import APIRouter
from datetime import datetime
import json


NEWS_CREATED = Counter('total_news_created', 'Amount of created news')

USERS_REGISTERED = Counter('total_registerations', 'Amount of registered users')

NOTIFICATION_SENT = Counter('notification_sent', 'Amount of sent notifications', ['type', 'status'])

router = APIRouter()

@router.get("/json")
async def get_metrics_json():
    metrics_data = {}

    for metric in REGISTRY.collect():
        metric_name = metric.name
        
        samples = []
        for sample in metric.samples:
            samples.append({
                'name': sample.name,
                'value': float(sample.value),
                'labels': sample.labels
            })
        
        metrics_data[metric_name] = {
            'help': metric.documentation,
            'type': metric.type,
            'samples': samples
        }
    
    return {
        'timestamp': datetime.now().isoformat(),
        'metrics': metrics_data
    }