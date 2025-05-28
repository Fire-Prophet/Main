"""
Machine Learning Integration and Predictive Models for Fire Simulation
Provides ML-based fire behavior prediction, parameter optimization, and automated analysis.
"""

# This script integrates machine learning models for fire behavior prediction.

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import json
import pickle
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


@dataclass
class ModelMetrics:
    """Model performance metrics."""
    mse: float
    rmse: float
    mae: float
    r2: float
    cross_val_score: float
    training_time: float
    prediction_time: float


@dataclass
class PredictionResult:
    """Fire behavior prediction result."""
    burned_area: float
    fire_intensity: float
    spread_rate: float
    containment_time: float
    confidence_interval: Tuple[float, float]
    feature_importance: Dict[str, float]
    model_used: str


class DataProcessor:
    """Processes simulation data for ML training."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.target_columns = []
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML training."""
        processed_data = data.copy()
        
        # Handle categorical variables
        categorical_cols = processed_data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                processed_data[col] = self.label_encoders[col].fit_transform(processed_data[col])
            else:
                processed_data[col] = self.label_encoders[col].transform(processed_data[col])
        
        # Create derived features
        processed_data = self._create_derived_features(processed_data)
        
        # Handle missing values
        processed_data = processed_data.fillna(processed_data.mean())
        
        return processed_data
    
    def _create_derived_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create derived features from raw data."""
        derived_data = data.copy()
        
        # Wind-related features
        if 'wind_speed' in data.columns and 'wind_direction' in data.columns:
            derived_data['wind_x'] = data['wind_speed'] * np.cos(np.radians(data['wind_direction']))
            derived_data['wind_y'] = data['wind_speed'] * np.sin(np.radians(data['wind_direction']))
        
        # Fuel moisture features
        if 'fuel_moisture' in data.columns:
            derived_data['fuel_dryness'] = 1 - data['fuel_moisture']
            derived_data['fire_risk'] = derived_data['fuel_dryness'] * data.get('temperature', 25) / 25
        
        # Topographic features
        if 'elevation' in data.columns:
            derived_data['elevation_normalized'] = (data['elevation'] - data['elevation'].min()) / (data['elevation'].max() - data['elevation'].min())
        
        if 'slope' in data.columns:
            derived_data['slope_radians'] = np.radians(data['slope'])
            derived_data['slope_factor'] = np.sin(derived_data['slope_radians'])
        
        # Weather interactions
        if all(col in data.columns for col in ['temperature', 'humidity']):
            derived_data['heat_index'] = data['temperature'] + 0.5 * (data['humidity'] - 50)
            derived_data['drought_index'] = data['temperature'] / (data['humidity'] + 1)
        
        return derived_data
    
    def split_features_targets(self, data: pd.DataFrame, target_cols: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data into features and targets."""
        features = data.drop(columns=target_cols)
        targets = data[target_cols]
        
        self.feature_columns = features.columns.tolist()
        self.target_columns = target_cols
        
        return features, targets
    
    def scale_features(self, features: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Scale features for ML models."""
        if fit:
            scaled_features = self.scaler.fit_transform(features)
        else:
            scaled_features = self.scaler.transform(features)
        
        return pd.DataFrame(scaled_features, columns=features.columns, index=features.index)


class FireBehaviorPredictor:
    """ML-based fire behavior prediction system."""
    
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
        }
        self.best_model = None
        self.best_model_name = None
        self.data_processor = DataProcessor()
        self.model_metrics = {}
        self.logger = logging.getLogger(__name__)
    
    def train_models(self, training_data: pd.DataFrame, target_columns: List[str]) -> Dict[str, ModelMetrics]:
        """Train multiple ML models and select the best one."""
        # Prepare data
        processed_data = self.data_processor.prepare_features(training_data)
        features, targets = self.data_processor.split_features_targets(processed_data, target_columns)
        
        # Scale features
        scaled_features = self.data_processor.scale_features(features, fit=True)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            scaled_features, targets, test_size=0.2, random_state=42
        )
        
        best_score = -np.inf
        
        for model_name, model in self.models.items():
            self.logger.info(f"Training {model_name}...")
            
            start_time = datetime.now()
            
            # Train model
            if len(target_columns) == 1:
                model.fit(X_train, y_train.iloc[:, 0])
                y_pred = model.predict(X_test)
                y_true = y_test.iloc[:, 0]
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_true = y_test
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Evaluate model
            pred_start = datetime.now()
            if len(target_columns) == 1:
                test_pred = model.predict(X_test)
            else:
                test_pred = model.predict(X_test)
            prediction_time = (datetime.now() - pred_start).total_seconds()
            
            # Calculate metrics
            if len(target_columns) == 1:
                mse = mean_squared_error(y_true, y_pred)
                r2 = r2_score(y_true, y_pred)
                mae = mean_absolute_error(y_true, y_pred)
                cv_score = cross_val_score(model, X_train, y_train.iloc[:, 0], cv=5).mean()
            else:
                mse = mean_squared_error(y_true, y_pred)
                r2 = r2_score(y_true, y_pred)
                mae = mean_absolute_error(y_true, y_pred)
                cv_score = cross_val_score(model, X_train, y_train, cv=5).mean()
            
            metrics = ModelMetrics(
                mse=mse,
                rmse=np.sqrt(mse),
                mae=mae,
                r2=r2,
                cross_val_score=cv_score,
                training_time=training_time,
                prediction_time=prediction_time
            )
            
            self.model_metrics[model_name] = metrics
            
            # Check if this is the best model
            if r2 > best_score:
                best_score = r2
                self.best_model = model
                self.best_model_name = model_name
            
            self.logger.info(f"{model_name} - R²: {r2:.4f}, RMSE: {np.sqrt(mse):.4f}")
        
        self.logger.info(f"Best model: {self.best_model_name} (R²: {best_score:.4f})")
        return self.model_metrics
    
    def predict_fire_behavior(self, input_data: Dict[str, Any]) -> PredictionResult:
        """Predict fire behavior from input parameters."""
        if self.best_model is None:
            raise ValueError("No trained model available. Please train models first.")
        
        # Convert input to DataFrame
        input_df = pd.DataFrame([input_data])
        
        # Process features
        processed_input = self.data_processor.prepare_features(input_df)
        scaled_input = self.data_processor.scale_features(processed_input, fit=False)
        
        # Make prediction
        prediction = self.best_model.predict(scaled_input)
        
        # Calculate confidence interval (simplified)
        if hasattr(self.best_model, 'estimators_'):
            # For ensemble methods, use prediction variance
            predictions = np.array([estimator.predict(scaled_input) for estimator in self.best_model.estimators_])
            confidence_interval = (
                np.percentile(predictions, 25, axis=0)[0],
                np.percentile(predictions, 75, axis=0)[0]
            )
        else:
            # Simplified confidence interval
            std_error = 0.1 * np.abs(prediction[0])
            confidence_interval = (prediction[0] - std_error, prediction[0] + std_error)
        
        # Get feature importance
        feature_importance = {}
        if hasattr(self.best_model, 'feature_importances_'):
            for feature, importance in zip(self.data_processor.feature_columns, self.best_model.feature_importances_):
                feature_importance[feature] = float(importance)
        
        # Create prediction result
        if len(prediction[0]) >= 4:
            result = PredictionResult(
                burned_area=float(prediction[0][0]),
                fire_intensity=float(prediction[0][1]),
                spread_rate=float(prediction[0][2]),
                containment_time=float(prediction[0][3]),
                confidence_interval=confidence_interval,
                feature_importance=feature_importance,
                model_used=self.best_model_name
            )
        else:
            # Single target prediction
            result = PredictionResult(
                burned_area=float(prediction[0]),
                fire_intensity=0.0,
                spread_rate=0.0,
                containment_time=0.0,
                confidence_interval=confidence_interval,
                feature_importance=feature_importance,
                model_used=self.best_model_name
            )
        
        return result
    
    def optimize_parameters(self, target_outcome: Dict[str, float], parameter_ranges: Dict[str, Tuple[float, float]], 
                          num_iterations: int = 100) -> Dict[str, float]:
        """Find optimal parameters to achieve target outcomes."""
        from scipy.optimize import minimize
        
        def objective_function(params):
            # Convert parameter array to dictionary
            param_dict = {}
            for i, (param_name, _) in enumerate(parameter_ranges.items()):
                param_dict[param_name] = params[i]
            
            # Predict outcomes
            try:
                prediction = self.predict_fire_behavior(param_dict)
                
                # Calculate difference from target
                diff = 0
                if 'burned_area' in target_outcome:
                    diff += (prediction.burned_area - target_outcome['burned_area']) ** 2
                if 'fire_intensity' in target_outcome:
                    diff += (prediction.fire_intensity - target_outcome['fire_intensity']) ** 2
                if 'spread_rate' in target_outcome:
                    diff += (prediction.spread_rate - target_outcome['spread_rate']) ** 2
                if 'containment_time' in target_outcome:
                    diff += (prediction.containment_time - target_outcome['containment_time']) ** 2
                
                return diff
            except:
                return 1e6  # Large penalty for invalid parameters
        
        # Set up optimization bounds
        bounds = [(min_val, max_val) for min_val, max_val in parameter_ranges.values()]
        
        # Initial guess (middle of ranges)
        initial_guess = [(min_val + max_val) / 2 for min_val, max_val in parameter_ranges.values()]
        
        # Optimize
        result = minimize(objective_function, initial_guess, bounds=bounds, method='L-BFGS-B')
        
        # Convert result back to parameter dictionary
        optimal_params = {}
        for i, (param_name, _) in enumerate(parameter_ranges.items()):
            optimal_params[param_name] = result.x[i]
        
        return optimal_params
    
    def save_model(self, filepath: str) -> None:
        """Save trained model and preprocessor."""
        model_data = {
            'best_model': self.best_model,
            'best_model_name': self.best_model_name,
            'data_processor': self.data_processor,
            'model_metrics': self.model_metrics,
            'feature_columns': self.data_processor.feature_columns,
            'target_columns': self.data_processor.target_columns
        }
        
        joblib.dump(model_data, filepath)
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load trained model and preprocessor."""
        model_data = joblib.load(filepath)
        
        self.best_model = model_data['best_model']
        self.best_model_name = model_data['best_model_name']
        self.data_processor = model_data['data_processor']
        self.model_metrics = model_data['model_metrics']
        
        self.logger.info(f"Model loaded from {filepath}")


class AutoMLFirePredictor:
    """Automated ML pipeline for fire prediction."""
    
    def __init__(self):
        self.predictor = FireBehaviorPredictor()
        self.training_history = []
        
    def auto_train(self, data_sources: List[str], target_columns: List[str]) -> Dict[str, Any]:
        """Automatically train models from multiple data sources."""
        # Combine data from multiple sources
        combined_data = pd.DataFrame()
        
        for source in data_sources:
            if source.endswith('.csv'):
                data = pd.read_csv(source)
            elif source.endswith('.json'):
                data = pd.read_json(source)
            else:
                continue
            
            combined_data = pd.concat([combined_data, data], ignore_index=True)
        
        # Remove duplicates and clean data
        combined_data = combined_data.drop_duplicates()
        combined_data = combined_data.dropna(subset=target_columns)
        
        # Train models
        metrics = self.predictor.train_models(combined_data, target_columns)
        
        # Store training history
        training_record = {
            'timestamp': datetime.now().isoformat(),
            'data_size': len(combined_data),
            'features': len(combined_data.columns) - len(target_columns),
            'best_model': self.predictor.best_model_name,
            'best_r2': max(m.r2 for m in metrics.values()),
            'metrics': {name: asdict(metric) for name, metric in metrics.items()}
        }
        self.training_history.append(training_record)
        
        return training_record
    
    def generate_synthetic_data(self, num_samples: int = 1000) -> pd.DataFrame:
        """Generate synthetic training data for demonstration."""
        np.random.seed(42)
        
        # Generate random parameters
        data = {
            'grid_size': np.random.randint(50, 500, num_samples),
            'wind_speed': np.random.uniform(0, 30, num_samples),
            'wind_direction': np.random.uniform(0, 360, num_samples),
            'temperature': np.random.normal(25, 10, num_samples),
            'humidity': np.random.uniform(10, 90, num_samples),
            'fuel_moisture': np.random.uniform(0.05, 0.5, num_samples),
            'fuel_type': np.random.randint(1, 14, num_samples),
            'elevation': np.random.uniform(0, 3000, num_samples),
            'slope': np.random.uniform(0, 45, num_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate synthetic targets based on realistic relationships
        df['burned_area'] = (
            df['grid_size'] * 0.1 +
            df['wind_speed'] * 50 +
            (1 - df['fuel_moisture']) * 500 +
            df['temperature'] * 10 +
            (100 - df['humidity']) * 5 +
            np.random.normal(0, 100, num_samples)
        ).clip(0)
        
        df['fire_intensity'] = (
            df['wind_speed'] * 20 +
            (1 - df['fuel_moisture']) * 1000 +
            df['temperature'] * 30 +
            np.random.normal(0, 50, num_samples)
        ).clip(0)
        
        df['spread_rate'] = (
            df['wind_speed'] * 2 +
            (1 - df['fuel_moisture']) * 10 +
            np.sin(np.radians(df['slope'])) * 5 +
            np.random.normal(0, 2, num_samples)
        ).clip(0)
        
        df['containment_time'] = (
            1000 / (df['wind_speed'] + 1) +
            df['fuel_moisture'] * 500 +
            df['humidity'] * 5 +
            np.random.normal(0, 50, num_samples)
        ).clip(10)
        
        return df


def run_ml_demo():
    """Demonstrate ML capabilities."""
    print("Fire Simulation ML Demo")
    print("=" * 50)
    
    # Create predictor
    predictor = AutoMLFirePredictor()
    
    # Generate synthetic data
    print("Generating synthetic training data...")
    training_data = predictor.generate_synthetic_data(2000)
    print(f"Generated {len(training_data)} training samples")
    
    # Save training data
    training_data.to_csv('/tmp/fire_training_data.csv', index=False)
    
    # Train models
    print("\nTraining ML models...")
    target_columns = ['burned_area', 'fire_intensity', 'spread_rate', 'containment_time']
    training_result = predictor.auto_train(['/tmp/fire_training_data.csv'], target_columns)
    
    print(f"Best model: {training_result['best_model']}")
    print(f"Best R²: {training_result['best_r2']:.4f}")
    
    # Make predictions
    print("\nMaking predictions...")
    test_input = {
        'grid_size': 200,
        'wind_speed': 15.0,
        'wind_direction': 45.0,
        'temperature': 30.0,
        'humidity': 20.0,
        'fuel_moisture': 0.1,
        'fuel_type': 7,
        'elevation': 1000,
        'slope': 15.0
    }
    
    prediction = predictor.predictor.predict_fire_behavior(test_input)
    print(f"Predicted burned area: {prediction.burned_area:.2f}")
    print(f"Predicted fire intensity: {prediction.fire_intensity:.2f}")
    print(f"Predicted spread rate: {prediction.spread_rate:.2f}")
    print(f"Predicted containment time: {prediction.containment_time:.2f}")
    
    # Optimize parameters
    print("\nOptimizing parameters...")
    target_outcome = {'burned_area': 1000, 'containment_time': 300}
    parameter_ranges = {
        'wind_speed': (1.0, 10.0),
        'fuel_moisture': (0.2, 0.5),
        'humidity': (40.0, 80.0)
    }
    
    optimal_params = predictor.predictor.optimize_parameters(target_outcome, parameter_ranges)
    print("Optimal parameters for target outcome:")
    for param, value in optimal_params.items():
        print(f"  {param}: {value:.4f}")
    
    # Save model
    model_path = '/tmp/fire_prediction_model.pkl'
    predictor.predictor.save_model(model_path)
    print(f"\nModel saved to {model_path}")


if __name__ == "__main__":
    run_ml_demo()
