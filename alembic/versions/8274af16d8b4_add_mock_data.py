"""add_mock_data

Revision ID: 8274af16d8b4
Revises: 3fca177ef5e7
Create Date: 2025-10-03 12:07:54.433606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta
import json


# revision identifiers, used by Alembic.
revision: str = '8274af16d8b4'
down_revision: Union[str, Sequence[str], None] = '3fca177ef5e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    users_table = sa.table('users',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('email', sa.String),
        sa.column('date', sa.DateTime),
        sa.column('is_author', sa.Boolean),
        sa.column('ava', sa.LargeBinary)
    )
    
    news_table = sa.table('news',
        sa.column('id', sa.Integer),
        sa.column('header', sa.String),
        sa.column('content', sa.JSON),
        sa.column('date', sa.DateTime),
        sa.column('author_id', sa.Integer),
        sa.column('cover', sa.LargeBinary)
    )
    
    comments_table = sa.table('comments',
        sa.column('id', sa.Integer),
        sa.column('text', sa.Text),
        sa.column('news_id', sa.Integer),
        sa.column('date', sa.DateTime),
        sa.column('author_id', sa.Integer)
    )
    
    op.bulk_insert(users_table, [
        {
            'name': 'Алексей Иванов',
            'email': 'alexey@example.com',
            'date': datetime.utcnow() - timedelta(days=30),
            'is_author': True,
            'ava': None
        },
        {
            'name': 'Мария Петрова', 
            'email': 'maria@example.com',
            'date': datetime.utcnow() - timedelta(days=25),
            'is_author': True,
            'ava': None
        },
        {
            'name': 'Дмитрий Сидоров',
            'email': 'dmitry@example.com',
            'date': datetime.utcnow() - timedelta(days=20),
            'is_author': False,
            'ava': None
        },
        {
            'name': 'Екатерина Козлова',
            'email': 'ekaterina@example.com',
            'date': datetime.utcnow() - timedelta(days=15),
            'is_author': False,
            'ava': None
        },
        {
            'name': 'Администратор Системы',
            'email': 'admin@example.com',
            'date': datetime.utcnow() - timedelta(days=40),
            'is_author': True,
            'ava': None
        }
    ])
    
    op.bulk_insert(news_table, [
        {
            'header': 'Запуск нового веб-сайта компании',
            'content': json.dumps({
                'text': 'Мы рады сообщить о запуске нашего нового веб-сайта. Теперь он стал еще удобнее и функциональнее!',
                'images': ['website.jpg'],
                'tags': ['новости', 'разработка', 'сайт'],
                'read_time': '3 мин'
            }, ensure_ascii=False),
            'date': datetime.utcnow() - timedelta(days=5),
            'author_id': 1,
            'cover': None
        },
        {
            'header': 'Обновление функционала комментариев на платформе',
            'content': json.dumps({
                'text': 'Добавлена возможность редактирования комментариев и ответов на них. Теперь общение стало еще удобнее!',
                'images': ['comments.png'],
                'features': ['редактирование', 'ответы', 'модерация'],
                'version': '2.1.0'
            }, ensure_ascii=False),
            'date': datetime.utcnow() - timedelta(days=3),
            'author_id': 2,
            'cover': None
        },
        {
            'header': 'Итоги года в IT индустрии: главные тренды 2024',
            'content': json.dumps({
                'text': 'Подводим итоги уходящего года в мире информационных технологий. Какие тренды стали наиболее значимыми?',
                'sections': [
                    {
                        'title': 'Искусственный интеллект', 
                        'content': 'AI продолжает развиваться семимильными шагами...',
                        'examples': ['ChatGPT', 'Midjourney', 'GitHub Copilot']
                    },
                    {
                        'title': 'Кибербезопасность', 
                        'content': 'Новые вызовы в защите данных требуют современных решений...'
                    }
                ],
                'tags': ['итоги', 'IT', 'тренды', '2024'],
                'author_notes': 'Материал подготовлен на основе аналитики рынка'
            }, ensure_ascii=False),
            'date': datetime.utcnow() - timedelta(days=1),
            'author_id': 5,
            'cover': None
        },
        {
            'header': 'Интервью с ведущим разработчиком: секреты успеха',
            'content': json.dumps({
                'text': 'Сегодня мы беседуем с нашим ведущим разработчиком о современных технологиях и подходах к программированию.',
                'interview': [
                    {
                        'question': 'Какие технологии вы используете в работе?', 
                        'answer': 'В основном Python, FastAPI, PostgreSQL, React...'
                    },
                    {
                        'question': 'Какие советы вы можете дать начинающим разработчикам?', 
                        'answer': 'Учите основы, практикуйтесь ежедневно и не бойтесь сложных задач...'
                    }
                ],
                'tags': ['интервью', 'разработка', 'советы', 'карьера'],
                'key_points': ['Постоянное обучение', 'Практика', 'Работа в команде']
            }, ensure_ascii=False),
            'date': datetime.utcnow() - timedelta(hours=12),
            'author_id': 1,
            'cover': None
        },
        {
            'header': 'Новые возможности в следующем обновлении платформы',
            'content': json.dumps({
                'text': 'Готовим большое обновление с новыми функциями и улучшениями производительности.',
                'planned_features': [
                    'Умная система рекомендаций',
                    'Оффлайн-режим',
                    'Улучшенный поиск',
                    'Интеграция с внешними API'
                ],
                'release_date': '2024-02-01',
                'status': 'в разработке'
            }, ensure_ascii=False),
            'date': datetime.utcnow() - timedelta(hours=6),
            'author_id': 5,
            'cover': None
        }
    ])
    
    op.bulk_insert(comments_table, [
        {
            'text': 'Отличная новость! Новый сайт действительно стал намного удобнее. Особенно понравился дизайн.',
            'news_id': 1,
            'date': datetime.utcnow() - timedelta(days=4),
            'author_id': 3
        },
        {
            'text': 'Ждал этого обновления! Спасибо за проделанную работу. Теперь все работает гораздо быстрее.',
            'news_id': 1, 
            'date': datetime.utcnow() - timedelta(days=4, hours=2),
            'author_id': 4
        },
        {
            'text': 'Очень удобные изменения, особенно возможность редактировать комментарии. Это экономит много времени!',
            'news_id': 2,
            'date': datetime.utcnow() - timedelta(days=2),
            'author_id': 3
        },
        {
            'text': 'Интересный обзор! Хотелось бы больше статистики по рынку и конкретных цифр.',
            'news_id': 3,
            'date': datetime.utcnow() - timedelta(hours=20),
            'author_id': 4
        },
        {
            'text': 'Полезные советы в интервью, особенно для тех кто только начинает свой путь в IT. Спасибо за материал!',
            'news_id': 4,
            'date': datetime.utcnow() - timedelta(hours=6),
            'author_id': 2
        },
        {
            'text': 'Согласен с предыдущим комментарием. Интервью очень вдохновляет и мотивирует развиваться дальше!',
            'news_id': 4,
            'date': datetime.utcnow() - timedelta(hours=4),
            'author_id': 3
        },
        {
            'text': 'Когда ждать следующих обновлений? Есть несколько идей для улучшения пользовательского опыта.',
            'news_id': 2,
            'date': datetime.utcnow() - timedelta(hours=1),
            'author_id': 4
        },
        {
            'text': 'Отличная работа команды! Особенно впечатлили новые функции в последнем обновлении.',
            'news_id': 5,
            'date': datetime.utcnow() - timedelta(hours=3),
            'author_id': 3
        },
        {
            'text': 'Интересно, будет ли поддержка мобильных устройств в оффлайн-режиме?',
            'news_id': 5,
            'date': datetime.utcnow() - timedelta(hours=2),
            'author_id': 4
        },
        {
            'text': 'С нетерпением жду выхода обновления! Особенно интересна система рекомендаций.',
            'news_id': 5,
            'date': datetime.utcnow() - timedelta(hours=1),
            'author_id': 2
        }
    ])

def downgrade():
    op.execute("DELETE FROM comments")
    op.execute("DELETE FROM news")
    op.execute("DELETE FROM users")
    
    op.execute("ALTER SEQUENCE users_id_seq RESTART WITH 1")
    op.execute("ALTER SEQUENCE news_id_seq RESTART WITH 1")
    op.execute("ALTER SEQUENCE comments_id_seq RESTART WITH 1")