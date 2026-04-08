import json

questions = []

with open("psych.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        parts = line.split("\t")
        if len(parts) == 2:
            term, definition = parts
            questions.append({
                "subject": "AP Psychology",
                "text": f"Define: {term}",
                "answer": definition
            })

with open("questions.json", "w") as f:
    json.dump(questions, f, indent=4)

print(f"Converted {len(questions)} questions successfully!")
