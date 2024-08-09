class MPMSDBRouter:
    """
    A router to control all database operations on models in the
    mpms_db application.
    """
    route_app_labels = {'mpms'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read mpms models go to mpms_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'mpms_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write mpms models go to mpms_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'mpms_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in mpms is involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the mpms's models get created on the right database.
        """
        if app_label in self.route_app_labels:
            return db == 'mpms_db'
        return None
