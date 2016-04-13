"""empty message

Revision ID: 19f7b53eee51
Revises: 220c8f08290f
Create Date: 2016-04-13 11:58:02.498174

"""

# revision identifiers, used by Alembic.
revision = '19f7b53eee51'
down_revision = '220c8f08290f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('schedule_service_matching_lookup', 'schedule', ['headcode', 'origin_location', 'origin_departure', 'unit'], unique=False)
    op.add_column('service_matching', sa.Column('total_missed_in_between', sa.Integer(), nullable=False))
    op.drop_column('service_matching', 'matched_over_total')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_matching', sa.Column('matched_over_total', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.drop_column('service_matching', 'total_missed_in_between')
    op.drop_index('schedule_service_matching_lookup', table_name='schedule')
    ### end Alembic commands ###