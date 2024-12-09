from django.apps import AppConfig


class StaticConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'static'
    def ready(self):
        from datlich.jobs import start_scheduler
        start_scheduler()