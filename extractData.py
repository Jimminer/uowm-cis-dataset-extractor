from PIL import Image
import pdf2image
import pytesseract
import tempfile
import os
import re

import getPdfs

def pdfToImage(pdf_path: str, temp_dir: str):
    images = pdf2image.convert_from_path(pdf_path, dpi=300)
    image_paths = []

    for i, image in enumerate(images):
        img_name = f"{os.path.basename(pdf_path)[:-4]}_{i:04}.png"
        full_path = os.path.join(temp_dir, img_name)
        image.save(full_path)
        image_paths.append(full_path)

    return image_paths

def imageToText(image_path: str):
    return pytesseract.image_to_string(
        Image.open(image_path),
        lang="ell+eng",
        config="--tessdata-dir ./tessdata --psm 6"
    )

def cleanText(text: str):
    # Normalize newlines first
    text = re.sub(r"\r\n|\r", "\n", text)

    # Remove long lines of symbols or non-alphanumerics (fake dividers, OCR junk)
    text = re.sub(r"[^Α-Ωα-ωΆ-ώA-Za-z0-9\s.,;:?!@%&/()\"'\[\]\-+=€$£<>|{}\n]", "", text)

    # Remove repeated garbage sequences (e.g. "οοοοοο", "τττττ", etc.)
    text = re.sub(r"([^\W\d_])\1{3,}", r"\1", text)

    # Fix common OCR errors
    text = text.replace("|||", " | ")
    text = text.replace("||", " | ")
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    text = text.replace(" :", ":")
    text = text.replace(" ;", ";")
    text = text.replace("..", ".")

    # Clean extra whitespace
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

def extractPdfText(pdf_file: str, temp_dir: str) -> str:
    images = pdfToImage(f"pdfs/{pdf_file}", temp_dir)
    full_text = ""

    for image_path in images:
        text = imageToText(image_path)
        cleaned = cleanText(text)

        # Skip pages that are mostly empty or junk
        if len(cleaned.split()) < 10:
            continue

        full_text += cleaned + "\n\n"

    return full_text

if __name__ == '__main__':
    os.makedirs("pdfs", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    if not os.listdir("pdfs"):
        getPdfs.downloadPdfs()

    with tempfile.TemporaryDirectory() as temp_dir:
        for pdf in os.listdir("pdfs"):
            if not pdf.endswith(".pdf"):
                continue

            print(f"Processing {pdf}...")

            try:
                text = extractPdfText(pdf, temp_dir)
                with open(f"output/{pdf[:-4]}.txt", "w", encoding="utf-8") as f:
                    f.write(text)

                print(f"Finished extracting {pdf}!\n")
            except Exception as e:
                print(f"Failed processing {pdf}: {e}")
