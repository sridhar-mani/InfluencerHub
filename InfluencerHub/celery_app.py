from celery import Celery
from app import app

def make_celery(app):
    redis_url = "redis://:hqNoRpztHCBnh46RrKz4QL4CS9xkuScn@redis-10812.c322.us-east-1-2.ec2.redns.redis-cloud.com:10812/0"
    celery=Celery(app.import_name,broker=redis_url,backend=redis_url)
    celery.conf.update({
        'broker_transport_options':{'protocol':3},
        'redis_backend_use_ssl':{'ssl_cert_reqs':0}
    })

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

celery = make_celery(app)