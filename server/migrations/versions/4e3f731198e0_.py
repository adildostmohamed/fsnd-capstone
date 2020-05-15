"""empty message

Revision ID: 4e3f731198e0
Revises: 
Create Date: 2020-05-14 15:57:45.944200

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e3f731198e0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movies', sa.Column('release_date', sa.Date(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movies', 'release_date')
    # ### end Alembic commands ###
