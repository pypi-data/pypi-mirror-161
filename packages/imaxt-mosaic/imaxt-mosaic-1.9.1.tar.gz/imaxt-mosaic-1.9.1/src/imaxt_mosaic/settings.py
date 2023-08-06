class Settings:
    timeout = 1800

    @classmethod
    def set_config(cls, config):
        for k in config:
            setattr(cls, k, config[k])
