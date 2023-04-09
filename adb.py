import os


class ADB:
    def __init__(self):
        self.cmd = "adb devices -l"
        self.list = []
        self.device_ids = []
        self.model_names = []
        self.product_names = []

    def get_connected(self):
        self.list = os.popen(self.cmd).read().splitlines()

    def read_device_ids(self):
        if not self.list:
            self.get_connected()

        for i in range(1, len(self.list)-1):
            line = self.list[i]
            if line.split()[0] not in self.device_ids:
                self.device_ids.append(line.split()[0])

    def get_device_ids(self) -> list:
        self.read_device_ids()
        return self.device_ids

    def read_product_names(self):
        if not self.list:
            self.get_connected()

        for i in range(1, len(self.list)-1):
            line = self.list[i]
            if line.split("product:")[1].split()[0] not in self.product_names:
                self.product_names.append(line.split("product:")[1].split()[0])

    def get_product_names(self) -> list:
        self.read_product_names()
        return self.product_names

    def read_model_names(self):
        if not self.list:
            self.get_connected()

        for i in range(1, len(self.list)-1):
            line = self.list[i]
            if line.split("model:")[1].split()[0] not in self.model_names:
                self.model_names.append(line.split("model:")[1].split()[0])

    def get_model_names(self) -> list:
        self.read_model_names()
        return self.model_names