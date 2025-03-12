# UoWM CIS Dataset Extractor

This is a simple python script that extracts text from specific files from the UoWM site

It grabs the files, converts them to pdf if needed and then runs Tesseract on them to extract the text

## Running

### Install Tesseract

On Arch Based Systems:
```bash
sudo pacman -S tesseract
```

On Debian Based Systems:
```bash
sudo apt install tesseract-ocr
```

On Windows:

*Don't use Windows 😁*

### Install Python Dependencies and Run

```bash
pip install -r requirements.txt
python extractData.py
```