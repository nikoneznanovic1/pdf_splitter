import os
import uuid
import shutil
from tempfile import mkdtemp
from flask import Blueprint, request, render_template, send_file, abort, after_this_request, current_app
from werkzeug.utils import secure_filename
from docx2pdf import convert as docx2pdf_convert
from pdf2docx import Converter as PDF2DOCXConverter

tools_bp = Blueprint('tools', __name__)

ALLOWED_WORD_EXT = {'.docx'}
ALLOWED_PDF_EXT  = {'.pdf'}

def allowed_file(filename, allowed_exts):
    return os.path.splitext(filename.lower())[1] in allowed_exts

def unique_filename(filename):
    name, ext = os.path.splitext(secure_filename(filename))
    return f"{name}-{uuid.uuid4().hex}{ext}"

def cleanup_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.isfile(path):
        os.remove(path)

@tools_bp.route("/word-to-pdf", methods=["GET", "POST"])
def word_to_pdf():
    if request.method == "GET":
        size_bytes = current_app.config.get("MAX_CONTENT_LENGTH") or (50 * 1024 * 1024)
        max_size = size_bytes // (1024 * 1024)
        return render_template("word_to_pdf.html", max_size=max_size)

    if "file" not in request.files:
        abort(400, "No file uploaded")

    file = request.files["file"]
    if not allowed_file(file.filename, ALLOWED_WORD_EXT):
        abort(400, "Only .docx files are supported")

    tmpdir = mkdtemp(prefix="word2pdf_")
    input_path = os.path.join(tmpdir, unique_filename(file.filename))
    output_path = os.path.splitext(input_path)[0] + ".pdf"
    file.save(input_path)

    try:
        docx2pdf_convert(input_path, output_path)
    except Exception as e:
        cleanup_dir(tmpdir)
        abort(500, f"Conversion failed: {e}")

    @after_this_request
    def remove_files(response):
        cleanup_dir(tmpdir)
        return response

    return send_file(output_path, as_attachment=True)

@tools_bp.route("/pdf-to-word", methods=["GET", "POST"])
def pdf_to_word():
    if request.method == "GET":
        return render_template("pdf_to_word.html")

    if "file" not in request.files:
        abort(400, "No file uploaded")

    file = request.files["file"]
    if not allowed_file(file.filename, ALLOWED_PDF_EXT):
        abort(400, "Only .pdf files are supported")

    tmpdir = mkdtemp(prefix="pdf2word_")
    input_path = os.path.join(tmpdir, unique_filename(file.filename))
    output_path = os.path.splitext(input_path)[0] + ".docx"
    file.save(input_path)

    try:
        cv = PDF2DOCXConverter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
    except Exception as e:
        cleanup_dir(tmpdir)
        abort(500, f"Conversion failed: {e}")

    @after_this_request
    def remove_files(response):
        cleanup_dir(tmpdir)
        return response

    return send_file(output_path, as_attachment=True)
