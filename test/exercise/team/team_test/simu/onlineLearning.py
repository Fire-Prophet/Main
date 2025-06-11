from sklearn.linear_model import SGDClassifier

model = SGDClassifier(loss='log')
# 반복적으로 사용: model.partial_fit(X_batch, y_batch, classes=[0,1,2,3])
