class GlobalDB:
    _instance = None

    def __init__(self):
        self.db = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
