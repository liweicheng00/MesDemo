"""empty message

Revision ID: c26ed8c4a290
Revises: 0aace307a427
Create Date: 2020-07-19 22:15:57.622719

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c26ed8c4a290'
down_revision = '0aace307a427'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('auth_manager_permission_key', 'auth_manager', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('auth_manager_permission_key', 'auth_manager', ['permission'])
    # ### end Alembic commands ###