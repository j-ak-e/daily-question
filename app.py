from flask import Flask, render_template
from datetime import date
import json

app = Flask(__name__)

with open("questions.json") as f:
    questions = json.load(f)

@app.route("/")
def home():
    today = date.today()
    index = today.toordinal() % len(questions)
    question = questions[index]
    return render_template("index.html", question=question)

if __name__ == "__main__":
    app.run(debug=True)