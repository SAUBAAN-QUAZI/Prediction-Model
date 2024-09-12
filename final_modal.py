# Required Libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from lightgbm import LGBMRegressor
from sklearn.preprocessing import LabelEncoder
import warnings

# To Suppress continous LightGBM warnings
warnings.filterwarnings('ignore', category=UserWarning, module='lightgbm')


# Loading the dataset
file_path = 'diamond.csv'  # Use the appropriate path
data = pd.read_csv(file_path)

# Preprocessing: Encode categorical variables (cut, color, clarity)
for col in ['cut', 'color', 'clarity']:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])

# Splitting data into features (X) and target (y)
X = data.drop('price', axis=1)
y = data['price']

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#  Train the Gradient Boosting Regressor
print("Training Gradient Boosting model...")
gbr_params = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 3,
    'random_state': 42
}

gbr_model = GradientBoostingRegressor(**gbr_params)
gbr_model.fit(X_train, y_train)

#  Getting predictions from Gradient Boosting model
gbr_predictions = gbr_model.predict(X_train)

# Calculating difference between actual and predicted values
residuals = y_train - gbr_predictions

#  Training the LightGBM model on difference
print("Training LightGBM model on residuals...")
lgb_params = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 6,
    'min_data_in_leaf': 20,
    'random_state': 42,
    'verbosity': -1  # Suppresses continous warnings
}

lgb_model = LGBMRegressor(**lgb_params)
lgb_model.fit(X_train, residuals)


# Final prediction - Gradient Boosting predictions + LightGBM corrections
# Applying Gradient Boosting to test data
gbr_test_predictions = gbr_model.predict(X_test)

# Using LightGBM to predict difference for test data and correct the final output
lgb_test_residuals = lgb_model.predict(X_test)

# Combining both predictions
final_predictions = gbr_test_predictions + lgb_test_residuals

# Evaluating the combined model
mae = mean_absolute_error(y_test, final_predictions)
mse = mean_squared_error(y_test, final_predictions)
r2 = r2_score(y_test, final_predictions)

print("\n### Combined Gradient Boosting + LightGBM Model Performance ###")
print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"R-Squared: {r2}")
