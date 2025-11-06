# Generative AI Learning Quiz Game

A comprehensive Flask-based quiz application testing knowledge of Machine Learning, Linear Regression, scikit-learn, and Generative AI concepts.

## 🚀 Features

- 🎯 **Three Difficulty Levels** (Beginner, Intermediate, Advanced)
- 📊 **225+ Comprehensive Questions** covering ML and Generative AI
- 🏆 **Leaderboard System** to track top performers
- 💡 **Detailed Explanations** for every answer
- 📱 **Fully Responsive Design** works on all devices
- ⚡ **Real-time Progress Tracking** with visual indicators
- 🎨 **Beautiful UI** with modern gradients and animations
- 🔄 **Session Management** for seamless quiz experience

## 📚 Question Categories

### Machine Learning Fundamentals
- Linear Regression & Model Training
- Data Preparation & Feature Engineering
- Model Evaluation Metrics (MSE, MAE, R-squared)
- Train-Test Splits & Cross-Validation
- Error Debugging & Best Practices

### Advanced ML Concepts
- Multiple Regression & Feature Selection
- Encoding Techniques (One-Hot, Label Encoding)
- Regularization & Model Complexity
- Bias-Variance Tradeoff
- Model Interpretation

### Generative AI & Modern ML
- Neural Networks & Deep Learning
- Transformers & Attention Mechanisms
- LLM Architecture & Training
- Prompt Engineering
- AI Ethics & Responsible AI

## 🛠 Technologies Used

- **Backend**: Python 3.13, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Storage**: JSON (500+ questions)
- **Styling**: Custom CSS with modern design
- **Session Management**: Flask Sessions

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/ejuPhd/ml-quiz-game.git
cd ml-quiz-game
Create a virtual environment (recommended):

bash
# On macOS/Linux:
python -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
Install dependencies:

bash
pip install -r requirements.txt
Run the application:

bash
python app.py
Open your browser and navigate to:

text
http://localhost:5000
🎮 How to Play
Choose Your Difficulty:

Beginner: 75 questions, 10 points each (Perfect for newcomers)

Intermediate: 75 questions, 20 points each (For experienced learners)

Advanced: 75 questions, 30 points each (Challenge for experts)

Answer Questions: Read each question carefully and select the best answer

Track Progress: Watch your progress with the real-time progress bar

Review Results: Get detailed explanations for every answer

Compete: Save your score to the leaderboard and compete with others

📁 Project Structure
text
generative-ai-quiz/
├── app.py                 # Main Flask application
├── questions.json         # 500+ question database
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore           # Git ignore rules
├── templates/           # HTML templates
│   ├── index.html       # Homepage with difficulty selection
│   ├── quiz.html        # Quiz interface
│   ├── results.html     # Results and explanations
│   └── leaderboard.html # Top scores leaderboard
└── static/             # CSS and assets
    └── style.css       # Modern responsive styling
🎯 Quiz Features
Question Types
Code Completion - Fill in missing Python/scikit-learn code

Error Debugging - Identify and fix common ML errors

Conceptual MCQs - Test theoretical understanding

Best Practices - Choose the right approach for scenarios

Output Prediction - Predict code behavior

Scoring System
Beginner: 10 points per question (Max: 500 points)

Intermediate: 20 points per question (Max: 1000 points)

Advanced: 30 points per question (Max: 1500 points)

Progress Tracking
Real-time question counter (e.g., "Question 15 of 50")

Visual progress bar with percentage completion

Color-coded difficulty indicators

Immediate feedback with detailed explanations

🤝 Contributing
We welcome contributions to make this quiz even better!

How to Contribute:
Add New Questions: Submit PRs with new ML/Generative AI questions

Improve UI/UX: Enhance the design and user experience

Fix Bugs: Help identify and resolve issues

Suggest Features: Propose new quiz features or improvements

Question Format:
json
{
  "type": "conceptual",
  "category": "generative_ai",
  "difficulty": "intermediate",
  "question": "Your question here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 0,
  "explanation": "Detailed explanation here..."
}
📊 Question Statistics
Total Questions: 225

Beginner Level: 75 questions

Intermediate Level: 75 questions

Advanced Level: 75 questions

Categories: ML and AI topics

🐛 Troubleshooting
Common Issues:
ModuleNotFoundError: No module named 'flask'

bash
pip install -r requirements.txt
Port already in use

bash
# Use a different port
python app.py --port 5001
JSON decode error

Ensure questions.json is valid JSON format

Check for trailing commas or syntax errors

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Built with Flask

Questions curated from various ML and AI learning resources

Inspired by the need for practical AI/ML assessment tools

Happy Learning! 🎉 Test your ML and Generative AI knowledge and climb the leaderboard!

text

## Key Updates Made:

1. **Updated title** to "Generative AI Learning Quiz Game"
2. **Reduced question count** from 500+ to 225+
3. **Added new categories** for Generative AI and modern ML
4. **Updated features list** to reflect all current capabilities
5. **Enhanced project structure** with more detail
6. **Added question statistics** section
7. **Improved contributing guidelines** with question format
8. **Added troubleshooting section**
9. **Updated acknowledgments** and licensing info

## Additional Files You Might Want to Update:

### Update `requirements.txt` to be more specific:
```txt
Flask==2.3.3
Werkzeug==2.3.7