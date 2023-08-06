"""
Copyright 2021 Daniel Afriyie

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import shutil
import errno
import stat


def abstractmethod(func):
    """A decorator indicating a method is abstract method"""

    def wrap(self, *args, **kwargs):
        raise NotImplementedError(f"{self.__class__.__name__}.{func.__name__} is not implemented!")

    return wrap


def get_data(fn, split=False, split_char=None, filter_blanks=False):
    """
    :param fn: filename to open
    :param split: if you want to split the data read
    :param split_char: character you want to split the data on
    :param filter_blanks: remove empty strings if split=True
    Example:
    >>>data = get_data('file.txt', split=True, split_char=",")
    >>>print(data)
    [1, 2, 3, 4]
    """
    with open(fn, encoding='utf-8') as f:
        data = f.read()
        if split:
            if split_char:
                data = data.split(split_char)
                if filter_blanks:
                    data = [s.strip() for s in data if s.strip() != '']
    return data


def mk_dir(*paths):
    for p in paths:
        if not os.path.exists(p):
            os.mkdir(p)


def get_filename(name, path, is_folder=False):
    files = os.listdir(path)
    split = name.split('.')
    if is_folder is False:
        ext = f".{split.pop(-1)}"
        fn = ''.join(split)
    else:
        fn = name
        ext = ''
    counter = 1
    while True:
        if name not in files:
            files.append(name)
            return os.path.join(path, name)
        name = f"{fn}({counter}){ext}"
        counter += 1


def handle_remove_read_only(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def remove_dir(p):
    try:
        shutil.rmtree(p, ignore_errors=False, onerror=handle_remove_read_only)
    except:
        pass
