"""Support TOR switches in Arsenal

Revision ID: d4574cc94ba8
Revises: b1bf5df56a22
Create Date: 2023-03-02 08:16:07.439795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4574cc94ba8'
down_revision = 'b1bf5df56a22'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('network_interfaces', sa.Column('mac_address', sa.Text(), nullable=True))
    op.add_column('network_interfaces', sa.Column('seen_mac_address', sa.Text(), nullable=True))
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('network_interfaces', 'seen_mac_address')
    op.drop_column('network_interfaces', 'mac_address')
    # ### end Alembic commands ###
