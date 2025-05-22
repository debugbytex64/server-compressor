import os
import numpy as np
import tiktoken
import matplotlib.pyplot as plt
from tqdm import tqdm
import zstandard as zstd 
import msgpack
import subprocess
import fitz
from PIL import Image

# Initialize the GPT-2 tokenizer
enc = tiktoken.get_encoding("gpt2")

class FileCompressor:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.txt_files = []
        self.pdf_files = []
        self.image_files = []
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    def split_files(self):
        if not os.path.isdir(self.directory_path):
            raise ValueError(f"The path '{self.directory_path}' is not a valid directory.")
        for filename in os.listdir(self.directory_path):
            full_path = os.path.join(self.directory_path, filename)
            if os.path.isfile(full_path):
                _, ext = os.path.splitext(filename)
                ext = ext.lower()
                if ext == '.txt':
                    self.txt_files.append(full_path)
                elif ext == '.pdf':
                    self.pdf_files.append(full_path)
                elif ext in self.image_extensions:
                    self.image_files.append(full_path)

    """Start of TXT file conversion"""
    def convert_txt_files(self, output_dir):
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        file_lengths = {}  # token count per file
        for txt_file in self.txt_files:
            with open(txt_file, 'r', encoding='utf-8') as f:
                text = f.read()
            token_ids = enc.encode_ordinary(text)
            token_ids.append(enc.eot_token)
            file_lengths[txt_file] = len(token_ids)
            # Save token IDs to a .bin file with same base name as original
            base = os.path.splitext(os.path.basename(txt_file))[0]
            bin_path = os.path.join(output_dir, base + ".bin")
            arr = np.array(token_ids, dtype=np.uint16)
            arr.tofile(bin_path)
            print(f"✔️ Converted and saved: {bin_path} ({len(token_ids)} tokens)")
        return file_lengths

    def restore_txt_files(self, bin_dir):
        restored_texts = {}
        for txt_file in self.txt_files:
            base = os.path.splitext(os.path.basename(txt_file))[0]
            bin_path = os.path.join(bin_dir, base + ".bin")
            if not os.path.exists(bin_path):
                print(f"❌ Missing binary file for: {txt_file}")
                continue
            arr = np.fromfile(bin_path, dtype=np.uint16)
            # Remove the final EOT token if present
            if arr[-1] == enc.eot_token:
                arr = arr[:-1]
            text = enc.decode(arr.tolist())
            restored_path = os.path.join(bin_dir, base + "_restored.txt")
            with open(restored_path, 'w', encoding='utf-8') as f:
                f.write(text)
            restored_texts[txt_file] = restored_path
            print(f"🔁 Restored text saved to: {restored_path}")
        return restored_texts
    """End of TXT file conversion"""

    def get_txt_files(self):
        return self.txt_files

    def get_pdf_files(self):
        return self.pdf_files

    def get_image_files(self):
        return self.image_files

"""Start of PDF file conversion"""
class PDFProcessor:
    GHOSTSCRIPT_PATH = r'C:\Program Files\gs\gs10.05.0\bin\gswin64c.exe'
    COMPRESSION_LEVEL = 22

    GHOSTSCRIPT_OPTIONS = [
        "-dPDFSETTINGS=/ebook",
        "-dColorImageResolution=72",
        "-dGrayImageResolution=72",
        "-dMonoImageResolution=72",
        "-dDownsampleColorImages=true",
        "-dDownsampleGrayImages=true",
        "-dDownsampleMonoImages=true",
        "-dAutoFilterColorImages=false",
        "-dAutoFilterGrayImages=false",
        "-dColorImageDownsampleType=/Bicubic",
        "-dGrayImageDownsampleType=/Bicubic",
        "-dMonoImageDownsampleType=/Bicubic"
    ]

    def __init__(self, pdf_files: list[str], bin_dir: str, restore_dir: str):
        self.pdf_files = pdf_files
        self.bin_dir = bin_dir
        self.restore_dir = restore_dir
        # Create bin and restore directories if they don't exist
        os.makedirs(self.bin_dir, exist_ok=True)
        os.makedirs(self.restore_dir, exist_ok=True)

    @staticmethod
    def format_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    def optimize_with_ghostscript(self, input_path: str, output_path: str) -> None:
        input_path = os.path.abspath(input_path)
        output_path = os.path.abspath(output_path)
        if not os.path.exists(self.GHOSTSCRIPT_PATH):
            raise FileNotFoundError(f"Ghostscript not found at {self.GHOSTSCRIPT_PATH}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cmd = [
            f'"{self.GHOSTSCRIPT_PATH}"',
            '-q',
            '-dNOPAUSE',
            '-dBATCH',
            '-sDEVICE=pdfwrite',
            f'-sOutputFile="{output_path}"',
            *self.GHOSTSCRIPT_OPTIONS,
            f'"{input_path}"'
        ]
        print(f"\n🔧 Running Ghostscript on: {input_path}")
        subprocess.run(" ".join(cmd), check=True, shell=True)
        if not os.path.exists(output_path):
            raise RuntimeError("Optimized PDF not created")

    def pdf_to_bin(self, pdf_path: str, bin_path: str) -> float:
        temp_pdf = "temp_optimized.pdf"
        try:
            self.optimize_with_ghostscript(pdf_path, temp_pdf)
            with open(temp_pdf, "rb") as f:
                optimized_bytes = f.read()
            cctx = zstd.ZstdCompressor(level=self.COMPRESSION_LEVEL)
            compressed = cctx.compress(optimized_bytes)
            data = {
                "zstd_compressed": compressed,
                "original_size": os.path.getsize(pdf_path),
                "optimized_size": len(optimized_bytes)
            }
            with open(bin_path, "wb") as f:
                f.write(msgpack.packb(data))
            return os.path.getsize(bin_path)
        finally:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)

    def bin_to_pdf(self, bin_path: str, output_path: str) -> None:
        if not os.path.exists(bin_path):
            raise FileNotFoundError(f"Compressed file not found: {bin_path}")
        with open(bin_path, "rb") as f:
            data = msgpack.unpackb(f.read())
        if 'zstd_compressed' not in data:
            raise ValueError("Invalid compressed data format")
        dctx = zstd.ZstdDecompressor()
        restored = dctx.decompress(data["zstd_compressed"])
        with open(output_path, "wb") as f:
            f.write(restored)

    def print_stats(self, original_path: str, bin_path: str, optimized_size: int):
        original_size = os.path.getsize(original_path)
        compressed_size = os.path.getsize(bin_path)
        reduction = original_size - compressed_size
        print(f"\n📊 Stats for {os.path.basename(original_path)}")
        print(f"• Original PDF Size:   {self.format_size(original_size)}")
        print(f"• Optimized PDF Size:  {self.format_size(optimized_size)}")
        print(f"• Final .bin Size:     {self.format_size(compressed_size)}")
        print(f"🔥 Total Reduction: {self.format_size(reduction)} ({reduction/original_size*100:.1f}%)")

    def process_all_pdfs(self):
        for pdf_path in self.pdf_files:
            if not os.path.exists(pdf_path):
                print(f"❌ File not found: {pdf_path}")
                continue
            base = os.path.splitext(os.path.basename(pdf_path))[0]
            bin_path = os.path.join(self.bin_dir, base + ".bin")
            restored_path = os.path.join(self.restore_dir, base + "_restored.pdf")
            try:
                final_size = self.pdf_to_bin(pdf_path, bin_path)
                self.print_stats(pdf_path, bin_path, final_size)
                self.bin_to_pdf(bin_path, restored_path)
                with fitz.open(restored_path) as doc:
                    print(f"✅ Restoration OK: {base}. Pages: {len(doc)}")
            except Exception as e:
                print(f"❌ Error processing {base}: {e}")
                for path in [bin_path, restored_path]:
                    if os.path.exists(path):
                        os.remove(path)
"""End of PDF file conversion"""

"""Start of Image file conversion"""
class ImgProcessor:
    def __init__(self, image_files: list[str], bin_dir: str, restore_dir: str):
        self.image_files = image_files  # list of full image paths
        self.bin_dir = bin_dir
        self.restore_dir = restore_dir
        os.makedirs(self.bin_dir, exist_ok=True)
        os.makedirs(self.restore_dir, exist_ok=True)
        self.first_original_path = None
        self.first_webp_path = None
        self.first_restored_path = None

    def convert_to_webp(self):
        total_original_size = 0
        total_webp_size = 0
        for file_path in self.image_files:
            filename = os.path.basename(file_path)
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                original_size = os.path.getsize(file_path)
                total_original_size += original_size
                image = Image.open(file_path).convert("RGB")
                # Save converted file with the same base name but .webp extension
                base = os.path.splitext(filename)[0]
                webp_path = os.path.join(self.bin_dir, base + ".webp")
                image.save(webp_path, format="WEBP", quality=80)
                webp_size = os.path.getsize(webp_path)
                total_webp_size += webp_size
                if self.first_original_path is None:
                    self.first_original_path = file_path
                    self.first_webp_path = webp_path
        print("\n[WebP Conversion Summary]")
        print(f"Total Original Size: {total_original_size / 1024:.2f} KB")
        print(f"Total WebP Size: {total_webp_size / 1024:.2f} KB")
        if total_original_size > 0:
            size_ratio = (total_webp_size / total_original_size) * 100
            print(f"Compression Ratio: {size_ratio:.2f}%")
            print(f"Size Reduction: {100 - size_ratio:.2f}%")
        else:
            print("No valid images found.")

    def restore_from_webp(self):
        for filename in os.listdir(self.bin_dir):
            if filename.lower().endswith('.webp'):
                base = os.path.splitext(filename)[0]
                webp_path = os.path.join(self.bin_dir, filename)
                # Save restored image with same base name and .jpg extension
                restored_path = os.path.join(self.restore_dir, base + "_restored.jpg")
                restored_image = Image.open(webp_path).convert("RGB")
                restored_image.save(restored_path, format="JPEG", quality=95)
                if self.first_restored_path is None:
                    self.first_restored_path = restored_path
        print("\n[Restoration Completed] Images restored to:", self.restore_dir)

    def get_visual_paths(self):
        return self.first_original_path, self.first_webp_path, self.first_restored_path
"""End of Image file conversion"""


