import mysql.connector
from faker import Faker
import random


import os


MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")


# Initialize Faker
fake = Faker()


# Establish MySQL connection
conn = mysql.connector.connect(
   host="127.0.0.1",    
   user="root",    
   password='2004manar', 
   database="ctc5",
   auth_plugin="mysql_native_password"
)


cursor = conn.cursor()




# Step 4: Insert Questions Data
def insert_questions(num_questions):
   for _ in range(num_questions):
       question_text = fake.text(max_nb_chars=100)  # Random question text
       difficulty_level = random.choice(['Easy', 'Medium', 'Hard'])
       correct_answer = fake.word()  # Random word as correct answer
       simulation_context = fake.text(max_nb_chars=200)  # Simulation context
       type_qst = random.choice(['Visual', 'Auditory', 'Kinesthetic'])
       cursor.execute("""
           INSERT INTO questions (question_text, difficulty_level, correct_answer, simulation_context,type_qst)
           VALUES (%s, %s, %s, %s,%s)
       """, (question_text, difficulty_level, correct_answer, simulation_context,type_qst))
  
   conn.commit()

   










# Call the functions to insert data
 # Insert 50 users
insert_questions(50)  # Insert 50 questions
print('added succesfully')
# Close the connection
cursor.close()
conn.close()
