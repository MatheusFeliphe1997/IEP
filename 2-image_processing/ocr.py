import cv2
import pytesseract
from pytesseract import Output
from PIL import Image
import re
import os
from openai import OpenAI
from dotenv import load_dotenv

def load_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Error loading image {image_path}")
    return image

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
    return gray, thresh

def find_checkboxes(thresh):
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    min_checkbox_size = 15
    max_checkbox_size = 40
    processed_boxes = []
    checkbox_results = []

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if min_checkbox_size < w < max_checkbox_size and min_checkbox_size < h < max_checkbox_size and 0.8 < w/h < 1.2:
                already_processed = any(abs(px - x) < 5 and abs(py - y) < 5 for px, py, pw, ph in processed_boxes)
                if already_processed:
                    continue
                processed_boxes.append((x, y, w, h))
                checkbox_roi = thresh[y:y+h, x:x+w]
                filled_ratio = cv2.countNonZero(checkbox_roi) / (w * h)

                if filled_ratio > 0.4:
                    checkbox_results.append((x, y, w, h, "[X]"))
                else:
                    checkbox_results.append((x, y, w, h, "[ ]"))
                
    return checkbox_results

def extract_text(gray):
    return pytesseract.image_to_data(Image.fromarray(gray), output_type=Output.DICT, config=r'--oem 3 --psm 6')

def map_checkboxes_to_words(checkbox_results, data):
    checkbox_word_mapping = {}
    for cx, cy, w, h, checkbox_mark in checkbox_results:
        closest_word_idx = None
        min_distance = float('inf')

        for i in range(len(data['text'])):
            word = data['text'][i].strip()
            if not word:
                continue

            x = data['left'][i]
            y = data['top'][i]

            if abs(y - (cy + h // 2)) < 20:
                distance = abs(x - (cx + w // 2))
                if distance < min_distance:
                    min_distance = distance
                    closest_word_idx = i

        if closest_word_idx is not None:
            if closest_word_idx in checkbox_word_mapping:
                checkbox_word_mapping[closest_word_idx].append(checkbox_mark)
            else:
                checkbox_word_mapping[closest_word_idx] = [checkbox_mark]

    return checkbox_word_mapping

def compile_final_output(data, checkbox_word_mapping):
    final_output = []
    for i, word in enumerate(data['text']):
        word = word.strip()
        if word:
            if i in checkbox_word_mapping:
                final_output.append(" ".join(checkbox_word_mapping[i]) + " " + word)
            else:
                final_output.append(word)
    return final_output

def clean_text(text):
    text = re.sub(r'\b(Ml Yes|MlYes|MyYes|LYes|MYes|Ml Yes]|Yes])\b', 'Yes', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(Ml No|MyNo|MINo|LINo|No])\b', 'No', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(LJ|L]|C1|_J)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bBstateieiat\b', 'State', text, flags=re.IGNORECASE)
    text = re.sub(r'\bBtateieiat\b', 'State', text, flags=re.IGNORECASE)
    text = re.sub(r'\b@\b', '', text)
    text = re.sub(r'\b4\)\b', '', text)
    text = text.replace('¥', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def save_results(final_output, output_text_path):
    with open(output_text_path, 'w', encoding='utf-8') as text_file:
        text_file.write(" ".join(final_output))

def process_text(client, text):
    try:
        prompt = (
            
            "You will receive texts extracted from IEP documents, which have been processed as images with [X] and [] checkboxes. Your task is: to separate these texts into sections, including all information."
            "In summary, follow these guidelines:"
            "Separate the information in each section into separate paragraphs, keeping the sections clearly identified."
            "Each section must contain all relevant information, without additional summaries or edits."
            "Let's think step by step."
            "Expeted output (as markdown format):"
            "## Summary of the <section name> section"
            "<summary of the section>;"
            "## Summary of the <section name> section"
            "<summary of the section>;"
            "..."
            "## Summary of the <section name> section"
            "<summary of the section>;"

            f"Extracted text:\n{text}"
        )

        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You professionally separate texts for the IEP."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error during processing: {e}")
        return ""

def detect_filled_checkboxes_and_extract_text_from_folder(folder_path, output_text_path, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    all_texts = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            image = load_image(image_path)
            gray, thresh = preprocess_image(image)
            checkbox_results = find_checkboxes(thresh)
            data = extract_text(gray)
            checkbox_word_mapping = map_checkboxes_to_words(checkbox_results, data)
            final_output = compile_final_output(data, checkbox_word_mapping)
            final_output = [clean_text(line) for line in final_output]
            cleaned_text = process_text(client, " ".join(final_output))
            all_texts.append(cleaned_text)

    save_results(all_texts, output_text_path)
    print(f"Results saved to {output_text_path}")

# Example usage
folder_path = "Redacted_IEP_2_CA"
output_text_path = "extracted_2_CA.txt"
load_dotenv()
openai_api_key = os.getenv("KEY_OPENAI")


detect_filled_checkboxes_and_extract_text_from_folder(folder_path, output_text_path, openai_api_key)