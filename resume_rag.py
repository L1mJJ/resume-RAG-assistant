from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import os
import re

from google import genai
from dotenv import load_dotenv


# ============================================================
# GEMINI and DOTENV SETUP
# ============================================================
load_dotenv()

client = genai.Client()

# ============================================================
# GEMINI OCR FALLBACK
# ============================================================
def extract_text_with_gemini(pdf_path):

    print("\nNo text found with pypdf.")
    print("Using Gemini to extract text from PDF...")

    uploaded_file = client.files.upload(
        file=pdf_path
    )

    prompt = """
Extract all text from this resume.

Return only the resume content as plain text.
Do not summarize it.
Do not add explanations.

Preserve important information such as:
- Name
- Contact information
- Education
- Work experience
- Projects
- Skills
- Certifications
- Achievements

If the document contains text inside images,
read and transcribe that text as well.
"""
   
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[prompt, uploaded_file]
    )

    return response.text

# ============================================================
# EMAIL EXTRACTION
# ============================================================
def extract_email(text):

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

    match = re.search(email_pattern, text)

    if match:
        return match.group(0).lower()

    return None

# ============================================================
# LOAD PDF
# ============================================================
pdf_path = input("Enter the path to the resume PDF: ").strip()

if not os.path.exists(pdf_path):
    print("Error: Resume PDF not found.")
    exit()

if not pdf_path.lower().endswith(".pdf"):
    print("Error: Please provide a PDF file.")
    exit()

reader = PdfReader(pdf_path)

# ============================================================
# EXTRACT TEXT USING PYPDF
# ============================================================
print(f"\nNumber of pages: {len(reader.pages)}")

text = ""

for i, page in enumerate(reader.pages):
    page_text = page.extract_text() or ""
    print(f"Page {i + 1}: {len(page_text)} characters")

    text += page_text + "\n"

# ============================================================
# CLEAN TEXT
# ============================================================
def clean_text(text):

    lines = []

    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    return "\n".join(lines)

text = clean_text(text)

print("\nTEXT EXTRACTION COMPLETE")
print(f"Characters extracted: {len(text)}")

# ============================================================
# GEMINI OCR FALLBACK
# ============================================================
if not text.strip():

    text = extract_text_with_gemini(pdf_path)
    text = clean_text(text)
    print(f"Characters extracted with Gemini: {len(text)}")

    if not text.strip():
        print("Error: Gemini could not extract any text from this PDF.")
        exit()

# ============================================================
# IDENTIFY CANDIDATE
# ============================================================
email = extract_email(text)

if not email:
    print("Error: No email address could be found in the resume.")
    exit()
print(f"Candidate email: {email}")

# ============================================================
# SPLIT TEXT INTO CHUNKS
# ============================================================
def chunk_text(text, chunk_size=60):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

chunks = chunk_text(text)

if not chunks:
    print("Error: No chunks were created from the resume.")
    exit()

print("\nResume loaded.")
print(f"Created {len(chunks)} chunks.")

# ============================================================
# CREATE EMBEDDINGS
# ============================================================
print("\nCreating embeddings...")

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)

print(f"Embedding shape: {embeddings.shape}")

# ============================================================
# STORE IN CHROMADB
# ============================================================
print("\nConnecting to ChromaDB...")

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

# Use the candidate's email as their unique identifier
candidate_id = email.replace("@", "_at_").replace(".", "_")
collection_name = f"candidate_{candidate_id}"

print(f"Collection name: {collection_name}")

# ============================================================
# REPLACE OLD RESUME FOR SAME CANDIDATE
# ============================================================
try:
    chroma_client.delete_collection(collection_name)
    print("Existing candidate collection found.")
    print("Replacing it with the updated resume.")

except Exception:
    print("No existing collection found.")
    print("Creating a new candidate collection.")

# ============================================================
# CREATE COLLECTION
# ============================================================
collection = chroma_client.create_collection(
    name=collection_name
)

# ============================================================
# ADD CHUNKS TO CHROMADB
# ============================================================
collection.add(
    ids=[
        f"chunk_{i}"
        for i in range(len(chunks))
    ],
    documents=chunks,
    embeddings=embeddings.tolist()
)

print(
    f"\nResume stored in ChromaDB collection: "
    f"{collection_name}"
)

# ============================================================
# SHOW CURRENT COLLECTIONS
# ============================================================
print("\n--- CHROMADB COLLECTIONS ---")

collections = chroma_client.list_collections()

for c in collections:
    print(f"- {c.name}")

# ============================================================
# ASK QUESTION
# ============================================================

question = input(
    "\nAsk a question about the resume: "
)

# ============================================================
# EMBED QUESTION
# ============================================================
question_embedding = model.encode(
    [question]
)

# ============================================================
# RETRIEVE RELEVANT CHUNKS
# ============================================================
results = collection.query(
    query_embeddings=question_embedding.tolist(),
    n_results=3
)

retrieved_chunks = results["documents"][0]

# ============================================================
# DISPLAY RETRIEVED CONTEXT
# ============================================================
print("\n--- RETRIEVED CONTEXT ---")

for i, chunk in enumerate(
    retrieved_chunks,
    start=1
):
    print(f"\nChunk {i}:")
    print(chunk)

context = "\n\n".join(
    retrieved_chunks
)

# ============================================================
# SEND CONTEXT + QUESTION TO GEMINI
# ============================================================
prompt = f"""
You are a resume assistant.

Answer the user's question using ONLY the information
provided in the resume context below.

Do not use outside knowledge.
Do not make assumptions.
Do not invent information.

If the answer cannot be found in the resume context,
say:

"The information is not available in the resume."

Resume context:

{context}

User question:

{question}
"""

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt
)

# ============================================================
# DISPLAY ANSWER
# ============================================================
print("\n--- ANSWER ---")
print(response.text)