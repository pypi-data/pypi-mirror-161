import yaml


class DataHandler:
    def __init__(self, full_path, file_name):
        self.full_path = full_path
        self.file_name = file_name

    def get_file_contents(self):
        with open(self.full_path) as f:
            data = None
            type = "unknown"

            try:
                data = yaml.load(f, Loader=yaml.FullLoader)
                type = "yml"
            except Exception as e:
                pass

            if data == None:
                with open(self.full_path) as f:
                    data = f.readlines()

            return type, data

    def get_file_name(self):
        return self.file_name

    def get_file_path(self):
        return self.full_path
