from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import io
import PyPDF2

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files.get("pdf")
        if not uploaded_file or uploaded_file.filename == "":
            return "No PDF uploaded.", 400

        filename = secure_filename(uploaded_file.filename)
        file_bytes = uploaded_file.read()

        # Very simple PDF text extraction (placeholder for your real logic)
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            all_text = ""
            for page in pdf_reader.pages:
                all_text += page.extract_text() or ""

            # For now, just show the first 1000 characters
            preview = all_text[:1000]

        except Exception as e:
            preview = f"Could not parse PDF text. Error: {e}"

        # Later, this is where we'll turn the text into deadlines / filenames.
        return render_template(
            "result.html",
            filename=filename,
            text_preview=preview
        )

    # GET request: show upload form
    return render_template("index.html")

# This is only used when running locally; Render will use gunicorn.
if __name__ == "__main__":
    app.run(debug=True)
