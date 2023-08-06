import json
import os.path
import logging
import collections.abc
from typing import Any

logging.root.setLevel(logging.ERROR)
logger = logging.getLogger("__smarterStore__")
logger.setLevel(level=logging.ERROR)


class SmarterStore:
    def __init__(self, deploy_dir: str):
        self.__project_manifest = deploy_dir + '/_manifest.json'
        self.__global_path = deploy_dir + '/../_data/index.json'
        self.__store_dir = deploy_dir + '/_data/'
        self._check_store_dir()
        self.__manifest = self._load_manifest()

    @staticmethod
    def _get_filename(pattern: str) -> str:
        return pattern.split(".")[0] + ".json"

    @staticmethod
    def _create_dict_from_pattern(pattern: str, value: Any) -> Any:
        split_str = pattern.split(".")
        keys = split_str[1:-1]
        new_data = {split_str[-1]: value} if len(split_str) > 1 else value
        for key in keys[::-1]:
            new_data = {key: new_data}
        return new_data

    @staticmethod
    def _get_json_property(json_obj: dict, property_sequence: str, default: Any = None) -> Any:
        property_sequence_list = property_sequence.split(".")
        data = json_obj
        for prop in property_sequence_list:
            if not data or type(data) != dict:
                return default
            data = data.get(prop)
        return data

    @staticmethod
    def _write_json(file_path: str, data: Any) -> None:
        with open(file_path, "w") as jsonFile:
            try:
                jsonFile.write(json.dumps(data))
            except Exception as ex:
                logger.error(f"Failed to save data to file, please check data is json serializable. Got Error {ex}")

    @staticmethod
    def _read_json(file_path: str) -> Any:
        if not os.path.isfile(file_path):
            return
        with open(file_path, "r") as jsonFile:
            data = json.load(jsonFile)
        return data

    def _check_store_dir(self) -> None:
        is_exist = os.path.exists(self.__store_dir)
        if not is_exist:
            os.makedirs(self.__store_dir)
            logger.info(
                f"Store directory was missing and has been automatically created at the path {self.__store_dir}")

    def _update(self, original_data: Any, update_data: Any) -> dict:
        if type(original_data) != dict:
            original_data = {}
        for k, v in update_data.items():
            if isinstance(v, collections.abc.Mapping):
                original_data[k] = self._update(original_data.get(k, {}), v)
            else:
                original_data[k] = v
        return original_data

    def _update_pattern_data(self, pattern_filename: str, new_data) -> Any:
        if not os.path.isfile(self.__store_dir + pattern_filename):
            return new_data
        original_data = self._read_json(file_path=self.__store_dir + pattern_filename)
        if type(original_data) != dict:
            return new_data
        self._update(original_data, new_data)
        return original_data

    def _get_data(self, pattern: str) -> Any:
        pattern_filename = self._get_filename(pattern=pattern)
        data = self._read_json(file_path=self.__store_dir + pattern_filename)
        if not data:
            return None
        keys = pattern.split(".")[1:]
        for key in keys:
            if type(data) != dict or key not in data:
                data = None
                break
            data = data[key]
        return data

    def _set_pattern_data(self, pattern: str, data: Any) -> None:
        pattern_filename = self._get_filename(pattern)
        new_data = self._create_dict_from_pattern(pattern=pattern, value=data)
        data = self._update_pattern_data(pattern_filename, new_data) if type(new_data) == dict else new_data
        self._write_json(file_path=self.__store_dir + pattern_filename, data=data)

    def _append_pattern_data(self, pattern: str, new_data: Any) -> None:
        original_data = self._get_data(pattern=pattern)
        if not original_data:
            original_data = new_data
        else:
            if type(original_data) != list:
                logger.error(f"Error: Can't append {type(new_data)} to a {type(original_data)} json object")
                return
            original_data.append(new_data)
        self._set_pattern_data(pattern=pattern, data=original_data)

    def _prepend_pattern_data(self, pattern: str, new_data: Any) -> None:
        original_data = self._get_data(pattern=pattern)
        if not original_data:
            original_data = new_data
        else:
            if type(original_data) != list:
                logger.error(f"Error: Can't append {type(new_data)} to a {type(original_data)} json object")
                return
            original_data.insert(0, new_data)
        self._set_pattern_data(pattern=pattern, data=original_data)

    def _load_manifest(self) -> Any:
        data = self._read_json(file_path=self.__project_manifest)
        return data or {}

    def get_pattern_data(self, pattern: str) -> Any:
        try:
            return self._get_data(pattern)
        except Exception as ex:
            logger.error(f"Failed to get pattern data. Error: {ex}")

    def set_pattern_data(self, pattern: str, data: Any) -> None:
        try:
            self._set_pattern_data(pattern, data)
        except Exception as ex:
            logger.error(f"Failed to set pattern data. Error: {ex}")

    def append_pattern_data(self, pattern: str, data: Any) -> None:
        try:
            self._append_pattern_data(pattern=pattern, new_data=data)
        except Exception as ex:
            logger.error(f"Failed to append pattern data. Error: {ex}")

    def prepend_pattern_data(self, pattern: str, data: Any) -> None:
        try:
            self._prepend_pattern_data(pattern=pattern, new_data=data)
        except Exception as ex:
            logger.error(f"Failed to prepend pattern data. Error: {ex}")

    def get_manifest_property(self, property_sequence: str = "") -> Any:
        """
        :param property_sequence: Example "details.meta.location"
        :return:
        """
        if not self.__manifest:
            return {}
        return self._get_json_property(json_obj=self.__manifest, property_sequence=property_sequence, default={})

    def read_global_store(self, pattern: str) -> Any:
        """
            :param pattern:
            :return:
        """
        if not os.path.exists(self.__global_path):
            return {}
        json_data = self._read_json(file_path=self.__global_path)
        if type(json_data) != dict:
            return {}
        return self._get_json_property(json_obj=json_data, property_sequence=pattern, default={})

    def write_global_store(self, pattern: str, data: Any) -> None:
        real_data = self._read_json(file_path=self.__global_path)
        if type(real_data) != dict:
            real_data = {}
        new_data = self._create_dict_from_pattern(pattern=pattern, value=data)
        data = self._update(original_data=real_data, update_data=new_data) if type(new_data) == dict else new_data
        self._write_json(file_path=self.__global_path, data=data)
