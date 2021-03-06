"""empty message

Revision ID: 44dbee4e8cb0
Revises: 49d55a134ad2
Create Date: 2015-11-23 14:17:25.122397

"""

# revision identifiers, used by Alembic.
revision = '44dbee4e8cb0'
down_revision = '49d55a134ad2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gps', sa.Column('gps_car_id', sa.String(length=20), nullable=True))
    op.drop_column('gps', 'device')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gps', sa.Column('device', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('gps', 'gps_car_id')
    ### end Alembic commands ###
