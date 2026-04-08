import json
import os
import sys

if len(sys.argv) != 3:
    print("Usage: python convert.py <input_file.txt> <output_name>")
    sys.exit(1)

input_file = sys.argv[1]
output_name = sys.argv[2]
output_path = f"questionbanks/{output_name}.json"

questions = []

with open(input_file, "r") as f:
    for line in f:
        line = line.strip().replace("\u00ad", "")
        if line.startswith("#") or not line:
            continue
        parts = line.split("\t")
        if len(parts) == 2:
            term, definition = parts
            questions.append({
                "subject": output_name.replace("-", " ").title(),
                "text": f"Define: {term}",
                "answer": definition
            })
        elif len(parts) >= 5:
            verb, conjugation, tense, _, context = parts[:5]
            context = context.strip()
            questions.append({
                "subject": output_name.replace("-", " ").title(),
                "text": f"What is the {tense} tense conjugation of '{verb}'? ({context})",
                "answer": conjugation
            })

with open(output_path, "w") as f:
    json.dump(questions, f, indent=4)

print(f"Converted {len(questions)} questions to {output_path}")