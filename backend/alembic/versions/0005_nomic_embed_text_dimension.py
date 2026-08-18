"""change vectors to nomic-embed-text's verified 768 dimensions

Revision ID: 0005_nomic_embed_text_dimension
Revises: 0004_fix_embedding_dimension
"""

from alembic import op


revision = "0005_nomic_embed_text_dimension"
down_revision = "0004_fix_embedding_dimension"
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM document_chunks WHERE embedding IS NOT NULL) THEN
                RAISE EXCEPTION
                    'Cannot change document_chunks.embedding from vector(8) to vector(768) while embeddings exist. Back up the database, delete only the derived document_chunks rows, then re-run this migration and re-ingest the source PDFs.';
            END IF;
        END $$;
        """
    )
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768) USING NULL")


def downgrade():
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(8) USING NULL")
