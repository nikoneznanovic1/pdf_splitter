from flask import Flask, render_template, request, send_file, send_from_directory, redirect, Response, url_for, flash
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io, zipfile, os
import fitz  # PyMuPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from tools import tools_bp  # Uvozimo blueprint tools.py

from routes_config import get_all_urls  # <- uvoz konfiguracije iz routes_config.py

SMTP_SERVER = "mail.pdfhub.org"  # npr. mail.neoserv.si ali smtp.gmail.com
SMTP_PORT = 587  # ali 465 za SSL
SMTP_USERNAME = "info@pdfhub.org"  # tvoj e-naslov
SMTP_PASSWORD = "neznanovski111"  # geslo za SMTP ali app password
TO_EMAIL = "info@pdfhub.org"  # kam naj grejo kontaktna sporočila

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
app.register_blueprint(tools_bp)  # Registracija orodij

@app.before_request
def redirect_to_www():
    if request.host == "pdfhub.org":
        return redirect("https://www.pdfhub.org" + request.full_path, code=301)

@app.route('/google8049692bb0d0557a.html')
def google_verification():
    return send_from_directory('static', 'google8049692bb0d0557a.html')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

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

@app.route('/featured')
def featured():
    return render_template('featured.html')

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

@app.route('/blog')
def blog_index():
    return render_template('blog/index.html')

@app.route('/blog/how-to-merge-pdfs')
def blog_merge_pdfs():
    return render_template('blog/how_to_merge_pdfs.html')

@app.route('/blog/top-free-pdf-editors')
def blog_pdf_editors():
    return render_template('blog/top_free_pdf_editors.html')

@app.route('/blog/how-to-compress-pdfs')
def blog_compress_pdfs():
    return render_template('blog/how_to_compress_pdfs.html')

@app.route('/blog/how-to-split-pdf-online-guide')
def blog_split_pdf():
    return render_template('blog/how_to_split_pdf_online.html')

@app.route('/blog/best-ai-pdf-tools-2025')
def blog_ai_pdf_tools():
    return render_template('blog/best_ai_pdf_tools_2025.html')

@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    today = date.today().isoformat()
    base = request.url_root.rstrip("/")

    urls = get_all_urls()

    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for u in urls:
        loc = f"{base}{u['path']}"
        # home (/) naj ostane z zaključenim /, ostalo brez trailing /
        loc = loc if u["path"] == "/" else loc.rstrip("/")
        xml_parts.append("  <url>")
        xml_parts.append(f"    <loc>{loc}</loc>")
        xml_parts.append(f"    <lastmod>{today}</lastmod>")
        xml_parts.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        xml_parts.append(f"    <priority>{u['priority']}</priority>")
        xml_parts.append("  </url>")

    xml_parts.append("</urlset>")
    return Response("\n".join(xml_parts), mimetype="application/xml")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
