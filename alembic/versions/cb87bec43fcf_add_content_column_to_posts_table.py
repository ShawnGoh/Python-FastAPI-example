"""add content column to posts table

Revision ID: cb87bec43fcf
Revises: 6b5a5f759ce4
Create Date: 2022-03-24 01:57:08.194501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb87bec43fcf'
down_revision = '6b5a5f759ce4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
