"""creating post table

Revision ID: 6b5a5f759ce4
Revises: 
Create Date: 2022-03-24 01:50:02.259692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b5a5f759ce4'
down_revision = None
branch_labels = None
depends_on = None

# to check for how to modify stuff, go to alembic documentation > api > ddl
def upgrade():
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable = False, primary_key = True),
                             sa.Column('title', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_table('posts')
    pass
