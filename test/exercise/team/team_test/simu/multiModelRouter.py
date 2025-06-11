def choose_model(input):
    if input['wind'] > 5:
        return 'models/fire_model_windy.pkl'
    else:
        return 'models/fire_model_calm.pkl'
