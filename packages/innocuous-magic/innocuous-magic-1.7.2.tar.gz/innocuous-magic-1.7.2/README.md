# magic
Experiment with any imaginable function using our Magic Object

## innocuous.MagicObj  
- [how to import package](#import-package)
- [get_dataset_path](#get_dataset_path)
- [get_model_path](#get_model_path)
- ~~[get_path](#get_path)~~
- [load_keras_model](#load_keras_model)
- [load_pytorch_model](#load_pytorch_model)
- [log](#log)
- [torch_save](#torch_save)
- [callback](#callback)

## innocuous.Endpoint
- [how to import package](#import-package-2)
- [download](#download)
- [save](#save)
- [ModelLoader](#ModelLoader)
    - checkpoint_path
    - update_model
    - save_model
    - get_model
    - save_config
    - get_config
- [PipelineHelper](#PipelineHelper)
    - get_last_metric
    - get_metric
    - update_last_metric
- [FileHelper](#FileHelper)
    - get
    - save
    - import_package
---

## innocuous.MagicObj  

### <span id=import-package> import package </span>
```python
from innocuous.MagicObj import MagicObj
...
mj = MagicObj()
...
```

### <span id=get_dataset_path> get_dataset_path() -> str: </span>
> At Experiment (function mode), get path of dataset.
```python
def main(epoch=5, lr=0.001):
    dataset_path = mj.get_dataset_path()
    train_path = os.path.join(dataset_path, 'train')
    val_path = os.path.join(dataset_path, 'val')
```

### <span id=get_model_path> get_model_path() -> str: </span>
> At Experiment (function mode), get path of model.
```python
def main(epoch=5, lr=0.001):
    ...
    model_path = mj.get_model_path()
    # Keras
    model = load_model(model_path)
    # Pytorch
    model = Model()
    model.load_state_dict(torch.load(model_path))
    ... 
```

### <span id=load_keras_model> load_keras_model(model_class) </span>
> At Experiment (function mode) or TrainPipeline, auto load keras model
```python
def main(epoch=5, lr=0.001):
    model = Sequential()
    model.add(Conv2D(...)
    model.add(Flatten())
    ...
    model.compile(...)
    ...
    model = mj.load_keras_model(model)
    ...
```

### <span id=load_pytorch_model> load_pytorch_model(model_class) </span>
> At Experiment (function mode) or TrainPipeline, auto load pytorch model
```python
class Model:
    def __init__(self):
        super(Model, self).__init__()
        ...

    def forward(self, x):
        ...

def main(epoch=5, lr=0.001):
    ...
    model = mj.load_pytorch_model(Model())
    ...
```

### <span id=log> log(mertic) </span>
> At Experiment (function mode) or TrainPipeline, report metrics
```python
def main(epoch=5, lr=0.001):
    ...

    for epoch in range(epochs):
        ...

        mj.log(accuracy=eval_acc/len(val_data), loss=eval_loss/len(val_data))
```

### <span id=torch_save> torch_save(checkpoint, path, epoch) </span>
> At Experiment (function mode) or TrainPipeline, save pytorch checkpoint
```python
def main(epoch=5, lr=0.001):
    ...

    for epoch in range(epochs):
        ...
        checkpoint = model.state_dict()
        ...
        mj.torch_save(
            checkpoint=checkpoint,               # checkpoint
            path='/home/user/workspace/results', # At Cloud IDE, save in local path
            epoch=epoch                          # Now epoch number
        )
        mj.log(accuracy=eval_acc/len(val_data), loss=eval_loss/len(val_data))
```

### <span id=callback> callback(mertic, filename, path, frequency, on) </span>
> At Experiment (function mode) or TrainPipeline, save keras checkpoint
```python
def main(epoch=5, lr=0.001):
    ...

    model.fit(
        train_generator, 
        epochs=epochs, 
        batch_size=batch_size, 
        verbose=1, 
        validation_data=validation_generator,
        callbacks=[mj.callback(
            metrics={"accuracy":"accuracy"},    
            filename="checkpoint.h5",
            path="/home/user/workspace/results",
            frequency=1,
            on="epoch_end")]
        )
```
---

## innocuous.Endpoint

### <span id=import-package-2> import package </span>
```python
import innocuous.Endpoint as endpoint
```

### <span id=download> download(urls: list(str)) -> list(str): </span>
> At endpoint, download predict files
```python
def predict(data):
    # data = {
    #   "images": [
    #       "http://example.com/example_1.jpg",
    #       "http://example.com/example_2.jpg",
    #       "http://example.com/example_3.jpg"
    #   ]
    # }
    ...
    # files is path of endpoint local path 
    # ["/tmp/xx/oo/example_1.jpg","/tmp/xx/oo/example_2.jpg","/tmp/xx/oo/example_3.jpg"])
    files = endpoint.download(data['images'])
    ...
```

### <span id=save> save(files: list(file)) -> list(str): </span>
> At endpoint, save predict files
```python
def predict_file(files):
    # files is path of endpoint local path 
    # ["/tmp/xx/oo/example_1.jpg","/tmp/xx/oo/example_2.jpg","/tmp/xx/oo/example_3.jpg"])
    files = endpoint.save(files)
    ...
```

---

## <span id=ModelLoader> ModelLoader </span>
```python
modelLoader = endpoint.ModelLoader()
```

### checkpoint_path
> get checkpoint path from Web setting
```python
path = modelLoader.checkpoint_path
```

### update_model(model: **object**):
> update modelloader model
```python
modelLoader.update_model(model)
```

### save_new_checkpoint_path():
> download new model to local
```python
modelLoader.save_new_checkpoint_path()
```

### get_model() -> **object**:
> get model from modelloader
```python
model = modelLoader.get_model()
```

### save_config(config: **object**):
> save config
```python
modelLoader.save_config(config)
```

### get_config() -> **object**:
> get config
```python
modelLoader.get_config()
```

### Example
```python
# Keras
def load_model():
    model = keras.models.load_model(modelLoader.path)
    modelLoader.update_model(model) # update model

# Pytorch
def load_model():
    model = Model()
    model.load_state_dict(torch.load(modelLoader.checkpoint_path))
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    modelLoader.update_model(model) # update model

# Common
def predict(data):
    model = modelLoader.get_model() # get model
    config = modelLoader.get_config() # get config
    ...

# Common
def on_train_completed(metric, config, new_model_path):
    ...
    modelLoader.save_new_checkpoint_path(new_model_path)  # Save model
    modelLoader.save_config(config)         # Save config
    ...
```

## <span id=PipelineHelper> PipelineHelper </span>
> At endpoint, save metric
```python
pipelineHelper = endpoint.PipelineHelper()
```

### get_last_metric() -> **float**:
> get last metric
```python
pipelineHelper.get_last_metric()
```

### get_metric(index=None: **float**) -> list(**float**):
> get metric list or one
```python
pipelineHelper.get_metric()
```

### update_last_metric(metric: **float**):
> update metric
```python
pipelineHelper.update_last_metric(1.2345)
```

### Example
```python
def on_train_completed(metric, config, new_model_path):
    if metric > pipelineHelper.get_last_metric():     # if new metirc better last
        pipelineHelper.update_last_metric(metric)    # update now metric
    print(pipelineHelper.getmetric())                # show all metric e.g. [0.1, 0.2]
    print(pipelineHelper.getlast_metric())           # show last metric e.g. 0.2
```

## <span id=FileHelper> FileHelper </span>
> At endpoint, save metric
```python
fileHelper = endpoint.FileHelper()
```

### get(source: **str**) -> **str**:
> download file from s3 to local
```python
fileHelper.get("data://xxx/ooo/config.json")
```

### save(source: **str**, destination: **str**):
> save file from local to s3
```python
fileHelper.save("local_file_path.json", "data://xxx/ooo/config.json")
```

### import_package(path: **str**) -> **module**:
> import module from path
```python
fileHelper.import_package("local/path/model.py")
```
