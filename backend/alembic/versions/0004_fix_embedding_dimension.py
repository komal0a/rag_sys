"""set document chunk embeddings to 8 dimensions

Revision ID: 0004_fix_embedding_dimension
Revises: 0003_add_vector_embedding
"""

from alembic import op


revision = "0004_fix_embedding_dimension"
down_revision = "0003_add_vector_embedding"
branch_labels = None
depends_on = None


def upgrade():
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE document_chunks ALTER COLUMN embedding "
            "TYPE vector(8) USING embedding::vector(8)"
        )


def downgrade():
    if op.get_bind().dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE document_chunks ALTER COLUMN embedding "
            "TYPE vector(384) USING embedding::vector(384)"
        )
