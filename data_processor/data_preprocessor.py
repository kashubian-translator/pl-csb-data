from logging import Logger


class DataPreprocessor:
    __logger: Logger

    def __init__(self, logger: Logger):
        self.__logger = logger

    def clean_data(self):
        pass

    def merge_data(self):
        pass

    def split_data(self):
        pass

    def augment_data(self):
        pass
