# dbrouters.py

class SarthakKasheeRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'erp_app':
            return 'sarthak_kashee'
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'erp_app':
            return False
        return True
