from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, JSON, Index
import os
from sqlalchemy.orm import relationship, declarative_base
import os

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(1024), nullable=False)
    num_pages = Column(Integer, nullable=True)
    original_filename = Column(String(1024), nullable=True)
    file_path = Column(String(2048), nullable=True)
    content_type = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, server_default="uploaded")
    # 'metadata' is a reserved attribute name on declarative base; use Python-side
    # attribute `meta` while keeping the DB column name `metadata` for compatibility.
    meta = Column('metadata', JSON, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", backref="documents")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False, index=True)
    page_number = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    # Use `meta` as the Python attribute name to avoid conflict with SQLAlchemy's
    # Declarative API while keeping the DB column name `metadata`.
    meta = Column('metadata', JSON, nullable=True)
    # Embeddings column: use pgvector.Vector when available (Postgres),
    # otherwise fall back to JSON for SQLite/testing environments.
    try:
        from pgvector.sqlalchemy import Vector

        if os.environ.get("DATABASE_URL", "").startswith("postgresql"):
            EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM", 768))
            embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
        else:
            embedding = Column(JSON, nullable=True)
    except Exception:
        embedding = Column(JSON, nullable=True)

    document = relationship("Document", backref="chunks")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="conversations")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", backref="messages")


Index("ix_document_chunk_doc_chunkidx", DocumentChunk.document_id, DocumentChunk.chunk_index)
