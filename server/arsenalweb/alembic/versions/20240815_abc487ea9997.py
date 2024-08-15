"""Adding data_center to physical_location

Revision ID: abc487ea9997
Revises: d8e2cee1e054
Create Date: 2024-08-15 10:00:13.839852

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'abc487ea9997'
down_revision = 'd8e2cee1e054'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('physical_locations', sa.Column('data_center_id', mysql.INTEGER(unsigned=True), nullable=True))
    op.create_foreign_key(op.f('fk_physical_locations_data_center_id_data_centers'), 'physical_locations', 'data_centers', ['data_center_id'], ['id'])
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_physical_locations_data_center_id_data_centers'), 'physical_locations', type_='foreignkey')
    op.drop_column('physical_locations', 'data_center_id')
    # ### end Alembic commands ###
