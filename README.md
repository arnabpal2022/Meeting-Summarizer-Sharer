# AI MeetingNotes and Call-Transcript Summarizer
The Meeting Summarizer API is an AI-powered system designed to process meeting transcripts and generate intelligent summaries through retrieval-augmented generation (RAG). The system accepts text or PDF documents containing meeting transcripts, chunks the content for semantic search, and leverages large language models to produce contextually relevant summaries that can be shared via email.

## Key Workflows
#### Document Ingestion
- Client uploads PDF or text via POST /transcripts/
- System extracts text using app/utils/pdf.py
- Text is chunked using app/utils/text.py
- Chunks are stored as Chunk models in database
- FAISS vector index is built via RAGIndexService
#### Summary Generation
- Client requests summary via POST /summaries/
- RAGIndexService.query() retrieves relevant chunks
- LLMService.generate_summary() calls Groq API with context
- Generated summary is stored as Summary model
- Optional email sharing via EmailService.send_summary()

Installation Steps
To install this project, you'll need to set up the Python dependencies listed in the requirements file requirements.txt:1-78 . The typical installation process would be:

Create a virtual environment (recommended):
```bash
python -m venv venv  
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000 
```
#### Key Dependencies

- FastAPI for the web framework
- PyTorch for machine learning functionality
- Sentence Transformers for text processing
- Groq for AI model integration
- FAISS for vector similarity search

## Architecture 
<img width="1126" height="827" alt="image" src="https://github.com/user-attachments/assets/63bbcdea-0db1-45f8-9b4b-e9ffbe9850f0" />


