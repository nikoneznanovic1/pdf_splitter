from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        pdf_reader = PdfReader(pdf_file)
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for i, page in enumerate(pdf_reader.pages):
                pdf_writer = PdfWriter()
                pdf_writer.add_page(page)
                output = io.BytesIO()
                pdf_writer.write(output)
                output.seek(0)
                zipf.writestr(f"page_{i+1}.pdf", output.read())

        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name="split_pages.zip")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
