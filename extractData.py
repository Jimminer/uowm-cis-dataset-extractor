from PIL import Image
import pdf2image
import pytesseract
import tempfile
import time
import os

import getPdfs

def pdfToImage(pdf: str, temp: str):
    images = pdf2image.convert_from_path(f"pdfs/{pdf}", dpi=200)
    for i, image in enumerate(images):
        image.save(f"{temp}/{pdf[:-4]}_{i:04}.png")

    return len(images)

def imageToText(image: str):
    return pytesseract.image_to_string(Image.open(image), lang="ell+eng", config="--tessdata-dir ./tessdata --psm 6")

if __name__ == '__main__':
    if not os.path.exists("pdfs"):
        os.mkdir("pdfs")

    if not os.path.exists("output"):
        os.mkdir("output")

    if not os.listdir("pdfs"):
        getPdfs.downloadPdfs()

    # convert all pdfs to images and extract text
    with tempfile.TemporaryDirectory() as temp:
        for pdf in os.listdir("pdfs"):
            if pdf.endswith(".pdf"):
                print(f"Converting {pdf} to images...")
                pdfToImage(pdf, temp)
                print(f"{pdf} converted successfully!")

            with open(f"output/{pdf[:-4]}.txt", "w") as file:
                for image in sorted(os.listdir(temp)):
                    if f"{pdf[:-4]}" not in image:
                        continue

                    text = imageToText(f"{temp}/{image}")
                    file.write(text)

                    print(f"Text extracted from {image} successfully!")

                print(f"Text extracted from {pdf} successfully!")