import time

from connexion import request

from paddlelabel_ml.model import models
from paddlelabel_ml.util import abort
from paddlelabel_ml.model.base.model import BaseModel

global loaded_models
global loading_models
loaded_models = {}
loading_models = set()


def isBackendUp():
    return True


def getAll():
    return [{"name": n} for n in models.keys()]


def getProgress():
    pass


def train(model_name):
    # print("train", model_name)
    load(model_name, reload=True)
    model = loaded_models[model_name]

    if model.training:
        abort(
            f"Model {model_name} is in training. Can't train this model till current train finishes.",
            500,
        )
    model.training = True
    try:
        model.train(data_dir=request.json["data_dir"])
    except Exception as e:
        raise e
    finally:
        model.training = False


def evaluate(model_name):
    pass


def getProgresss(model_name):
    pass


def predict(model_name):
    tic = time.time()
    if model_name not in loaded_models.keys():
        abort(f"Model {model_name} not loaded, call load endpoint first!", 500)
    if model_name in loading_models:
        abort(f"Model {model_name} is still loading, check back after 1 or 2 minutes!", 500)

    res = {"result": loaded_models[model_name].predict(request.json)}
    print(f"Inference took {time.time() - tic} s")
    return res


def load(model_name, reload=False):
    tic = time.time()
    params = request.json.get("init_params", {})

    # 1. backend has this model
    if model_name not in models.keys():
        abort(f"No model named {model_name}", 404)

    # 2. model is loading or loaded
    if model_name in loaded_models.keys():
        # 2.1 loading
        if model_name in loading_models:
            abort(f"Model {model_name} is still loading, check back after 1 or 2 minutes!", 500)
        # 2.2 loaded with same params
        if loaded_models[model_name].params == params:
            return f"Model {model_name} is already loaded", 200

    # 3. load model
    loading_models.add(model_name)
    loaded_models[model_name] = models[model_name](**params)
    loaded_models[model_name].params = params
    loading_models.remove(model_name)

    loaded_models[model_name].load_time = time.time()
    print(f"Load model {model_name} took {time.time() - tic} s")
    return f"Model {model_name} loaded", 200


def unload(model_name):
    if model_name not in models.keys():
        abort(f"No model named {model_name}", 404)
    if model_name in loaded_models.keys():
        del loaded_models[model_name]
        return f"Model {model_name} unloaded!"
    return f"Model {model_name} is not loaded!"
