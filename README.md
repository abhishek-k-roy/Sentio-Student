# Sentio Student 🧠

### An AI-assisted student well-being and reflection app

Sentio Student is a Streamlit-based application designed to help students reflect on their stress, understand their current workload, and explore practical ways to manage overwhelming academic situations.

By combining text-based emotion analysis, personalized reset suggestions, and self-reported stress tracking, Sentio provides a space for students to check in with themselves and observe patterns in their well-being over time.

> **Disclaimer:** Sentio Student is a general well-being and reflection tool. It is not a medical or mental-health diagnostic tool and is not intended for emergencies.

## ✨ Features

### 🏠 Home
A central starting point to navigate the app and explore its student well-being features.

### 📝 Student Check-in
- Describe what is happening in your academic or personal life.
- Use a fine-tuned DistilBERT model to analyze the submitted text and provide an uncertain, model-generated emotion prediction.
- Record self-reported stress on a 1–10 scale.
- Select a primary concern, workload level, available time, and optional energy and sleep information.
- Receive three practical reset suggestions based on the check-in choices.
- Select a suggestion and optionally provide feedback on whether it was helpful.

### 📊 My Well-being Patterns
Visualize self-reported well-being patterns through:
- Stress-over-time line charts.
- Average stress by concern.
- Average stress by workload.

These visualizations help users explore how their reported stress varies across check-ins and different situations.

### 📈 My Progress
- Compare the average stress score from earlier check-ins with more recent check-ins.
- View the number of logged check-ins and the stress trend.
- Explore changes in stress scores following selected reset suggestions.
- Identify suggestions associated with more favorable reported changes.

These comparisons are descriptive, not causal. A change in stress after a reset does not establish that the reset caused it.

### 🔒 About & Privacy
Sentio includes privacy information and an opt-in local tracking approach. When tracking is disabled, check-ins are not saved by the Student Check-in workflow. When tracking is enabled, selected check-in information is stored locally in SQLite, subject to the app's save-text option.

Users should avoid entering identifying or highly sensitive information.

## 🛠️ Tech Stack

- **Python** — application logic and data processing
- **Streamlit** — interactive web application interface
- **DistilBERT** — transformer-based text classification
- **Hugging Face Transformers** — model loading and inference
- **PyTorch** — deep-learning model execution
- **Pandas** — tabular data processing, where used
- **Plotly** — interactive charts, where used
- **SQLite** — local check-in storage

## 🧠 How It Works

1. The student completes a check-in and describes their current situation, if they wish.
2. The text is passed to the trained DistilBERT classifier for a model-generated emotion prediction, when text analysis is available.
3. The app selects practical reset suggestions using check-in choices such as the main concern, stress score, available time, and workload.
4. If tracking is enabled, the check-in is saved to the local database.
5. The student can select a suggestion and submit optional helpfulness feedback.
6. The progress and pattern pages visualize recorded check-ins and summarize observed changes over time.

The suggested actions are intended to support reflection and practical planning. The emotion prediction is an uncertain model output, not a definitive assessment of the student's emotional state.

## 🚀 Getting Started

### Prerequisites

- Python compatible with the project's installed dependencies
- Git
- A local copy of this repository

### Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/sentio-student.git
cd sentio-student
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Model Setup

The application requires the trained DistilBERT model files to be available at the path expected by the code.

If model weights are hosted separately, download them according to the instructions you provide and place them in the expected model directory. Do not commit large weight files to the repository unless you have deliberately chosen an appropriate hosting and versioning approach.

### Run the Application

From the project root, run:

```bash
python -m streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser.

## 📁 Project Structure

The main project files are organized approximately as follows:

```text
sentio-student/
├── app.py
├── pages/
│   ├── 1_Student_Check_in.py
│   ├── ...
├── sentio/
│   ├── database.py
│   ├── emotion_model.py
│   ├── suggestions.py
│   ├── safety.py
│   ├── privacy.py
│   └── ui.py
├── models/
│   └── distilBERT/
├── data/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

This is an illustrative overview. Update the page filenames and directories to match the files actually included in your repository.

## 🔐 Privacy and Data Handling

- Check-in tracking is opt-in.
- Check-ins are stored in a local SQLite database when tracking is enabled.
- The option to save written text is separate from saving the check-in's other fields.
- Local database files and secrets should not be committed to GitHub.
- Anyone running the app should review the source code and privacy information before entering personal information.

Local storage does not automatically mean data is encrypted. Avoid storing sensitive personal information, and use appropriate safeguards before deploying the application for other users.

## ⚠️ Limitations and Responsible Use

- Emotion predictions may be incorrect or uncertain.
- The app is not a substitute for professional mental-health support.
- Stress scores are self-reported and can be affected by many factors.
- A stress reduction after a suggested reset does not prove that the suggestion caused the change.
- The quality of the predictions depends on the training data, labels, and model evaluation.
- Results from synthetic or demonstration data must not be presented as real student outcomes.

## 🔮 Potential Future Improvements

- Evaluate model performance using suitable classification metrics and held-out data.
- Improve handling of ambiguous or out-of-scope text.
- Add a dedicated post-reset stress check-in to capture a student's immediate self-reported response.
- Improve longitudinal visualizations and data export.
- Add automated tests and more robust error handling.
- Document model provenance, licensing, and reproducible setup steps.

## 👨‍💻 About the Project

Sentio Student is a portfolio project exploring the intersection of natural language processing, machine learning, interactive data visualization, and student well-being.

The project demonstrates how AI and data-driven interfaces can be used to build a practical reflection tool while acknowledging the limitations of model predictions and self-reported data.

---

**Built with Python, Streamlit, DistilBERT, and PyTorch.**
