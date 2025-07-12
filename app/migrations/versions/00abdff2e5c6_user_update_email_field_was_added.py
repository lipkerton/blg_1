"""user update email field was added

Revision ID: 00abdff2e5c6
Revises: f3d60a9cb63a
Create Date: 2025-07-11 15:22:48.709037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00abdff2e5c6'
down_revision: Union[str, Sequence[str], None] = 'f3d60a9cb63a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
