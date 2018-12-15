import logging
from django.db.models import F
from django.apps import apps
from forum.models import Message
from story_pieces.celery import app

logger = logging.getLogger('record')

@app.task(ignore_result=True)
def raise_heat(id, type, number):
    try:
        app_label = 'member' if type == 'UserGroup' else 'forum'
        Type = apps.get_model(app_label, type)
        Type.objects.filter(id=id).update(heat=F('heat') + number)
    except Exception as e:
        logger.info(e)


@app.task(ignore_result=True)
def add_likes(message_id):
    try:
        Message.objects.filter(id=message_id).update(likes_num=F('likes_num') + 1)
    except Exception as e:
        logger.info(e)


@app.task
def add_answers(message_id):
    try:
        Message.objects.filter(id=message_id).update(answers_num=F('answers_num') + 1)
    except Exception as e:
        logger.info(e)