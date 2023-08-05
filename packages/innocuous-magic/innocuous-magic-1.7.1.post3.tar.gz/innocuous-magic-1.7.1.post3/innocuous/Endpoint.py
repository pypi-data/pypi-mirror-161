import os
import importlib
import threading
import subprocess
from datetime import datetime
from urllib.parse import urlparse

RUN_PATH = os.getenv('RUN_PATH', '/tmp/innocuous/endpoint/app')
IMAGE_TMPE_PATH = os.getenv('IMAGE_TMPE_PATH', os.path.join(RUN_PATH, 'images'))

if not os.path.exists(IMAGE_TMPE_PATH):
    subprocess.run(f'mkdir -p {IMAGE_TMPE_PATH}', shell=True)

def __download(url, path):
    cmd = f'wget -nv {url} -P {path} 2>&1 |cut -d\\" -f2'
    process = subprocess.check_output(cmd, shell=True)
    return process.decode('utf-8').replace('\n', '').replace('\r', '')

def __clean():
    subprocess.run(f'rm -rf {IMAGE_TMPE_PATH}/*', shell=True)

def download(urls, clean=True):
    if clean:
        __clean()
    file_list = []
    for url in urls:
        file_fullname = __download(url, IMAGE_TMPE_PATH)
        file_list.append(file_fullname)
    return file_list

def save(files, clean=True):
    if clean:
        __clean()
    file_list = []
    for file in files:
        file_location = os.path.join(IMAGE_TMPE_PATH, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())	
            file_list.append(file_location)
    return file_list

class EventHandler:
    def __init__(self):
        self.listeners = []
    
    def __iadd__(self, listener):
        self.listeners.append(listener)
        return self
    
    def trigger(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)

class ModelLoader():
    __instance_lock = threading.Lock()

    def __init__(self):
        self._path = ''
        self._new_checkpoint_path_s3 = ''
        self._last_checkpoint_path = ''
        self._model = {}
        self._config = {}
        self.UpdateCheckpointHandler = EventHandler()
        
    def __new__(cls, *args, **kwargs):
        if not hasattr(ModelLoader, "_instance"):
            with ModelLoader.__instance_lock:
                if not hasattr(ModelLoader, "_instance"):
                    ModelLoader._instance = object.__new__(cls)
        return ModelLoader._instance

    def _setDownloader(self, downloader):
        self.downloader = downloader

    @property
    def checkpoint_path(self):
        return self._path

    @checkpoint_path.setter
    def checkpoint_path(self, value):
        if os.path.isfile(value):
            self._path = value
        else:
            print('Error, file not exist.')

    def save_new_checkpoint_path(self, delete_last=True):
        if self._new_checkpoint_path_s3 != '':
            path = self.downloader(self._new_checkpoint_path_s3)
            if delete_last:
                if self._last_checkpoint_path != '':
                    os.path.os.remove(self._last_checkpoint_path)
                self._last_checkpoint_path = path
            return path
        return ''

    def update_model(self, model):
        self.UpdateCheckpointHandler.trigger()
        self._model = model

    def get_model(self):
        return self._model

    def update_config(self, config):
        self._config = config

    def get_config(self):
        return self._config

class PipelineHepler():
    __instance_lock = threading.Lock()

    def __init__(self):
        self._metric = []
        self._index = -1

    def __new__(cls, *args, **kwargs):
        if not hasattr(PipelineHepler, "_instance"):
            with PipelineHepler.__instance_lock:
                if not hasattr(PipelineHepler, "_instance"):
                    PipelineHepler._instance = object.__new__(cls)
        return PipelineHepler._instance

   
    def get_last_metric(self):
        return self._metric[self._index]

    
    def get_metric(self, index=None):
        if index == None:
            return self._metric
        elif index >= 0:
            return self._metric[index]
    
    def update_last_metric(self, metric):
        self._metric.append(metric)
        self._index += 1

class FileHelper():
    __instance_lock = threading.Lock()

    def __init__(self):
        pass
        
    def __new__(cls, *args, **kwargs):
        if not hasattr(FileHelper, "_instance"):
            with FileHelper.__instance_lock:
                if not hasattr(FileHelper, "_instance"):
                    FileHelper._instance = object.__new__(cls)
        return FileHelper._instance

    def _setDownloader(self, downloader):
        self.downloader = downloader

    def _setUploader(self, uploader):
        self.uploader = uploader

    def get(self, source):
        """ Get file from s3
        source: path of s3
        """
        return self.downloader(source)

    def save(self, source, destination):
        """ Save file to s3
        source: source file path
        destination: s3 save path
        """
        self.uploader(source, destination)

    def import_package(self, path):
        """ Import package by path
        path: package path
        """
        path = self.downloader(path)
        spec = importlib.util.spec_from_file_location('user_import_model', path)
        md = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(md)
        return md
