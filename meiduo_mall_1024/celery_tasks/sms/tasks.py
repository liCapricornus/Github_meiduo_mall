# 生产者 -- 任务 函数
# 1. 这个函数 必须要让celery的实例task装饰器装饰
# 2. 需要celery自动检测指定包的任务

from celery_tasks.main import app
from libs.yuntongxun.sms import CCP


@app.task
# @shared_task
def celery_send_sms_code(mobile, sms_code):
    CCP().send_template_sms(mobile,[sms_code,3],1)