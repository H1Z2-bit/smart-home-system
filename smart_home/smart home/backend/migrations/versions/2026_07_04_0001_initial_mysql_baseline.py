"""initial mysql baseline

Revision ID: 0001_initial_mysql_baseline
Revises:
Create Date: 2026-07-04 19:30:00
"""

from __future__ import annotations

revision = "0001_initial_mysql_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The current baseline schema is initialized by smart_home.sql.
    pass


def downgrade() -> None:
    pass
