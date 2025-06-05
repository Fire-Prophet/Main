import pickle

_model_cache = {}

def load_model(path):
    if path not in _model_cache:
        with open(path, 'rb') as f:
            _model_cache[path] = pickle.load(f)
    return _model_cache[path]
