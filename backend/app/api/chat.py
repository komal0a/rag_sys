from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.deps import get_db, get_current_user
from sqlalchemy.orm import Session
from app.services.retrieval import Retriever
from app.services.llm import get_provider
from app import models

router = APIRouter()

DEFAULT_CHAT_TOP_K = 5
MAX_CONTEXT_CHUNK_CHARS = 3000


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    document_id: Optional[int] = None
    top_k: Optional[int] = DEFAULT_CHAT_TOP_K
    conversation_id: Optional[int] = None


@router.post('/chat')
def chat(req: ChatRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # enforce ownership if document_id provided
    if req.document_id:
        doc = db.query(models.Document).filter(models.Document.id == req.document_id).first()
        if not doc or doc.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Document not found")

    retriever = Retriever(db)
    retrieval = retriever.retrieve(req.query, top_k=req.top_k, document_id=req.document_id, user_id=current_user.id)
    results = retrieval.get('results', [])

    # Build a clean, numbered context with source metadata
    context_lines = []
    for idx, r in enumerate(results, start=1):
        src = f"doc:{r['document_id']} chunk:{r['chunk_id']} page:{r.get('page_number') or ''}"
        # Keep the response sources complete, but bound only the text sent to
        # the local LLM so a few large chunks cannot cause Ollama timeouts.
        content = r.get('content', '').strip()[:MAX_CONTEXT_CHUNK_CHARS]
        context_lines.append(f"[{idx}] SOURCE: {src}\n{content}")
    context = "\n\n".join(context_lines)

    prompt = f"""
    You are a document question-answering assistant.

    Answer the user's question using ONLY the information in the CONTEXT.

    IMPORTANT:
    - Read ALL provided context before answering.
    - Combine information from ALL relevant chunks.
    - Do not stop after mentioning the first qualification.
    - If the question asks for skills or qualifications, provide EVERY relevant skill and qualification found in the context.
    - Do not use outside knowledge.
    - Use clear headings and bullet points.
    - Give a complete answer.
    - Do not mention the retrieval process or chunks.

    If the answer truly cannot be found in the context, say:
    "I don't have enough information to answer that."

    QUESTION:
    {req.query}

    CONTEXT:
    {context}

    ANSWER:
    """


    try:
        llm = get_provider()
        print("\n========== PROMPT SENT TO GEMINI ==========")
        print(prompt)
        print("========== END PROMPT ==========\n")
        answer = llm.generate(prompt, max_tokens=1500)
        print("\n========== GEMINI ANSWER ==========")
        print(repr(answer))
        print("ANSWER LENGTH:", len(answer))
        print("========== END GEMINI ANSWER ==========\n")
    except Exception:
        raise HTTPException(status_code=502, detail="LLM provider error")

    # handle conversation and messages
    conv = None
    if req.conversation_id:
        conv = db.query(models.Conversation).filter(models.Conversation.id == req.conversation_id).first()
        if not conv or conv.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = models.Conversation(user_id=current_user.id, title=req.query)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # save user message
    um = models.Message(conversation_id=conv.id, sender="user", content=req.query)
    db.add(um)
    db.commit()

    # save assistant message (answer)
    am = models.Message(conversation_id=conv.id, sender="assistant", content=answer)
    db.add(am)
    db.commit()

    sources = []
    for r in results:
        sources.append({
            "document_id": r["document_id"],
            "chunk_id": r["chunk_id"],
            "page_number": r.get("page_number"),
            "content": r["content"],
            "similarity": r.get("similarity"),
        })

    return {"answer": answer, "sources": sources, "conversation_id": conv.id}
