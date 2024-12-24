import pandas as pd
import pickle
from utils import add_user_to_db,fetch_questions_by_difficulty,get_db_connection

def test_model_loading(filepath):
    try:
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        print("Model loaded successfully.")
        
        # Create a test DataFrame
        test_data = pd.DataFrame([[25, 85, 1.2, 3, 'Male']],
                                 columns=['age', 'score', 'response_time', 'YearsExperience', 'gender'])
        
        # Preprocess the test data if necessary
        test_data['gender'] = test_data['gender'].map({'Male': 1, 'Female': 0})
        
        # Make a prediction
        prediction = model.predict(test_data)
        print("Prediction:", prediction)
        
    except Exception as e:
        print(f"Error loading or using the model: {e}")
        return None

# Test the function
#test_model_loading("/Users/pc/CTC project/app/model/SL_model.pkl")


#add_user_to_db(1, 'name', 20, 'Male', 'advanced', 'Visual', 3)
#a=fetch_questions_by_difficulty('Hard',1)
#print(a)
get_db_connection()