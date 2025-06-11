import matplotlib.pyplot as plt
import pickle

model = pickle.load(open('models/fire_model_latest.pkl', 'rb'))
features = ['temp', 'humidity', 'wind']
importances = model.feature_importances_

plt.bar(features, importances)
plt.title('Feature Importance')
plt.savefig('outputs/feature_importance.png')
