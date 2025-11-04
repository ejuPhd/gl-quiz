from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import json
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production!

# Load questions from JSON file


def load_questions():
    with open('questions.json', 'r') as f:
        data = json.load(f)
    return data['questions']


def get_questions_by_difficulty(questions, difficulty, count=50):
    """Get specified number of questions by difficulty level"""
    filtered = [q for q in questions if q['difficulty'] == difficulty]
    return random.sample(filtered, min(count, len(filtered)))


def calculate_score(questions, user_answers):
    """Calculate score based on difficulty and correct answers"""
    score = 0
    correct_count = 0
    difficulty_points = {'beginner': 10, 'intermediate': 20, 'advanced': 30}

    for i, question in enumerate(questions):
        if user_answers.get(str(i)) == question['correct_answer']:
            score += difficulty_points[question['difficulty']]
            correct_count += 1

    return score, correct_count


@app.route('/')
def index():
    session.clear()  # Clear any existing session data
    return render_template('index.html')


@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    difficulty = request.form.get('difficulty', 'beginner')
    questions = load_questions()

    # Select questions based on difficulty - CHANGED FROM 10 TO 50
    quiz_questions = get_questions_by_difficulty(questions, difficulty, 50)

    # Initialize session
    session['quiz_questions'] = quiz_questions
    session['user_answers'] = {}
    session['current_question'] = 0
    session['start_time'] = datetime.now().isoformat()
    session['difficulty'] = difficulty
    session['score'] = 0

    return redirect(url_for('quiz'))


@app.route('/quiz')
def quiz():
    if 'quiz_questions' not in session:
        return redirect(url_for('index'))

    current_idx = session['current_question']
    questions = session['quiz_questions']

    if current_idx >= len(questions):
        return redirect(url_for('results'))

    question = questions[current_idx]

    # Calculate progress percentage and round to nearest 10 for class name
    progress_percent = (current_idx / len(questions)) * 100
    progress_class = f"progress-{int(round(progress_percent / 10) * 10)}"

    # Calculate exact progress percentage for display
    exact_progress = (current_idx / len(questions)) * 100

    return render_template('quiz.html',
                           question=question,
                           question_num=current_idx + 1,
                           total_questions=len(questions),
                           progress_class=progress_class,
                           progress_percent=exact_progress)  # Added this line


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'quiz_questions' not in session:
        return redirect(url_for('index'))

    current_idx = session['current_question']
    answer = request.form.get('answer')

    # Store the answer
    session['user_answers'][str(current_idx)] = int(answer) if answer else None
    session['current_question'] = current_idx + 1

    # Move to next question or show results
    if current_idx + 1 >= len(session['quiz_questions']):
        return redirect(url_for('results'))
    else:
        return redirect(url_for('quiz'))


@app.route('/results')
def results():
    if 'quiz_questions' not in session or 'user_answers' not in session:
        return redirect(url_for('index'))

    questions = session['quiz_questions']
    user_answers = session['user_answers']

    # Calculate score
    score, correct_count = calculate_score(questions, user_answers)
    session['score'] = score
    session['correct_count'] = correct_count
    session['end_time'] = datetime.now().isoformat()

    # Prepare results with explanations
    results_data = []
    for i, question in enumerate(questions):
        user_answer = user_answers.get(str(i))
        is_correct = user_answer == question['correct_answer']
        results_data.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
            'correct_answer': question['correct_answer']
        })

    return render_template('results.html',
                           results=results_data,
                           score=score,
                           correct_count=correct_count,
                           total_questions=len(questions),
                           difficulty=session['difficulty'])


@app.route('/leaderboard')
def leaderboard():
    # In a real app, you'd store this in a database
    # For now, we'll use a simple list in session
    leaderboard_data = session.get('leaderboard', [])
    return render_template('leaderboard.html', leaderboard=leaderboard_data)


@app.route('/save_score', methods=['POST'])
def save_score():
    player_name = request.form.get('player_name', 'Anonymous')
    score = session.get('score', 0)
    difficulty = session.get('difficulty', 'beginner')

    # Add to leaderboard
    leaderboard_entry = {
        'name': player_name,
        'score': score,
        'difficulty': difficulty,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }

    leaderboard = session.get('leaderboard', [])
    leaderboard.append(leaderboard_entry)
    # Sort by score descending and keep top 10
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    session['leaderboard'] = leaderboard[:10]

    return redirect(url_for('leaderboard'))


@app.route('/restart')
def restart():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
