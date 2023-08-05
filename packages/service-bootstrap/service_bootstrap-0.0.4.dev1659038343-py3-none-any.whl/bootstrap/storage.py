import json
import mimetypes
import os
import shutil


class SingleObjectStorage:
    def __init__(self, file_name):
        self.file_name = file_name

    def load(self, default_value=None):
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_value

    def save(self, data):
        with open(self.file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, indent=4))


class KeyValueStorage:
    def __init__(self, dir_name):
        self.dir_name = dir_name

    def contains(self, key):
        return os.path.exists(f'{self.dir_name}/{key}.json')

    def __contains__(self, key):
        return self.contains(key)

    def get(self, key, default_value=None):
        if os.path.exists(f'{self.dir_name}/{key}.json'):
            with open(f'{self.dir_name}/{key}.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_value

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def keys(self):
        result = []
        a = {}
        a.keys()
        for file in os.listdir(self.dir_name):
            if file.endswith('.json'):
                with open(f'{self.dir_name}/{file}', 'r', encoding='utf-8') as f:
                    result.append(json.load(f))
        return result

    def __iter__(self):
        return self.keys().__iter__()

    def set(self, key, value):
        with open(f'{self.dir_name}/{key}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(value, indent=4))
            f.flush()


class FilesStorage:
    def __init__(self, dir_name):
        self.dir_name = dir_name

    def list(self):
        return os.listdir(self.dir_name)

    def __iter__(self):
        return self.list().__iter__()

    def __path(self, item):
        return f'{self.dir_name}/{item}'

    def __contains__(self, item):
        return os.path.exists(self.__path(item))

    def get_path(self, item):
        if item in self:
            return self.__path(item)
        return None

    def get_root_path(self):
        return self.dir_name

    def upload(self, src, dest_name):
        shutil.copy(src, f'{self.dir_name}/{dest_name}')
        os.chmod(f'{self.dir_name}/{dest_name}', 0o777)

    def __setitem__(self, item, src):
        return self.upload(src, item)

    def guess_mime_type(self, item):
        if item not in self:
            return None, None
        return mimetypes.guess_type(self.__path(item))

    def open(self, item, mode='r'):
        return open(self.__path(item), mode)


class Storage:
    def __init__(self, dir):
        self.dir = dir

    def open_key_value_storage(self, storage_name) -> KeyValueStorage:
        path = f'{self.dir}/{storage_name}'
        os.makedirs(path, exist_ok=True)
        return KeyValueStorage(path)

    def open_single_object_storage(self, storage_name) -> SingleObjectStorage:
        path = f'{self.dir}/{storage_name}'
        os.makedirs(path, exist_ok=True)
        return SingleObjectStorage(f'{path}/{storage_name}.json')

    def open_files_storage(self, storage_name) -> FilesStorage:
        path = f'{self.dir}/{storage_name}'
        os.makedirs(path, exist_ok=True)
        return FilesStorage(path)
