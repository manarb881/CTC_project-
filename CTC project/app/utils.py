import mysql.connector
#from .config import Config

# Function to get a connection to the database

import logging


def get_db_connection():
    
        try:
            connection = mysql.connector.connect(
              host="127.0.0.1",    
              user="root",    
              password="2004manar", 
              database="ctc5" ,
              port=3306,
              auth_plugin="mysql_native_password"
             )

            print('connection succesful') 
            return connection
       
        except mysql.connector.Error as err:
            logging.error(f"MySQL error: {err}")
        
      
            return 0

# Function to add a new user to the database
def add_user_to_db(user_id, name, age, gender, predicted_skill_level, learning_preference, years_experience):
    connection = get_db_connection()
    if connection is None:
        return "Failed to connect to the database"
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, name, age, gender, skill_level, learning_preference, yearsExperience) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (user_id, name, age, gender, predicted_skill_level, learning_preference, years_experience)
        )
        connection.commit()
        return "User added successfully"
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "Failed to add user to the database"
    finally:
        if connection:
            connection.close()

# Function to retrieve user information from the database
def get_user_from_db(user_id):
    connection = get_db_connection()
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT skill_level, difficulty_level FROM users WHERE user_id = %s", (user_id))
        user_info = cursor.fetchone()
        return user_info
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if connection:
            connection.close()

# Function to fetch questions based on the difficulty level and user's preferences
def fetch_questions_by_difficulty(difficulty_level,user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT learning_preference FROM users WHERE user_id = %s", (user_id,))
        user_preference = cursor.fetchone()
        if not user_preference:
            logging.warning(f"No user preference found for user_id: {user_id}")
            return []

        cursor.execute(
            "SELECT question_id, question_text FROM questions WHERE type_qst = %s AND difficulty_level = %s",
            (user_preference['learning_preference'], difficulty_level)
        )
        questions = cursor.fetchall() 
        return [q['question_text'] for q in questions] if questions else [{'dificulty level':difficulty_level}]
    except mysql.connector.Error as err:
        logging.error(f"MySQL error: {err}")
        return []
    finally:
        if connection:
            connection.close()
