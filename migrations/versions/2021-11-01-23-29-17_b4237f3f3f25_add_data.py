"""add_data

Revision ID: b4237f3f3f25
Revises: b2235513b173
Create Date: 2021-11-01 23:29:17.705993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4237f3f3f25'
down_revision = 'b2235513b173'
branch_labels = None
depends_on = None


def upgrade():
    cohorts_table = sa.sql.table('Cohorts', sa.column('id', sa.Integer),
                                 sa.column('name', sa.String),
                                 sa.column('notion_db_id', sa.String))
    op.bulk_insert(cohorts_table, [
        {'name': '1 когорта',
            'notion_db_id': 'aeb4e708-8d6b-496f-91ee-e139a7fbbdbb'},
        {'name': '2 когорта',
            'notion_db_id': 'bd13def1-8bb9-4135-ac55-fa67fd4f73b6'},
    ])


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
