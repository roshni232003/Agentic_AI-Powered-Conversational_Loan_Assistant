import pytesseract
from PIL import Image


def verify_document(image_path):
    image = Image.open(image_path)

    extracted_text = pytesseract.image_to_string(image)

    keywords = ["AADHAR", "PAN", "GOVERNMENT"]

    verified = any(word in extracted_text.upper() for word in keywords)

    return {
        "verified": verified,
        "text": extracted_text
    }
