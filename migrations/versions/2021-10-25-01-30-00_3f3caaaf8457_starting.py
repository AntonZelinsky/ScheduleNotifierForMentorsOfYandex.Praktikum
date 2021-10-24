"""Starting

Revision ID: 3f3caaaf8457
Revises: 
Create Date: 2021-10-24 23:22:55.536790

"""
import sqlalchemy as sa
from alembic import op

revision = '3f3caaaf8457'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('Cohorts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('notion_db_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Cohorts_id'), 'Cohorts', ['id'], unique=False)
    op.create_table('Users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('telegram_id', sa.Integer(), nullable=True),
        sa.Column('notion_user_id', sa.String(), nullable=True),
        sa.Column('is_activated', sa.Boolean(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=True),
        sa.Column('modified', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Users_email'), 'Users', ['email'], unique=True)
    op.create_index(op.f('ix_Users_id'), 'Users', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_Users_id'), table_name='Users')
    op.drop_index(op.f('ix_Users_email'), table_name='Users')
    op.drop_table('Users')
    op.drop_index(op.f('ix_Cohorts_id'), table_name='Cohorts')
    op.drop_table('Cohorts')
