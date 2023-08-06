from os import environ


class Environment:
    @classmethod
    def is_var_truthy(cls, name, default):
        return environ.get(name, str(default)) in ['true', 'True', 'TRUE', '1']
