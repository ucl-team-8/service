"""empty message

Revision ID: 20d7bb337fa1
Revises: 43713183abe2
Create Date: 2015-12-31 02:14:18.397114

"""

# revision identifiers, used by Alembic.
revision = '20d7bb337fa1'
down_revision = '43713183abe2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('geographical_location', sa.Column('cif_pass_count', sa.Integer(), nullable=True))
    op.add_column('geographical_location', sa.Column('cif_stop_count', sa.Integer(), nullable=True))
    op.add_column('geographical_location', sa.Column('crs', sa.String(length=10), nullable=True))
    op.add_column('geographical_location', sa.Column('description', sa.String(length=50), nullable=True))
    op.add_column('geographical_location', sa.Column('is_cif_stop', sa.Boolean(), nullable=True))
    op.add_column('geographical_location', sa.Column('latitude', sa.Float(precision=32), nullable=True))
    op.add_column('geographical_location', sa.Column('longitude', sa.Float(precision=32), nullable=True))
    op.add_column('geographical_location', sa.Column('stanox', sa.String(length=10), nullable=True))
    op.add_column('geographical_location', sa.Column('type', sa.String(length=20), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('geographical_location', 'type')
    op.drop_column('geographical_location', 'stanox')
    op.drop_column('geographical_location', 'longitude')
    op.drop_column('geographical_location', 'latitude')
    op.drop_column('geographical_location', 'is_cif_stop')
    op.drop_column('geographical_location', 'description')
    op.drop_column('geographical_location', 'crs')
    op.drop_column('geographical_location', 'cif_stop_count')
    op.drop_column('geographical_location', 'cif_pass_count')
    ### end Alembic commands ###
