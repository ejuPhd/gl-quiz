from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import json
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Load questions from JSON file


def load_questions():
    """Loads all quiz questions from the questions.json file."""
    # NOTE: Assumes 'questions.json' is available in the same directory
    with open('questions.json', 'r') as f:
        data = json.load(f)
    return data['questions']


def get_questions_by_difficulty(questions, difficulty, count=50):
    """
    Selects a specified number of questions by difficulty level.
    Ensures the number of selected questions does not exceed available questions.
    """
    filtered = [q for q in questions if q['difficulty'] == difficulty]
    return random.sample(filtered, min(count, len(filtered)))


def get_question_by_id(question_id):
    """Retrieves a specific question by its ID."""
    questions = load_questions()
    for q in questions:
        if q['id'] == question_id:
            return q
    return None


def calculate_score(question_ids, user_answers):
    """Calculates the final score and correct count based on user submissions."""
    score = 0
    correct_count = 0
    difficulty_points = {'beginner': 10, 'intermediate': 20, 'advanced': 30}

    questions = load_questions()
    question_dict = {q['id']: q for q in questions}

    for i, question_id in enumerate(question_ids):
        question = question_dict[question_id]
        # Compare user's answer index (int) with the correct answer index (int)
        if user_answers.get(str(i)) == question['correct_answer']:
            score += difficulty_points[question['difficulty']]
            correct_count += 1

    return score, correct_count


@app.route('/')
def index():
    """Home page: Clears session and displays difficulty/question count selection."""
    session.clear()
    return render_template('index.html')


@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    """Initializes the quiz session based on user selections."""
    difficulty = request.form.get('difficulty', 'beginner')

    # Get and validate question count (between 5 and 50)
    try:
        question_count = min(
            50, max(5, int(request.form.get('question_count', 10))))
    except ValueError:
        question_count = 10  # Default fallback

    questions = load_questions()

    # Select questions based on difficulty and count
    quiz_questions = get_questions_by_difficulty(
        questions, difficulty, question_count)

    # Store only question IDs in session
    question_ids = [q['id'] for q in quiz_questions]

    # Initialize session state
    session['question_ids'] = question_ids
    session['user_answers'] = {}
    session['current_question'] = 0
    session['start_time'] = datetime.now().isoformat()
    session['difficulty'] = difficulty
    session['score'] = 0
    # NEW: Initialize correct/incorrect counters for real-time tracking
    session['correct_count_rt'] = 0
    session['incorrect_count_rt'] = 0
    session.modified = True

    return redirect(url_for('quiz'))


@app.route('/quiz')
def quiz():
    """Renders the current question and tracks progress."""
    if 'question_ids' not in session:
        return redirect(url_for('index'))

    current_idx = session.get('current_question', 0)
    question_ids = session['question_ids']
    total_questions = len(question_ids)

    # Check for end of quiz
    if current_idx >= total_questions:
        return redirect(url_for('results'))

    # Get the current question by ID
    question = get_question_by_id(question_ids[current_idx])

    if not question:
        print(f"Error: Question ID {question_ids[current_idx]} not found.")
        return redirect(url_for('index'))

    # CORRECTED: Calculate progress for progress bar and text
    progress_percent = (current_idx / total_questions) * 100
    # Create class name for CSS color coding (e.g., progress-30)
    progress_class = f"progress-{int(round(progress_percent / 10) * 10)}"
    exact_progress = progress_percent

    # Retrieve real-time counters from session
    correct_count_rt = session.get('correct_count_rt', 0)
    incorrect_count_rt = session.get('incorrect_count_rt', 0)

    return render_template('quiz.html',
                           question=question,
                           question_num=current_idx + 1,
                           total_questions=total_questions,
                           progress_class=progress_class,
                           progress_percent=exact_progress,
                           # NEW: Pass real-time counters
                           correct_count_rt=correct_count_rt,
                           incorrect_count_rt=incorrect_count_rt)


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Processes the user's answer, updates real-time score, and moves to the next question."""
    if 'question_ids' not in session:
        return redirect(url_for('index'))

    current_idx = session['current_question']
    answer = request.form.get('answer')
    question_ids = session['question_ids']

    if current_idx >= len(question_ids):
        return redirect(url_for('results'))

    question_id = question_ids[current_idx]
    question = get_question_by_id(question_id)

    if question and answer is not None:
        try:
            user_answer = int(answer)

            # NEW: Check correctness and update real-time counter
            if user_answer == question['correct_answer']:
                session['correct_count_rt'] += 1
            else:
                session['incorrect_count_rt'] += 1

            # Store the answer
            session['user_answers'][str(current_idx)] = user_answer
        except ValueError:
            session['user_answers'][str(current_idx)] = None
    else:
        session['user_answers'][str(current_idx)] = None

    session['current_question'] = current_idx + 1
    session.modified = True  # Necessary to save changes to complex/modified session data

    # Move to next question or show results
    if session['current_question'] >= len(question_ids):
        return redirect(url_for('results'))
    else:
        return redirect(url_for('quiz'))


@app.route('/results')
def results():
    """Displays the final quiz results, score, and detailed review."""
    if 'question_ids' not in session or 'user_answers' not in session:
        return redirect(url_for('index'))

    question_ids = session['question_ids']
    user_answers = session['user_answers']

    # Calculate final score (which resets/confirms the real-time counters)
    score, correct_count = calculate_score(question_ids, user_answers)
    session['score'] = score
    session['correct_count'] = correct_count
    session['end_time'] = datetime.now().isoformat()
    session.modified = True  # Ensure all updates are saved

    # Prepare results with explanations
    results_data = []
    questions = load_questions()
    question_dict = {q['id']: q for q in questions}

    for i, question_id in enumerate(question_ids):
        question = question_dict.get(question_id)
        if not question:
            continue

        user_answer = user_answers.get(str(i))
        is_correct = user_answer == question['correct_answer']

        options = question.get('options', [])

        # Determine user answer text
        user_answer_text = "No answer selected"
        if user_answer is not None and user_answer >= 0 and user_answer < len(options):
            user_answer_text = options[user_answer]

        # Determine correct answer text
        correct_answer_index = question['correct_answer']
        correct_answer_text = f"Answer #{correct_answer_index + 1} (Option not found)"
        if correct_answer_index >= 0 and correct_answer_index < len(options):
            correct_answer_text = options[correct_answer_index]

        results_data.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
            'correct_answer': correct_answer_index,
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
    """Check if all questions have required fields (Development helper function)."""
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


@app.route('/leaderboard')
def leaderboard():
    """Displays the leaderboard from session storage."""
    leaderboard_data = session.get('leaderboard', [])
    return render_template('leaderboard.html', leaderboard=leaderboard_data)


@app.route('/save_score', methods=['POST'])
def save_score():
    """Saves the player's score to the leaderboard in session."""
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
    # Keep only the top 10 scores
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    session['leaderboard'] = leaderboard[:10]
    session.modified = True  # Ensure leaderboard update is saved

    return redirect(url_for('leaderboard'))


@app.route('/restart')
def restart():
    """Clears the session and redirects to the home page."""
    session.clear()
    return redirect(url_for('index'))


# Temporary: Check for problematic questions on startup
problematic_questions = validate_questions()
if problematic_questions:
    print("🚨 PROBLEMATIC QUESTIONS FOUND:")
    for pq in problematic_questions:
        print(f"Question ID {pq['id']} missing: {pq['missing_fields']}")
else:
    print("✅ All questions have required fields!")


if __name__ == '__main__':
    app.run(debug=True)
