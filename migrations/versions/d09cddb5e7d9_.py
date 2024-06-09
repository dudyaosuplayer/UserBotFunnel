"""empty message

Revision ID: d09cddb5e7d9
Revises: 8b13af56fb08
Create Date: 2024-06-09 15:46:01.663926

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd09cddb5e7d9'
down_revision: Union[str, None] = '8b13af56fb08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('second_message_cancelled', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'second_message_cancelled')
    # ### end Alembic commands ###