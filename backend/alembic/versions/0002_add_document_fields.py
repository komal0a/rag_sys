"""add document file metadata fields

Revision ID: 0002_add_document_fields
Revises: 0001_initial
Create Date: 2026-08-15
"""
from alembic import op
import sqlalchemy as sa

revision = '0002_add_document_fields'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('documents', sa.Column('original_filename', sa.String(length=1024), nullable=True))
    op.add_column('documents', sa.Column('file_path', sa.String(length=2048), nullable=True))
    op.add_column('documents', sa.Column('content_type', sa.String(length=255), nullable=True))
    op.add_column('documents', sa.Column('file_size', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'))
    op.add_column('documents', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')))


def downgrade():
    op.drop_column('documents', 'updated_at')
    op.drop_column('documents', 'status')
    op.drop_column('documents', 'file_size')
    op.drop_column('documents', 'content_type')
    op.drop_column('documents', 'file_path')
    op.drop_column('documents', 'original_filename')
