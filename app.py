from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import io
import PyPDF2
import re
import datetime

app = Flask(__name__)

MONTH_REGEX = r"(January|February|March|April|May|June|July|August|September|October|November|December)"
DATE_PATTERNS = [
    re.compile(rf"\b{MONTH_REGEX}\s+\d{{1,2}},\s+\d{{4}}\b"),
    re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),
]


def parse_date_str(s: str):
    """Try a few common date formats and return a date object or None."""
    for fmt in ("%B %d, %Y", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def extract_trial_and_deadlines(text: str):
    """
    Very simple v0:
    - Look for a line containing the word 'trial' plus a date.
    - Use that as the trial date.
    - Generate a couple of sample deadlines before trial.
    """
    trial_date = None
    lines = text.splitlines()

    for line in lines:
        if "trial" in line.lower():
            for pattern in DATE_PATTERNS:
                match = pattern.search(line)
                if match:
                    d = parse_date_str(match.group(0))
                    if d:
                        trial_date = d
                        break
            if trial_date:
                break

    deadlines = []
    if trial_date:
        def add_event(label: str, date_obj: datetime.date):
            deadlines.append(
                {
                    "label": label,
                    "date_str": date_obj.strftime("%m/%d/%Y"),
                    "weekday": date_obj.strftime("%A"),
                }
            )

        add_event("Trial", trial_date)
        add_event("Sample deadline 60 days before trial", trial_date - datetime.timedelta(days=60))
        add_event("Sample deadline 30 days before trial", trial_date - datetime.timedelta(days=30))

    return trial_date, deadlines


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files.get("pdf")
        if not uploaded_file or uploaded_file.filename == "":
            return "No PDF uploaded.", 400

        filename = secure_filename(uploaded_file.filename)
        file_bytes = uploaded_file.read()

        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            all_text = ""
            for page in pdf_reader.pages:
                all_text += page.extract_text() or ""

            preview = all_text[:1000]

        except Exception as e:
            all_text = ""
            preview = f"Could not parse PDF text. Error: {e}"

        trial_date, deadlines = extract_trial_and_deadlines(all_text)

        return render_template(
            "result.html",
            filename=filename,
            text_preview=preview,
            deadlines=deadlines,
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
