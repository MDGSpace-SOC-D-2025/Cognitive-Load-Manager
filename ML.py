import pandas as pd
from sklearn.tree import DecisionTreeRegressor
import joblib



synthetic_data_file_path=r"C:\Users\ryapa\OneDrive\Desktop\CLM\training_data.csv"
predicting_data=pd.read_csv(synthetic_data_file_path)
# print(predicting_data.describe())

y=predicting_data.cognitive_load

predicting_features=['sleep_hours', 'fatigue_level', 'assignments_due', 'avg_deadline_days', 'study_hours']

x=predicting_data[predicting_features]
# print(x.describe())

# predicting_model=DecisionTreeRegressor(random_state=1)
# predicting_model.fit(x,y)

# print("Making predictions for the following:")
# print(x.head())
# print("The predictions are")
# print(predicting_model.predict(x.head()))

predicting_model=DecisionTreeRegressor()
predicting_model.fit(x,y)

joblib.dump(predicting_model, "cognitive_load_model.pkl")