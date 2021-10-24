"""add data

Revision ID: 467132e028dd
Revises: 3f3caaaf8457
Create Date: 2021-10-25 01:35:55.378992

"""
from alembic import op
import sqlalchemy as sa


revision = '467132e028dd'
down_revision = '3f3caaaf8457'
branch_labels = None
depends_on = None


def upgrade():
    cohorts_table = sa.sql.table('Cohorts',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('notion_db_id', sa.String)
    )
    op.bulk_insert(cohorts_table,
        [
            {'id': 1, 'name': '1 когорта',
                    'notion_db_id': 'aeb4e7088d6b496f91eee139a7fbbdbb'},
            {'id': 2, 'name': '2 когорта',
                    'notion_db_id': 'bd13def18bb94135ac55fa67fd4f73b6'},
        ]
    )


def downgrade():
    pass
