"""empty message

Revision ID: 220c8f08290f
Revises: 3bf1357adaa3
Create Date: 2016-04-12 15:59:45.417942

"""

# revision identifiers, used by Alembic.
revision = '220c8f08290f'
down_revision = '3bf1357adaa3'

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
    op.add_column('service_matching', sa.Column('iqr_time_error', sa.Float(), nullable=False))
    op.add_column('service_matching', sa.Column('matched_over_total', sa.Float(), nullable=False))
    op.drop_column('service_matching', 'variance_time_error')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_matching', sa.Column('variance_time_error', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.drop_column('service_matching', 'matched_over_total')
    op.drop_column('service_matching', 'iqr_time_error')
    op.alter_column('geographical_location', 'longitude',
               existing_type=sa.Float(precision=32),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    op.alter_column('geographical_location', 'latitude',
               existing_type=sa.Float(precision=32),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    ### end Alembic commands ###