"""empty message

Revision ID: 02a9c9e68bc7
Revises: 4f22e3757970
Create Date: 2018-11-26 11:41:25.549913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02a9c9e68bc7'
down_revision = '4f22e3757970'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('status', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('requests', 'status')
    # ### end Alembic commands ###