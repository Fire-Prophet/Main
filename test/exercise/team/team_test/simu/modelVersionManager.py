import os
import pickle

def get_latest_model():
    models = sorted(os.listdir('models'))
    latest = models[-1]
    return pickle.load(open(f'models/{latest}', 'rb'))
