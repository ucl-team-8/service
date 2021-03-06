"""empty message

Revision ID: 43713183abe2
Revises: 247b8442222b
Create Date: 2015-12-03 11:49:51.845683

"""

# revision identifiers, used by Alembic.
revision = '43713183abe2'
down_revision = '247b8442222b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('geographical_location',
    sa.Column('tiploc', sa.String(length=20), nullable=False),
    sa.Column('easting', sa.Integer(), nullable=True),
    sa.Column('northing', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('tiploc')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('geographical_location')
    ### end Alembic commands ###
