class SyncRouter:
    """
    Ensures everything in sync_old
    """

    route_app_labels = ("sync_old",)

    def db_for_read(self, model, **hints):
        """
        Attempts to read detsker models go to detsker.
        """
        if model._meta.app_label in self.route_app_labels:
            return "detsker"
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write detsker models go to detsker.
        """
        if model._meta.app_label in self.route_app_labels:
            return "detsker"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the detsker apps is involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure detsker apps only appear in the 'detsker' database and only
        the selected models, the rest are inspectdb stuff.
        """
        if (
            db == "detsker"
            and app_label in self.route_app_labels
            and model_name == "sync"
        ):
            return True
        elif db == "detsker":
            return False
        return None
