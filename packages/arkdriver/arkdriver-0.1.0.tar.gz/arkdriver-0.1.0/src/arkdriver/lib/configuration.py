from abc import abstractmethod
from pathlib import Path
import configparser


class Configuration:
    def __init__(self, path: Path or str):
        self.path = Path(path)
        if not self.path.exists():
            message = f"The config.ini file could not be found in path: {self.path}"
            if self.path.parent.exists():
                print("Files Found Only: ", list(self.path.parent.iterdir()))
            raise FileNotFoundError(message)
        self.data = None

    @abstractmethod
    def __getitem__(self, item):
        pass

    @abstractmethod
    def __contains__(self, item):
        pass

    @abstractmethod
    def __delitem__(self, key):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def items(self):
        pass

    @abstractmethod
    def keys(self):
        pass


class Ini(Configuration):
    def __init__(self, path):
        super().__init__(path)
        config = configparser.ConfigParser()
        config.read(self.path)
        self.data = self.__to_dict(config)

    @classmethod
    def __to_dict(cls, data: dict, result=None):
        if result is None:
            result = {}
        for key, value in data.items():
            if isinstance(value, configparser.SectionProxy):
                result[key] = cls.__to_dict(dict(value))
            else:
                result[key] = value
        return result

    @classmethod
    def __to_array(cls, data: list):
        result = []
        for item in data:
            result.append(item)
        return list(data)

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def __iter__(self):
        return iter(self.data)

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return "<Ini(path={self.path})>"
