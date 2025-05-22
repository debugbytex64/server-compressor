from model import *

data_path = "data"
splitter = FileCompressor(data_path)
splitter.split_files()

# List detected files
print("TXT Files:", splitter.get_txt_files())
print("PDF Files:", splitter.get_pdf_files())
print("Image Files:", splitter.get_image_files())

# Process TXT files (convert and restore)
if splitter.get_txt_files():
    print("\n📄 Processing TXT Files...")
    txt_output_dir = "txt_bins"
    file_lengths = splitter.convert_txt_files(txt_output_dir)
    restored_texts = splitter.restore_txt_files(txt_output_dir)
    for orig, restored in restored_texts.items():
        print(f"\nOriginal: {orig}\nRestored: {restored}\n")

# Process PDF files
if splitter.get_pdf_files():
    print("\n📕 Processing PDF Files...")
    pdf_processor = PDFProcessor(
        pdf_files=splitter.get_pdf_files(),
        bin_dir="pdf_bins",
        restore_dir="pdf_restored"
    )
    pdf_processor.process_all_pdfs()

# Process Image files
if splitter.get_image_files():
    print("\n🖼️ Processing Image Files...")
    img_processor = ImgProcessor(
        image_files=splitter.get_image_files(),
        bin_dir="img_bins",
        restore_dir="img_restored"
    )
    img_processor.convert_to_webp()
    img_processor.restore_from_webp()
    orig, webp, restored = img_processor.get_visual_paths()
    print(f"\nFirst visual files:\n- Original: {orig}\n- WebP: {webp}\n- Restored: {restored}")
