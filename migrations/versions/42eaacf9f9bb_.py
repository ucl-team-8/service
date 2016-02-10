"""empty message

Revision ID: 42eaacf9f9bb
Revises: 20d7bb337fa1
Create Date: 2016-02-10 15:54:27.019184

"""

# revision identifiers, used by Alembic.
revision = '42eaacf9f9bb'
down_revision = '20d7bb337fa1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('diagram_service',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unit', sa.String(length=20), nullable=True),
    sa.Column('cif_uid', sa.String(length=20), nullable=True),
    sa.Column('date_runs_from', sa.String(length=6), nullable=True),
    sa.Column('date_runs_to', sa.String(length=6), nullable=True),
    sa.Column('days_run', sa.String(length=7), nullable=True),
    sa.Column('train_category', sa.String(length=2), nullable=True),
    sa.Column('train_class', sa.String(length=1), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('diagram_stop',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('diagram_service_id', sa.Integer(), nullable=True),
    sa.Column('station_type', sa.String(length=2), nullable=True),
    sa.Column('tiploc', sa.String(length=20), nullable=True),
    sa.Column('arrive_time', sa.DateTime(), nullable=True),
    sa.Column('depart_time', sa.DateTime(), nullable=True),
    sa.Column('pass_time', sa.DateTime(), nullable=True),
    sa.Column('engineering_allowance', sa.Integer(), nullable=True),
    sa.Column('pathing_allowance', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['diagram_service_id'], ['diagram_service.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column(u'geographical_location', 'latitude',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               type_=sa.Float(precision=32),
               existing_nullable=True)
    op.alter_column(u'geographical_location', 'longitude',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               type_=sa.Float(precision=32),
               existing_nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'geographical_location', 'longitude',
               existing_type=sa.Float(precision=32),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    op.alter_column(u'geographical_location', 'latitude',
               existing_type=sa.Float(precision=32),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    op.drop_table('diagram_stop')
    op.drop_table('diagram_service')
    ### end Alembic commands ###
