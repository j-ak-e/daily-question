from flask import Flask, render_template, request, redirect
from datetime import date
import json
import os

app = Flask(__name__)

def load_questions(subject):
    path = f"questionbanks/{subject}.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def get_todays_question(questions):
    index = date.today().toordinal() % len(questions)
    return questions[index]

def detect_and_convert(lines, deck_name):
    questions = []
    subject = deck_name.replace("-", " ").title()

    for line in lines:
        line = line.strip().replace("\u00ad", "")
        if line.startswith("#") or not line:
            continue
        parts = line.split("\t")

        if len(parts) == 2:
            # Standard term/definition
            term, definition = parts
            questions.append({
                "subject": subject,
                "text": f"Define: {term}",
                "answer": definition
            })

        elif len(parts) >= 5 and not parts[0].strip().isdigit():
            # Spanish conjugation: verb, conjugation, tense, -, context
            verb, conjugation, tense, _, context = parts[:5]
            questions.append({
                "subject": subject,
                "text": f"What is the {tense} tense conjugation of '{verb}'? ({context.strip()})",
                "answer": conjugation
            })

        elif len(parts) >= 3 and parts[0].strip().isdigit():
            # Periodic table: number, symbol, name, ...
            number, symbol, name = parts[:3]
            category = parts[6].strip() if len(parts) > 6 else ""
            questions.append({
                "subject": subject,
                "text": f"What is the symbol for {name}?",
                "answer": symbol
            })
            questions.append({
                "subject": subject,
                "text": f"What element has atomic number {number}?",
                "answer": name
            })
            if category:
                questions.append({
                    "subject": subject,
                    "text": f"What category is {name}?",
                    "answer": category
                })

        elif len(parts) >= 3 and not parts[0].strip().isdigit():
            # Vocab with example sentence: term, definition, example
            term, definition = parts[0], parts[1]
            questions.append({
                "subject": subject,
                "text": f"Define: {term}",
                "answer": definition
            })

    return questions

@app.route("/")
def home():
    subjects = [f.replace(".json", "") for f in os.listdir("questionbanks") if f.endswith(".json")]
    return render_template("home.html", subjects=subjects)

@app.route("/<subject>")
def question_page(subject):
    questions = load_questions(subject)
    if questions is None:
        return "Question bank not found", 404
    question = get_todays_question(questions)
    return render_template("index.html", question=question, subject=subject)

@app.route("/import", methods=["GET", "POST"])
def import_deck():
    if request.method == "POST":
        file = request.files.get("deck_file")
        deck_name = request.form.get("deck_name", "").strip().replace(" ", "-")

        if not file or not deck_name:
            return render_template("import.html", error="Please provide both a file and a deck name.")

        lines = file.read().decode("utf-8").splitlines()
        questions = detect_and_convert(lines, deck_name)

        if not questions:
            return render_template("import.html", error="No questions could be parsed. Check your file format.")

        output_path = f"questionbanks/{deck_name}.json"
        with open(output_path, "w") as f:
            json.dump(questions, f, indent=4)

        return redirect("/")

    return render_template("import.html", error=None)

if __name__ == "__main__":
    app.run(debug=True)