import os
from pdf2image import convert_from_path

# Path to the PDF file
pdf_path = 'ocr_pdf/Redacted_IEP_4_TX.pdf'  # Replace with your PDF file

# Create a folder with the name of the PDF (without extension)
pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
output_folder = pdf_name

# Create the folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Convert PDF to images
images = convert_from_path(pdf_path)

# Save each page as a JPG image
for i, image in enumerate(images):
    image_path = os.path.join(output_folder, f'{pdf_name}_page_{i + 1}.jpg')
    image.save(image_path, 'JPEG')
    print(f'Page {i + 1} saved as: {image_path}')