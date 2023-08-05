import threading
import os
import json
import subprocess
import errno
import logging
from colorlog import ColoredFormatter
from collections import OrderedDict
from ray import tune
from lazy_import import lazy_callable, lazy_module
torch = lazy_module('torch')
TuneReportCheckpointCallback = lazy_callable('ray.tune.integration.keras.TuneReportCheckpointCallback')
ModelCheckpoint = lazy_callable('tensorflow.keras.callbacks.ModelCheckpoint')
Sequential = lazy_callable('tensorflow.keras.Sequential')

LOG_LEVEL = logging.DEBUG
datefmt = '%Y-%m-%d %H:%M:%S'
LOGFORMAT = "%(log_color)s[%(asctime)s][%(levelname)-8s]%(reset)s %(log_color)s%(message)s%(reset)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT, datefmt)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('Magic')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)

class MagicObj(object):
    __instance_lock = threading.Lock()
    __param_path = '/tmp/innocuous/.magic.json'
    __user = None
    __download_file_path = None
    __checkpoint_path = None
    __storage_type = None
    __bucket = None
    __blob = None
    __isDev = None
    __isPipeline = None
    __metric = None
    __cp_count = 0

    def __init__(self):
        self.__load_param()

    def __new__(cls, *args, **kwargs):
        if not hasattr(MagicObj, "_instance"):
            with MagicObj.__instance_lock:
                if not hasattr(MagicObj, "_instance"):
                    MagicObj._instance = object.__new__(cls)
        return MagicObj._instance

    def __load_param(self):
        if not os.path.isfile(self.__param_path):
            subprocess.run(f"mkdir -p {os.path.split(self.__param_path)[0]}", shell=True)	
            subprocess.run(f"touch {self.__param_path}", shell=True)
            self.__isDev = True
        elif os.path.getsize(self.__param_path) == 0:
            self.__isDev = True
        else:
            with open(self.__param_path, 'r') as f:
                obj = json.load(f)
                self.__download_file_path = obj['DATASET_NAME']
                log.info('Dataset loading path is now: ' + self.__download_file_path)
                log.info('New dataset path defined as')
                self.__user = obj['USER_ID']
                if 'CHECKPOINT_PATH' in obj:
                    self.__checkpoint_path = obj['CHECKPOINT_PATH']
                if 'METRIC' in obj:
                    self.__metric = obj['METRIC']

                if obj['STORAGE_TYPE'] == 'S3':
                    import boto3
                    s3 = boto3.resource('s3', 
                        aws_access_key_id=obj['AWS_KEY'], 
                        aws_secret_access_key=obj['AWS_SECRET'])
                    self.__bucket = s3.Bucket(obj['S3_BUCKET_NAME'])
       
                elif obj['STORAGE_TYPE'] == 'Azure':
                    from azure.storage.blob import BlobServiceClient
                    conn = f'DefaultEndpointsProtocol=https;AccountName={obj["AZURE_STORAGE_ACCOUNT_NAME"]};AccountKey={obj["AZURE_STORAGE_ACCOUNT_KEY"]};EndpointSuffix=core.windows.net'
                    blob_service_client = BlobServiceClient.from_connection_string(conn)
                    self.__blob = blob_service_client.get_container_client(obj["AZURE_STORAGE_CONTAINER"])

                self.__storage_type = obj['STORAGE_TYPE']
                
                self.__isDev = False if obj['RUN_ENV'] == 'POD' else True
                self.__isPipeline = True if obj['TRAIN_MODE'] == 'PIPELINE' else False

    def __is_dev_env(self):
        return self.__isDev

    def __is_pipeline(self):
        return self.__isPipeline

    def __download_file(self, filename):
        print(f'Download file: {filename}')        
        _ , name = os.path.split(filename)
        save_path = os.path.join(self.__download_file_path, name)
        if self.__storage_type == 'S3':
            self.__bucket.download_file(f'Users/{self.__user}/dataset/{name}', save_path)
        elif self.__storage_type == 'Azure':
            with open(save_path, "wb") as data:
                blob_data = self.__blob.download_blob(f'Users/{self.__user}/dataset/{name}')
                blob_data.readinto(data)
        return save_path
    
    #will depricate
    def get_dataset_path(self):
        return self.__download_file_path

    def get_checkpoint_path(self):
        return self.__checkpoint_path

    def get_path(self, filename):
        if self.__is_dev_env():
            return filename
        else:
            if not os.path.exists(self.__download_file_path):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.__download_file_path)
            return self.__download_file_path

    def is_training_pipeline(self):
        return self.__is_pipeline()

    def load_keras_model(self, model_class):
        if self.__is_pipeline():
            from keras.models import load_model
            return load_model(self.__checkpoint_path)
        else:
            return model_class

    def load_pytorch_model(self, model_class):
        if self.__is_pipeline():
            import torch
            model_class.load_state_dict(torch.load(self.__checkpoint_path)) 
            return model_class
        else:
            return model_class

    def log(self, *args, **kwargs):
        if args:
            raise ValueError("only use keyword-only arguments")
        kwargs_str = ','.join('{}={}'.format(k, v) for k, v in kwargs.items())
        if self.__is_dev_env():
            print(f"We are logging the following metrics: {kwargs_str}")
            return
        tune.report(**kwargs if kwargs else None)

    def torch_get_checkpoint_path(self, path, epoch):
        """
        epoch: iteration of loop(int).  
        path: path to save checkpoints or models from each epoch(str)
        """
        if type(path) != str:
            raise TypeError("`path` expected str, bytes or os.PathLike object")
        if path[-1] == "/":
            raise ValueError("The end of `path` shouldn't be '/'")
        if type(epoch) != int:
            raise TypeError("`epoch` expected int")
        if self.__is_dev_env():
            whole_path = os.path.join(path, "checkpoint")
            return whole_path
        with tune.checkpoint_dir(step=epoch) as checkpoint_dir:
            whole_path = os.path.join(checkpoint_dir, "checkpoint")
        return whole_path

    def _tensorflow_get_checkpoint_path(self, path, filename):
        """
        path: path to save checkpoints or models from each epoch(str).
        """
        if type(path) != str:
            raise TypeError("`path` expected str, bytes or os.PathLike object")
        if type(filename) != str:
            raise TypeError("`filename` expected str, bytes or os.PathLike object")
        if path[-1] == "/":
            raise ValueError("The end of `path` shouldn't be '/'")
        if self.__is_dev_env():
            whole_path = os.path.join(path, filename, f"checkpoint_{str(self.__cp_count)}")
            self.__cp_count += 1
            return whole_path
        with tune.checkpoint_dir(step=self.__cp_count) as checkpoint_dir:
            whole_path = os.path.join(checkpoint_dir, "checkpoint")
            self.__cp_count += 1
        return whole_path

    def torch_save(self, checkpoint, path, epoch):
        """
        checkpoint: checkpoints to save (dict|OrderDict).  
        path: path to save checkpoints or models from each epoch(str).  
        epoch: iteration of loop.  
        """
        if type(checkpoint) != dict and type(checkpoint) != OrderedDict:
            raise TypeError("`checkpoint` expected dictionary or collections.OrderDict object")
        if type(path) != str:
            raise TypeError("`path` expected str, bytes or os.PathLike object")
        if path[-1] == "/":
            raise ValueError("The end of `path` shouldn't be '/'")
        if type(epoch) != int:
            raise TypeError("`epoch` expected int")
        if self.__is_dev_env():
            whole_path = os.path.join(path, "checkpoint.pt")
            torch.save(checkpoint, whole_path)
            return
        with tune.checkpoint_dir(step=epoch) as checkpoint_dir:
            whole_path = os.path.join(checkpoint_dir, "checkpoint.pt")
            torch.save(checkpoint, whole_path)

    def tensorflow_save(self, checkpoint, path, epoch):
        """
        checkpoint: model of each epoch (Sequential)
        save_path: path to save checkpoints or models from each epoch (str)
        epoch: iteration of loop
        """
        if type(checkpoint) != Sequential:
            raise TypeError("`checkpoint` expected Sequential object")
        if type(path) != str:
            raise TypeError("`path` expected str, bytes or os.PathLike object")
        if path[-1] == "/":
            raise ValueError("The end of `path` shouldn't be '/'")
        if type(epoch) != int:
            raise TypeError("`epoch` expected int")
        if self.__is_dev_env():
            whole_path = os.path.join(path, "checkpoint")
            checkpoint.save_weights(whole_path)
            return
        with tune.checkpoint_dir(step=epoch) as checkpoint_dir:
            whole_path = os.path.join(checkpoint_dir, "checkpoint")
            checkpoint.save_weights(whole_path)

    def callback(self, metrics, path, frequency=1, on="epoch_end", filename=None):
        """
        metrics (str|list|dict): Metrics to report to Tune, which is from `log`.  
        frequency (int|list): Checkpoint frequency. If this is an integer `n`,
            checkpoints are saved every `n` times each hook was called. If
            this is a list, it specifies the checkpoint frequencies for each
            hook individually.
        on (str|list): When to trigger checkpoint creations. Must be one of
            the Keras event hooks (less the ``on_``), e.g.
            "train_start", or "predict_end". Defaults to "epoch_end".
        """
        if type(metrics) != str and type(metrics) != list and type(metrics) != dict:
            raise TypeError("`checkpoint` expected string, list or dictionary")
        if type(path) != str:
            raise TypeError("`path` expected str, bytes or os.PathLike object")
        if path[-1] == "/":
            raise ValueError("The end of `path` shouldn't be '/'")
        if self.__is_dev_env():
            self.log(**metrics)
            save_path = self._tensorflow_get_checkpoint_path(path, filename)
            return ModelCheckpoint(filepath=save_path)
        return TuneReportCheckpointCallback(
            metrics=metrics,
            filename="checkpoint.h5",
            frequency=frequency,
            on=on)
