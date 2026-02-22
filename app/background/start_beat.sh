#!/bin/bash

echo "Starting Celery Beat (Scheduler)..."
echo "Make sure Redis and Worker are running!"
echo ""


celery -A tasks beat --loglevel=info