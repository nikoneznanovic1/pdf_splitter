from flask import Flask, render_template, request, send_file
from flask import Flask, render_template, request, redirect, url_for, flash
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io, zipfile, os
import fitz  # PyMuPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "mail.pdfhub.org"  # npr. mail.neoserv.si ali smtp.gmail.com
SMTP_PORT = 587  # ali 465 za SSL
SMTP_USERNAME = "info@pdfhub.org"  # tvoj e-naslov
SMTP_PASSWORD = "neznanovski111"  # geslo za SMTP ali app password
TO_EMAIL = "info@pdfhub.org"  # kam naj grejo kontaktna sporočila

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/split-pdf")
def split_pdf_page():
    return render_template("split.html")

@app.route("/merge-pdf")
def merge_pdf_page():
    return render_template("merge.html")

@app.route("/compress-pdf")
def compress_pdf_page():
    return render_template("compress.html")

@app.route("/convert-pdf")
def convert_pdf_page():
    return render_template("convert.html")

@app.route("/watermark-pdf")
def watermark_pdf_page():
    return render_template("watermark.html")

# ------------------- API ROUTES -------------------

@app.route("/api/split-pdf", methods=["POST"])
def api_split_pdf():
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
    return send_file(zip_buffer, as_attachment=True, download_name="split_pages.zip", mimetype="application/zip")

@app.route("/api/merge-pdf", methods=["POST"])
def api_merge_pdf():
    files = request.files.getlist("pdfs")
    pdf_writer = PdfWriter()

    for file in files:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    output = io.BytesIO()
    pdf_writer.write(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="merged.pdf", mimetype="application/pdf")

@app.route("/api/compress-pdf", methods=["POST"])
def api_compress_pdf():
    pdf_file = request.files["pdf"]
    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()

    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    output = io.BytesIO()
    pdf_writer.write(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="compressed.pdf", mimetype="application/pdf")

@app.route("/api/convert-pdf", methods=["POST"])
def api_convert_pdf():
    pdf_file = request.files["pdf"]
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            img_bytes = io.BytesIO(pix.tobytes("png"))
            zipf.writestr(f"page_{i+1}.png", img_bytes.read())

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name="pdf_images.zip", mimetype="application/zip")

@app.route("/api/watermark-pdf", methods=["POST"])
def api_watermark_pdf():
    pdf_file = request.files["pdf"]
    watermark_text = request.form.get("watermark")
    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()

    for page in pdf_reader.pages:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 40)
        can.setFillGray(0.5, 0.5)
        can.drawString(100, 500, watermark_text)
        can.save()

        packet.seek(0)
        watermark_reader = PdfReader(packet)
        page.merge_page(watermark_reader.pages[0])
        pdf_writer.add_page(page)

    output = io.BytesIO()
    pdf_writer.write(output)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="watermarked.pdf", mimetype="application/pdf")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        try:
            msg = MIMEMultipart()
            msg["From"] = SMTP_USERNAME
            msg["To"] = TO_EMAIL
            msg["Subject"] = f"Contact Form: {subject}"

            body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()

            return render_template("contact.html", success=True)
        except Exception as e:
            print("Email sending error:", e)
            return render_template("contact.html", error=True)

    return render_template("contact.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

# Če delam lokalno
# if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 5000))
#    app.run(host="0.0.0.0", port=port)

# Če dam na Render
if __name__ == "__main__":
    app.run()