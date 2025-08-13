import pickle
import os
from django.shortcuts import render
from django.contrib.auth.models import User
import numpy as np
from authenticate_user.views import login_required
from .models import PropertyPrediction

# Load all ML models from the models directory
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
MODEL_FILES = {
    'XGBoost': 'xgb_model_tree.pkl',
    'Decision Tree': 'DecisionTreeRegressor_tree.pkl',
    'LGBM': 'LGBMRegressor.pkl',
    'Random Forest': 'RandomForestRegressor_tree.pkl',
    'Linear Regression': 'LinearRegression.pkl',
    'Support Vector': 'SupportVectorRegressor.pkl'
}

# Define your feature schema - customize this based on your training data
FEATURE_SCHEMA = {
    'numeric_features': [
        'Title', 'Price (in rupees)', 'Bathroom', 'Balcony', 'Super Area'
    ],
    'categorical_features': {
        'Transaction': ['New Property', 'Other', 'Rent/Lease', 'Resale'],
        'location': [
            'agra', 'ahmadnagar', 'ahmedabad', 'allahabad', 'aurangabad', 'badlapur',
            'bangalore', 'belgaum', 'bhiwadi', 'bhiwandi', 'bhopal', 'bhubaneswar',
            'chandigarh', 'chennai', 'coimbatore', 'dehradun', 'durgapur', 'ernakulam',
            'faridabad', 'ghaziabad', 'goa', 'greater-noida', 'guntur', 'gurgaon',
            'guwahati', 'gwalior', 'haridwar', 'hyderabad', 'indore', 'jabalpur',
            'jaipur', 'jamshedpur', 'kanpur', 'karnal', 'kochi', 'kolkata',
            'lucknow', 'ludhiana', 'madurai', 'meerut', 'mohali', 'mumbai',
            'mysore', 'nagpur', 'nashik', 'navi-mumbai', 'new-delhi', 'noida',
            'palwal', 'panipat', 'patiala', 'patna', 'pondicherry', 'pune',
            'raipur', 'rajkot', 'salem', 'siliguri', 'sonipat', 'surat',
            'thane', 'thiruvananthapuram', 'tinsukia', 'tirupur', 'tirunelveli',
            'tirupati', 'udaipur', 'vadodara', 'varanasi', 'vijayawada',
            'visakhapatnam', 'warangal'
        ],
        'Furnishing': ['Furnished', 'Semi-Furnished', 'Unfurnished'],
        'facing': ['East', 'North', 'North - East', 'North - West', 'South', 'South - East', 'South - West', 'West']
    },
    'text_features': {
        # Features that have too many categories to list - user will type them
        'Floor': 'text',  # e.g., "1 out of 10", "Ground", etc.
        'overlooking': 'text',  # e.g., "Garden/Park", "Main Road", etc.
        'Society': 'text'  # e.g., "Ansal API Valley", etc.
    }
}

# Load expected feature names from model
def get_model_feature_names():
    """Get the feature names from the first available model"""
    try:
        for model in ML_MODELS.values():
            if model is not None and hasattr(model, 'feature_names_in_'):
                return model.feature_names_in_
        return None
    except:
        return None

def load_models():
    """Load all pickled ML models"""
    models = {}
    for model_name, filename in MODEL_FILES.items():
        try:
            model_path = os.path.join(MODELS_DIR, filename)
            with open(model_path, 'rb') as file:
                model = pickle.load(file)
            models[model_name] = model
            print(f"Successfully loaded {model_name} model")
        except FileNotFoundError:
            print(f"Model file not found: {filename}")
            models[model_name] = None
        except Exception as e:
            print(f"Error loading {model_name} model: {str(e)}")
            models[model_name] = None
    return models

def format_currency(amount):
    """Format currency amount in a readable way"""
    if amount >= 10000000:  # 1 crore or more
        crores = amount / 10000000
        return f"₹{crores:.2f} Crores"
    elif amount >= 100000:  # 1 lakh or more
        lakhs = amount / 100000
        return f"₹{lakhs:.2f} Lakhs"
    else:
        return f"₹{amount:,.2f}"

def manual_one_hot_encode(data_dict):
    """
    Manually perform one-hot encoding for categorical features to match the trained model
    """
    if not ML_MODELS or all(model is None for model in ML_MODELS.values()):
        raise ValueError("No models loaded")
    
    # Get expected feature names from the first available model
    expected_features = get_model_feature_names()
    if expected_features is None:
        raise ValueError("Could not get feature names from model")
    
    # Initialize feature vector with zeros
    feature_vector = np.zeros(len(expected_features))
    
    # Set numeric features
    for feature in FEATURE_SCHEMA['numeric_features']:
        if feature in expected_features:
            feature_idx = list(expected_features).index(feature)
            if feature in data_dict:
                try:
                    feature_vector[feature_idx] = float(data_dict[feature])
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid numeric value for {feature}: {data_dict[feature]}")
            else:
                raise ValueError(f"Missing required numeric feature: {feature}")
    
    # Set categorical features (dropdown selections)
    for cat_feature, possible_values in FEATURE_SCHEMA['categorical_features'].items():
        if cat_feature in data_dict:
            user_value = data_dict[cat_feature].strip()
            encoded_feature_name = f"{cat_feature}_{user_value}"
            if encoded_feature_name in expected_features:
                feature_idx = list(expected_features).index(encoded_feature_name)
                feature_vector[feature_idx] = 1.0
            else:
                print(f"Warning: Unknown value '{user_value}' for feature '{cat_feature}'")
        else:
            raise ValueError(f"Missing required categorical feature: {cat_feature}")
    
    # Set text features (user-typed values)
    for text_feature in FEATURE_SCHEMA['text_features'].keys():
        if text_feature in data_dict and data_dict[text_feature].strip():
            user_value = data_dict[text_feature].strip()
            encoded_feature_name = f"{text_feature}_{user_value}"
            if encoded_feature_name in expected_features:
                feature_idx = list(expected_features).index(encoded_feature_name)
                feature_vector[feature_idx] = 1.0
            else:
                print(f"Warning: Unknown value '{user_value}' for feature '{text_feature}' - skipping")
                # For text features, this is fine - just skip unknown values
        # Don't raise error for missing text features - they are optional
        elif text_feature not in ['Society']:  # Society is completely optional
            if text_feature not in data_dict or not data_dict[text_feature].strip():
                raise ValueError(f"Missing required text feature: {text_feature}")
    
    return feature_vector.reshape(1, -1)

def get_feature_names():
    """Get the ordered list of feature names for the model"""
    model_features = get_model_feature_names()
    if model_features is not None:
        return model_features
    
    # Fallback: construct feature names manually
    feature_names = []
    feature_names.extend(FEATURE_SCHEMA['numeric_features'])
    
    for cat_feature, possible_values in FEATURE_SCHEMA['categorical_features'].items():
        for value in possible_values:
            feature_names.append(f"{cat_feature}_{value}")
    
    return feature_names

# Load all models once when the module is imported
try:
    ML_MODELS = load_models()
except:
    ML_MODELS = {}

@login_required
def home(request):
    """Home page with a form for predictions"""
    context = {
        'feature_schema': FEATURE_SCHEMA,
        'expected_features': get_feature_names()
    }
    return render(request, 'ml_predictor/home.html', context)

@login_required
def predict_form(request):
    """Handle form-based predictions with manual one-hot encoding for all models"""
    if request.method == 'GET':
        return render(request, 'ml_predictor/home.html', {
            'feature_schema': FEATURE_SCHEMA,
            'expected_features': get_feature_names()
        })
    
    try:
        if not ML_MODELS or all(model is None for model in ML_MODELS.values()):
            return render(request, 'ml_predictor/home.html', {
                'error': 'No models loaded. Please ensure model files are in the models directory.',
                'feature_schema': FEATURE_SCHEMA,
                'expected_features': get_feature_names()
            })
        
        # Extract features from form data
        input_data = {}
        
        # Get numeric features
        for feature in FEATURE_SCHEMA['numeric_features']:
            value = request.POST.get(feature)
            if value:
                input_data[feature] = value
            else:
                return render(request, 'ml_predictor/home.html', {
                    'error': f'Missing value for numeric feature: {feature}',
                    'feature_schema': FEATURE_SCHEMA,
                    'expected_features': get_feature_names()
                })
        
        # Get categorical features
        for feature in FEATURE_SCHEMA['categorical_features'].keys():
            value = request.POST.get(feature)
            if value:
                input_data[feature] = value
            else:
                return render(request, 'ml_predictor/home.html', {
                    'error': f'Missing value for categorical feature: {feature}',
                    'feature_schema': FEATURE_SCHEMA,
                    'expected_features': get_feature_names()
                })
        
        # Get text features
        for feature in FEATURE_SCHEMA['text_features'].keys():
            value = request.POST.get(feature)
            if feature == 'Society':
                # Society is optional - only add if provided
                if value and value.strip():
                    input_data[feature] = value.strip()
            else:
                # Other text features are required
                if value and value.strip():
                    input_data[feature] = value.strip()
                else:
                    return render(request, 'ml_predictor/home.html', {
                        'error': f'Missing value for text feature: {feature}',
                        'feature_schema': FEATURE_SCHEMA,
                        'expected_features': get_feature_names()
                    })
        
        # Perform manual one-hot encoding
        encoded_features = manual_one_hot_encode(input_data)
        
        # Make predictions from all models
        predictions = {}
        formatted_predictions = {}
        model_info = {}  # This will store model names with their predictions
        
        for model_name, model in ML_MODELS.items():
            if model is not None:
                try:
                    prediction = model.predict(encoded_features)
                    prediction_value = float(prediction[0])
                    predictions[model_name] = prediction_value
                    formatted_predictions[model_name] = format_currency(prediction_value)
                    # Add model info with just name and prediction
                    model_info[model_name] = {
                        'name': model_name,
                        'prediction': format_currency(prediction_value),
                        'prediction_raw': prediction_value
                    }
                except Exception as e:
                    print(f"Error making prediction with {model_name}: {str(e)}")
                    predictions[model_name] = None
                    formatted_predictions[model_name] = "Error"
                    model_info[model_name] = {
                        'name': model_name,
                        'prediction': "Error",
                        'prediction_raw': None
                    }
        
        # Save the prediction data to database silently
        try:
            # Get user name from session
            user_name = request.session.get('user_name', 'Anonymous')
            
            # Create PropertyPrediction instance
            property_prediction = PropertyPrediction(
                user_name=user_name,
                title=float(input_data.get('Title', 0)),
                price_in_rupees=float(input_data.get('Price (in rupees)', 0)),
                bathroom=int(input_data.get('Bathroom', 0)),
                balcony=int(input_data.get('Balcony', 0)),
                super_area=float(input_data.get('Super Area', 0)),
                transaction=input_data.get('Transaction', ''),
                location=input_data.get('location', ''),
                furnishing=input_data.get('Furnishing', ''),
                facing=input_data.get('facing', ''),
                floor=input_data.get('Floor', ''),
                overlooking=input_data.get('overlooking', ''),
                society=input_data.get('Society', ''),
                prediction_xgboost=predictions.get('XGBoost'),
                prediction_decision_tree=predictions.get('Decision Tree'),
                prediction_lgbm=predictions.get('LGBM'),
                prediction_random_forest=predictions.get('Random Forest'),
                prediction_linear_regression=predictions.get('Linear Regression'),
                prediction_support_vector=predictions.get('Support Vector')
            )
            property_prediction.save()
            
        except Exception as e:
            # Silently handle database errors - don't show to user
            pass
        
        context = {
            'predictions': predictions,
            'formatted_predictions': formatted_predictions,
            'model_info': model_info,
            'input_data': input_data
        }
        
        return render(request, 'ml_predictor/result.html', context)
    
    except Exception as e:
        return render(request, 'ml_predictor/home.html', {
            'error': f'An error occurred: {str(e)}',
            'feature_schema': FEATURE_SCHEMA,
            'expected_features': get_feature_names()
        })
