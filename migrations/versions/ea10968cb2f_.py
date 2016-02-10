"""empty message

Revision ID: ea10968cb2f
Revises: 4b29c2a22cbf
Create Date: 2016-02-10 16:51:21.925165

"""

# revision identifiers, used by Alembic.
revision = 'ea10968cb2f'
down_revision = '4b29c2a22cbf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('geographical_location', 'latitude',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               type_=sa.Float(precision=32),
               existing_nullable=True)
    op.alter_column('geographical_location', 'longitude',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               type_=sa.Float(precision=32),
               existing_nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('geographical_location', 'longitude',
               existing_type=sa.Float(precision=32),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    op.alter_column('geographical_location', 'latitude',
               existing_type=sa.Float(precision=32),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    ### end Alembic commands ###
