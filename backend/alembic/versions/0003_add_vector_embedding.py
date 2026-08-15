"""add vector embedding column and enable pgvector

Revision ID: 0003_add_vector_embedding
Revises: 0002_add_document_fields
Create Date: 2026-08-15
"""
from alembic import op
import sqlalchemy as sa
import os

revision = '0003_add_vector_embedding'
down_revision = '0002_add_document_fields'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        # enable extension
        op.execute('CREATE EXTENSION IF NOT EXISTS vector')
        dim = int(os.environ.get('EMBEDDING_DIM', 8))
        # add vector column; leave existing JSON column if present to avoid data loss
        op.add_column('document_chunks', sa.Column('embedding', sa.types.UserDefinedType(), nullable=True))
        # Use raw SQL to create the vector column with dimension
        op.execute(f'ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector({dim}) USING embedding::vector')


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        # drop vector column
        op.drop_column('document_chunks', 'embedding')
        # optionally remove extension (left in place)