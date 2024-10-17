# Introduction
This project focuses on developing applications that read and interpret unstructured documents, such as PDFs and images. Utilizing tools like Langchain and LLMs, including Llama3 and GPT-4, the system transforms textual content into useful information.

# The project workflow involves the following steps:

Text Extraction: The system converts PDF files into text, generating a .txt file with the extracted content.
Storage in Vector Database: The extracted information is stored in ChromaDB, a vector database that enables efficient searching.
Search and Response Generation: Using techniques like Retrieval-Augmented Generation (RAG), searches are performed with embeddings to obtain precise answers.
Response Processing: The responses are processed and returned in a .json file, facilitating the subsequent use of the information.
The project also applies prompt engineering techniques, such as Chain-of-Thought (CoT) and Tree-of-Thought (ToT), to optimize interaction with the language model.

#Prerequisites
Before getting started, ensure you have Python and pip installed on your system. You will also need an OpenAI key.

# Step-by-Step Guide
1. Clone the Repository
Clone the repository to your computer using the following command:

git clone

2. Set Up the Environment
Create a .env file in the root of the project and add your OpenAI key:

KEY_OPENAI = "your_key_here"

3. Install Dependencies
Install the required libraries by running the following commands:

pip install opencv-python pytesseract Pillow openai python-dotenv
pip install chromadb

4. Add the PDF
Place your PDF file in the pdf_to_image folder.

5. Convert the PDF to Images
Open the pdf_to_jpg.py file and modify the pdf_path variable to the name of your PDF file:

pdf_path = 'pdf_to_image/your.pdf'

Run the script to generate the images:

python pdf_to_jpg.py

This will create a folder containing images of each page of your PDF.

6. Image Processing with OCR
Navigate to the image_processing folder and open the ocr.py file. Change the folder_path variable to point to the folder created from the PDF:

folder_path = "pdf_to_image/created_folder"

Run the script to generate a .txt file with the extracted text from the PDF:

python ocr.py

7. Create Embeddings
Go to the embedding folder and open the create_db_embedding.py file. Change the following variables:

chroma_client = chromadb.PersistentClient(path='your_database_name')
collection = chroma_client.get_or_create_collection(name="your_collection_name")
with open('image_processing/your_file.txt'

Run the script to create a new folder with the name of your database and a collection containing the information from your .txt file in embedding format:

python create_db_embedding.py

8. Query Data
Access the query_and_response folder and open the iep_assistant.py file. Change the variables to your database and collection names:

chroma_client = chromadb.PersistentClient(path='iap_db')
collection_name = "2ca"

Run the script:

python iep_assistant.py

When prompted, type your question and press Enter. The system will return an answer and create a .json file with the same name as the collection.

9. Utilize the JSON File
You can now use the generated .json file as needed.

# Conclusion
Follow these steps to successfully set up and operate the system. For any questions or issues, refer to the documentation of the libraries used or contact the repository maintainer.