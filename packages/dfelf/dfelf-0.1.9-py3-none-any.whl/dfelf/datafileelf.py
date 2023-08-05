import os
import hashlib
from abc import ABCMeta, abstractmethod
from dfelf.commons import logger


class DataFileElf(metaclass=ABCMeta):

    def __init__(self, output_dir=None, output_flag=True):
        self._config = None
        self._output_flag = output_flag
        self.init_config()
        self._cwd = os.getcwd()
        self._log_path = self.get_filename_with_path('log')
        self._output_path = None
        self.set_output(output_dir)
        self.init_dir()

    def shutdown_output(self):
        self._output_flag = False

    def activate_output(self):
        self._output_flag = True

    def set_output(self, output_dir):
        if output_dir is None:
            self._output_path = self.get_filename_with_path('output')
        else:
            self._output_path = self.get_filename_with_path(output_dir)
            if not os.path.exists(self._output_path):
                os.makedirs(self._output_path)

    def init_dir(self):
        if not os.path.exists(self._log_path):
            os.makedirs(self._log_path)
        if not os.path.exists(self._output_path):
            os.makedirs(self._output_path)

    def get_filename_with_path(self, filename):
        return os.path.join(self._cwd, filename)

    def get_output_path(self, filename):
        return os.path.join(self._output_path, filename)

    def get_log_path(self, filename):
        return os.path.join(self._log_path, filename)

    @abstractmethod
    def init_config(self):
        pass  # pragma: no cover

    @abstractmethod
    def to_output(self, task_key, **kwargs):
        pass  # pragma: no cover

    def is_default(self, task_key):
        res = self._config.is_default(task_key)
        if res:
            logger.warning([1000, task_key])
        return res

    def set_config_by_task_key(self, task_key, **kwargs):
        new_kwargs = {
            task_key: kwargs
        }
        self.set_config(**new_kwargs)

    def set_config(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._config:
                self._config[key] = value

    def generate_config_file(self, config_filename=None, **kwargs):
        self.set_config(**kwargs)
        self._config.dump(config_filename)

    def load_config(self, config_filename):
        self._config.load_config(config_filename)

    def get_config(self):
        return self._config

    def checksum(self, filename):
        hash_md5 = hashlib.md5()
        input_filename = self.get_filename_with_path(filename)
        with open(input_filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
