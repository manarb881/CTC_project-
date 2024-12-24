CREATE TABLE users (
    user_id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    gender ENUM('Male', 'Female', 'Other'),
    skill_level VARCHAR(50),
    learning_preference VARCHAR(50),
    years_experience INT
);

CREATE TABLE questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    question_text TEXT NOT NULL,
    type_qst ENUM('Visual', 'Auditory', 'Kinesthetic') NOT NULL,
    difficulty_level ENUM('Easy', 'Medium', 'Hard') NOT NULL
);

CREATE TABLE performance (
    performance_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    question_id INT,
    correctness BOOLEAN,
    time_taken FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE
);

CREATE TABLE test_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    age INT,
    score FLOAT CHECK (score BETWEEN 0 AND 10),
    response_time FLOAT,
    YearsExperience INT,
    gender VARCHAR(10),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

