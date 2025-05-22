import os
import shutil
from model import *

# Setup paths
data_path = "data"
upload_path = "uploads"
os.makedirs(upload_path, exist_ok=True)  # Ensure uploads folder exists

# Initialize file splitter
splitter = FileCompressor(data_path)
splitter.split_files()

# Show detected files
print("TXT Files:", splitter.get_txt_files())
print("PDF Files:", splitter.get_pdf_files())
print("Image Files:", splitter.get_image_files())

# === TXT FILES ===
if splitter.get_txt_files():
    print("\n📄 Processing TXT Files...")
    txt_output_dir = "txt_bins"
    
    # Convert and save bin files
    splitter.convert_txt_files(txt_output_dir)
    
    #  Copy converted (bin) files only
    for file in os.listdir(txt_output_dir):
        if file.endswith(".bin"):  # Only copy .bin files
            shutil.copy(os.path.join(txt_output_dir, file), os.path.join(upload_path, file))

# === PDF FILES ===
if splitter.get_pdf_files():
    print("\n📕 Processing PDF Files...")
    pdf_processor = PDFProcessor(
        pdf_files=splitter.get_pdf_files(),
        bin_dir="pdf_bins",
        restore_dir="pdf_restored"
    )
    pdf_processor.process_all_pdfs()

    #  Copy only .bin files from PDF bin dir
    for file in os.listdir("pdf_bins"):
        if file.endswith(".bin"):
            shutil.copy(os.path.join("pdf_bins", file), os.path.join(upload_path, file))

# === IMAGE FILES ===
if splitter.get_image_files():
    print("\n🖼️ Processing Image Files...")
    img_processor = ImgProcessor(
        image_files=splitter.get_image_files(),
        bin_dir="img_bins",
        restore_dir="img_restored"
    )
    img_processor.convert_to_webp()
    img_processor.restore_from_webp()

    # Copy only .webp converted images (not original or restored)
    for file in os.listdir("img_bins"):
        if file.endswith(".webp"):
            shutil.copy(os.path.join("img_bins", file), os.path.join(upload_path, file))
