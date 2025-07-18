"""user model update email field update now it's must be fullfilled

Revision ID: b0b8662bd8eb
Revises: 99c42659819b
Create Date: 2025-07-11 15:31:46.244607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0b8662bd8eb'
down_revision: Union[str, Sequence[str], None] = '99c42659819b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
    op.create_unique_constraint(None, 'users', ['email'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
    # ### end Alembic commands ###
