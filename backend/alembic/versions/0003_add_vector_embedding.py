"""add vector embedding column and enable pgvector

Revision ID: 0003_add_vector_embedding
Revises: 0002_add_document_fields
"""

from alembic import op
import os


revision = "0003_add_vector_embedding"
down_revision = "0002_add_document_fields"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

        dim = int(os.environ.get("EMBEDDING_DIM", "8"))

        # embedding already exists as JSON from migration 0001.
        # Convert the existing column to pgvector.
        op.execute(
            f"""
            ALTER TABLE document_chunks
            ALTER COLUMN embedding TYPE vector({dim})
            USING NULL
            """
        )


def downgrade():
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        dim = int(os.environ.get("EMBEDDING_DIM", "8"))

        # Convert vector back to JSON-compatible text.
        op.execute(
            """
            ALTER TABLE document_chunks
            ALTER COLUMN embedding TYPE JSON
            USING NULL
            """
        )
