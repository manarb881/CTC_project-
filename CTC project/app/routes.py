from flask import Flask, request, jsonify
from .models import RLAgent
from .utils import get_user_from_db, get_db_connection, fetch_questions_by_difficulty, add_user_to_db
import pandas as pd
from .config import Config

difficulty_skill_map = {
    'Beginner': 'Easy',
    'Intermediate': 'Medium',
    'Advanced': 'Hard'
}
def get_current_difficulty(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT skill_level FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    if user:
        return difficulty_skill_map.get(user['skill_level'])  # Assuming you have a mapping for skill levels
    return None

def add_routes(app,rl_agent):
    # Route to add a user and predict their skill level
  
    @app.route('/addUser', methods=['POST'])
    def add_user():
        user_data = request.json
        user_id = user_data['user_id']
        name = user_data['name']
        age = user_data['age']
        gender = user_data['gender']
        years_experience = user_data['yearsExperience']
        learning_preference = user_data['learning_preference']
        
        # Fetch the user's score and response time from the test database
        connection = get_db_connection()
        
        if connection:
           print("Database connection successful")

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT score, response_time FROM test_results WHERE user_id = %s",
            (user_id,)
        )
        test_results = cursor.fetchone()
        cursor.close()
        connection.close()

        if not test_results:
            return jsonify({"error": "Test results not found for user"}), 404

        score = test_results['score']
        response_time = test_results['response_time']
        
        # Prepare the user data for prediction
        user_df = pd.DataFrame([[age, score, response_time, years_experience, gender]],
                               columns=['age', 'score', 'response_time', 'YearsExperience', 'gender'])

       
        predicted_skill_level ='Intermediate'
     

        add_user_to_db(user_id, name, age, gender, predicted_skill_level, learning_preference, years_experience)

        # Fetch the appropriate difficulty level based on skill level
        difficulty_level = get_difficulty_from_skill(predicted_skill_level)

        # Fetch questions based on difficulty level
        questions = fetch_questions_by_difficulty(difficulty_level, user_id)

        return jsonify({
            "message": "User added successfully!",
            "predicted_skill_level": predicted_skill_level,
            "questions": questions,
            "difficulty_level": difficulty_level
        })

    # Function to get difficulty from skill level
    def get_difficulty_from_skill(skill_level):
        difficulty_map = {
            'Beginner': 'Easy',
            'Intermediate': 'Medium',
            'Advanced': 'Hard'
        }
        return difficulty_map.get(skill_level, 'Easy')
    @app.route('/submitAnswer', methods=['POST'])
    def submit_answer():
     print("submit_answer route triggered")  # Debugging line
    try:
        user_data = request.json
        user_id = user_data['user_id']
        answers = user_data['answers']  # List of dictionaries containing question_id, score, response_time, feedback
        attempt_date = user_data['attempt_date']
        
        print(f"Received data: {user_data}")  # Debugging line

        # Store user answers in the performance table
        connection = get_db_connection()
        print('that was succesfull')
        cursor = connection.cursor(dictionary=True)
        for answer in answers:
            cursor.execute(
                """
                INSERT INTO performance (user_id, qst_id, score, response_time, feedback, attempt_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user_id, answer['qst_id'], answer['score'], answer['response_time'], answer['feedback'], attempt_date)
            )
        connection.commit()
        cursor.close()
        print("Answers inserted successfully")  # Debugging line

        # Check if the user has answered 10 questions at the current difficulty level
        current_difficulty = get_current_difficulty(user_id)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT COUNT(*) as question_count
            FROM performance
            WHERE user_id = %s AND qst_id IN (
                SELECT question_id FROM questions WHERE difficulty_level = %s
            )
            """,
            (user_id, current_difficulty)
        )
        question_count = cursor.fetchone()['question_count']
        cursor.close()
        print(f"Question count: {question_count}")  # Debugging line

        # Determine next step based on the number of answered questions
        if question_count == 10:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT COUNT(*) as score_count
                FROM performance
                WHERE user_id = %s AND score = 1 AND qst_id IN (
                    SELECT question_id FROM questions WHERE difficulty_level = %s
                )
                """,
                (user_id, current_difficulty)
            )
            score_count = cursor.fetchone()['score_count']
            cursor.close()

            avg_score = (score_count / question_count) * 10 if question_count > 0 else 0

            return jsonify({
                "next_step": "adjust_difficulty",
                "avg_score": avg_score,
                "current_difficulty": current_difficulty
            })

        else:
            fetch_questions_by_difficulty(current_difficulty, user_id)
            return jsonify({"next_step": "continue", "current_difficulty": current_difficulty})

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging line
        return jsonify({"error": str(e)}), 500
    finally:
        # Ensure the database connection is closed even if an error occurs
        if connection:
            connection.close()


    # Route to adjust the difficulty based on performance after 10 questions
    @app.route('/adjustDifficulty', methods=['POST'])
    def adjust_difficulty():
        user_data = request.json
        user_id = user_data['user_id']
        avg_score = user_data['avg_score']  # Performance percentage in the last session (out of 10)

        # Fetch the user's current information from the database
        user_info = get_user_from_db(user_id)

        if not user_info:
            return jsonify({"error": "User not found"}), 404

        # Determine reward or penalty based on performance threshold
        reward = 1 if avg_score == 10 else -1

        # Update RL agent's state
        current_state = str(user_info['skill_level'])
        current_action = difficulty_skill_map[user_info['skill_level']]

        # Adjust exploration rate dynamically
        rl_agent.adjust_exploration_rate(avg_score)

        # Get next action (difficulty level) from RL agent
        next_action = rl_agent.choose_action(current_state)

        # Update Q-table with feedback (reward/penalty)
        rl_agent.update_q_table(current_state, current_action, reward, next_action)

        # Save the RL agent (model) after updating it
        try:
            rl_agent.save_agent('app/model/rl_agent.pkl')
        except Exception as e:
            return jsonify({"error": f"Failed to save agent: {str(e)}"}), 500

        # Update the user's skill level in the users table
        update_skill_level(user_id, next_action)

        # Fetch new questions based on the adjusted difficulty level
        questions = fetch_questions_by_difficulty(next_action, user_id)

        return jsonify({
            "message": "Difficulty adjusted successfully!",
            "new_skill_level": user_info['skill_level'],
            "performance": avg_score,
            "reward": reward,
            "questions": questions,
            "difficulty_level": next_action
        })

    # Function to update the skill level in the users table
    def update_skill_level(user_id, new_difficulty_level):
        skill_level_map = {
            'Easy': 'Beginner',
            'Medium': 'Intermediate',
            'Hard': 'Advanced'
        }

        new_skill_level = skill_level_map.get(new_difficulty_level, 'Beginner')  # Default to 'Beginner' if not found

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE users
            SET skill_level = %s
            WHERE user_id = %s
            """,
            (new_skill_level, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
