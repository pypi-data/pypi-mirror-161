class ParameterManager:
    def __init__(self):
        self.param_dict = {}

    def put_param(self, param_name, param_value):
        self.param_dict[param_name] = param_value

    def get_param(self, param_name, default_value=""):
        if param_name in self.param_dict:
            return self.param_dict[param_name]
        else:
            return default_value
