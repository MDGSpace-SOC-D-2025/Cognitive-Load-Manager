import xgboost

import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from xgboost import XGBRegressor
import joblib
from numpy import absolute



synthetic_data_file_path=r"C:\Users\ryapa\OneDrive\Desktop\CLM\training_data.csv"
predicting_data=pd.read_csv(synthetic_data_file_path)

# print(predicting_data.shape)
# print(predicting_data.head())

y=predicting_data.cognitive_load
predicting_features=['sleep_hours', 'fatigue_level', 'assignments_due', 'avg_deadline_days', 'study_hours']
x=predicting_data[predicting_features]
model=XGBRegressor()
cv=RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
scores = cross_val_score(model, x, y, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)
# force scores to be positive
scores = absolute(scores)
# print('Mean MAE: %.3f (%.3f)' % (scores.mean(), scores.std()) )


model.fit(x,y)

joblib.dump(model, "cognitive_model.pkl")