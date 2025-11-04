from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import json
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Load questions from JSON file


def load_questions():
    with open('questions.json', 'r') as f:
        data = json.load(f)
    return data['questions']


def get_questions_by_difficulty(questions, difficulty, count=50):
    """Get specified number of questions by difficulty level"""
    filtered = [q for q in questions if q['difficulty'] == difficulty]
    return random.sample(filtered, min(count, len(filtered)))


def get_question_by_id(question_id):
    """Get a specific question by ID from the full question set"""
    questions = load_questions()
    for q in questions:
        if q['id'] == question_id:
            return q
    return None


def calculate_score(question_ids, user_answers):
    """Calculate score based on difficulty and correct answers"""
    score = 0
    correct_count = 0
    difficulty_points = {'beginner': 10, 'intermediate': 20, 'advanced': 30}

    questions = load_questions()
    question_dict = {q['id']: q for q in questions}

    for i, question_id in enumerate(question_ids):
        question = question_dict[question_id]
        if user_answers.get(str(i)) == question['correct_answer']:
            score += difficulty_points[question['difficulty']]
            correct_count += 1

    return score, correct_count


@app.route('/')
def index():
    session.clear()
    return render_template('index.html')


@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    difficulty = request.form.get('difficulty', 'beginner')
    questions = load_questions()

    # Select questions based on difficulty
    quiz_questions = get_questions_by_difficulty(questions, difficulty, 50)

    # Store only question IDs in session to avoid cookie size limits
    question_ids = [q['id'] for q in quiz_questions]

    # Initialize session with minimal data
    session['question_ids'] = question_ids
    session['user_answers'] = {}
    session['current_question'] = 0
    session['start_time'] = datetime.now().isoformat()
    session['difficulty'] = difficulty
    session['score'] = 0

    return redirect(url_for('quiz'))


@app.route('/quiz')
def quiz():
    if 'question_ids' not in session:
        return redirect(url_for('index'))

    current_idx = session['current_question']
    question_ids = session['question_ids']

    if current_idx >= len(question_ids):
        return redirect(url_for('results'))

    # Get the current question by ID
    question = get_question_by_id(question_ids[current_idx])

    if not question:
        return redirect(url_for('index'))

    # Calculate progress
    progress_percent = (current_idx / len(question_ids)) * 100
    progress_class = f"progress-{int(round(progress_percent / 10) * 10)}"
    exact_progress = (current_idx / len(question_ids)) * 100

    return render_template('quiz.html',
                           question=question,
                           question_num=current_idx + 1,  # This shows current question number
                           total_questions=len(question_ids),
                           progress_class=progress_class,
                           progress_percent=exact_progress)


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'question_ids' not in session:
        return redirect(url_for('index'))

    current_idx = session['current_question']
    answer = request.form.get('answer')

    # Store the answer
    session['user_answers'][str(current_idx)] = int(answer) if answer else None
    session['current_question'] = current_idx + 1

    # Move to next question or show results
    if current_idx + 1 >= len(session['question_ids']):
        return redirect(url_for('results'))
    else:
        return redirect(url_for('quiz'))


@app.route('/results')
def results():
    if 'question_ids' not in session or 'user_answers' not in session:
        return redirect(url_for('index'))

    question_ids = session['question_ids']
    user_answers = session['user_answers']

    # Calculate score
    score, correct_count = calculate_score(question_ids, user_answers)
    session['score'] = score
    session['correct_count'] = correct_count
    session['end_time'] = datetime.now().isoformat()

    # Prepare results with explanations - FIXED: Handle missing 'options' key
    results_data = []
    questions = load_questions()
    question_dict = {q['id']: q for q in questions}

    for i, question_id in enumerate(question_ids):
        question = question_dict[question_id]
        user_answer = user_answers.get(str(i))
        is_correct = user_answer == question['correct_answer']

        # Safely handle questions that might be missing 'options' key
        user_answer_text = "No answer"
        if user_answer is not None:
            if 'options' in question and user_answer < len(question['options']):
                user_answer_text = question['options'][user_answer]
            else:
                user_answer_text = f"Answer #{user_answer + 1}"

        correct_answer_text = f"Answer #{question['correct_answer'] + 1}"
        if 'options' in question and question['correct_answer'] < len(question['options']):
            correct_answer_text = question['options'][question['correct_answer']]

        results_data.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
            'correct_answer': question['correct_answer'],
            'user_answer_text': user_answer_text,
            'correct_answer_text': correct_answer_text
        })

    return render_template('results.html',
                           results=results_data,
                           score=score,
                           correct_count=correct_count,
                           total_questions=len(question_ids),
                           difficulty=session['difficulty'])


def validate_questions():
    """Check if all questions have required fields"""
    questions = load_questions()
    problematic_questions = []

    for q in questions:
        missing_fields = []
        if 'id' not in q:
            missing_fields.append('id')
        if 'options' not in q:
            missing_fields.append('options')
        if 'correct_answer' not in q:
            missing_fields.append('correct_answer')
        if 'difficulty' not in q:
            missing_fields.append('difficulty')
        if 'category' not in q:
            missing_fields.append('category')

        if missing_fields:
            problematic_questions.append({
                'id': q.get('id', 'Unknown'),
                'missing_fields': missing_fields
            })

    return problematic_questions

# You can call this function to check your questions
# problematic = validate_questions()
# if problematic:
#     print("Problematic questions found:", problematic)


@app.route('/leaderboard')
def leaderboard():
    leaderboard_data = session.get('leaderboard', [])
    return render_template('leaderboard.html', leaderboard=leaderboard_data)


@app.route('/save_score', methods=['POST'])
def save_score():
    player_name = request.form.get('player_name', 'Anonymous')
    score = session.get('score', 0)
    difficulty = session.get('difficulty', 'beginner')

    leaderboard_entry = {
        'name': player_name,
        'score': score,
        'difficulty': difficulty,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }

    leaderboard = session.get('leaderboard', [])
    leaderboard.append(leaderboard_entry)
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    session['leaderboard'] = leaderboard[:10]

    return redirect(url_for('leaderboard'))


@app.route('/restart')
def restart():
    session.clear()
    return redirect(url_for('index'))


# Temporary: Check for problematic questions
problematic_questions = validate_questions()
if problematic_questions:
    print("🚨 PROBLEMATIC QUESTIONS FOUND:")
    for pq in problematic_questions:
        print(f"Question ID {pq['id']} missing: {pq['missing_fields']}")
else:
    print("✅ All questions have required fields!")


if __name__ == '__main__':
    app.run(debug=True)
