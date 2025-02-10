import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from mapie.regression import MapieRegressor
import joblib

def train_model():
    # Load data
    df = pd.read_csv('apartment_data.csv')
    
    # Prepare features
    le_floor = LabelEncoder()
    le_style = LabelEncoder()
    
    df['floor_material_encoded'] = le_floor.fit_transform(df['floor_material'])
    df['style_encoded'] = le_style.fit_transform(df['style'])
    
    # Save encoders
    joblib.dump(le_floor, 'le_floor.joblib')
    joblib.dump(le_style, 'le_style.joblib')
    
    # Prepare features and target
    features = ['rooms', 'bathrooms', 'total_surface', 'building_age', 
                'floor_material_encoded', 'style_encoded']
    X = df[features]
    y = df['monthly_rent']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train base model
    base_model = RandomForestRegressor(n_estimators=100, random_state=42)
    base_model.fit(X_train, y_train)
    
    # Train conformal predictor
    mapie = MapieRegressor(
        estimator=base_model,
        method="plus",  # Using the plus method for prediction intervals
        cv="prefit",
        random_state=42
    )
    
    # Fit MAPIE
    mapie.fit(X_train, y_train)
    
    # Get predictions with confidence intervals
    y_pred, y_pis = mapie.predict(X_test, alpha=0.05)  # 95% confidence interval
    
    # Evaluate model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Calculate prediction interval coverage
    coverage = np.mean((y_test >= y_pis[:, 0, 0]) & (y_test <= y_pis[:, 1, 0]))
    
    print(f"Mean Squared Error: {mse}")
    print(f"R2 Score: {r2}")
    print(f"Empirical coverage: {coverage:.3f}")
    
    # Save models
    joblib.dump(base_model, 'rent_model.joblib')
    joblib.dump(mapie, 'conformal_model.joblib')
    
if __name__ == "__main__":
    train_model()
