"""Add composite indexes for better performance

Revision ID: bb041bf1c89e
Revises: fa749791dfc6
Create Date: 2025-07-10 14:58:17.845989

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb041bf1c89e'
down_revision: Union[str, Sequence[str], None] = 'fa749791dfc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add composite indexes for better search performance."""
    # Create composite index for full name searches
    op.create_index('idx_name_full', 'employees', ['first_name', 'last_name'], unique=False)
    
    # Create composite index for department and position searches
    op.create_index('idx_dept_position', 'employees', ['department', 'position'], unique=False)
    
    # Create composite index for location and status searches
    op.create_index('idx_location_status', 'employees', ['location', 'status'], unique=False)


def downgrade() -> None:
    """Remove the composite indexes."""
    op.drop_index('idx_location_status', table_name='employees')
    op.drop_index('idx_dept_position', table_name='employees')
    op.drop_index('idx_name_full', table_name='employees')
