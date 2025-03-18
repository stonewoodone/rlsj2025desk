"""Add transport_company field to FuelTransportation

Revision ID: 1bdf76cb5259
Revises: be0ad152e516
Create Date: 2025-03-17 22:30:43.938768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bdf76cb5259'
down_revision = 'be0ad152e516'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fuel_transportation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('transport_company', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fuel_transportation', schema=None) as batch_op:
        batch_op.drop_column('transport_company')

    # ### end Alembic commands ###
