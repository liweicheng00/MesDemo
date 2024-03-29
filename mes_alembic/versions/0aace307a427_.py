"""empty message

Revision ID: 0aace307a427
Revises: 12f82425ab95
Create Date: 2020-07-19 22:05:45.754667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0aace307a427'
down_revision = '12f82425ab95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('auth_manager', 'func_name',
               existing_type=sa.VARCHAR(length=80),
               nullable=True)
    op.alter_column('auth_manager', 'num',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('auth_manager', 'permission',
               existing_type=sa.VARCHAR(length=80),
               nullable=True)
    op.alter_column('auth_manager', 'route_name',
               existing_type=sa.VARCHAR(length=80),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('auth_manager', 'route_name',
               existing_type=sa.VARCHAR(length=80),
               nullable=False)
    op.alter_column('auth_manager', 'permission',
               existing_type=sa.VARCHAR(length=80),
               nullable=False)
    op.alter_column('auth_manager', 'num',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('auth_manager', 'func_name',
               existing_type=sa.VARCHAR(length=80),
               nullable=False)
    # ### end Alembic commands ###
