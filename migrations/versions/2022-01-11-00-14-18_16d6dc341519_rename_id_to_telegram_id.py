"""rename id to telegram_id

Revision ID: 16d6dc341519
Revises: 6270cbc9981c
Create Date: 2022-01-11 00:14:18.816447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16d6dc341519'
down_revision = '6270cbc9981c'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('ix_Registrations_id', table_name='Registrations')
    op.alter_column('Registrations', 'id', new_column_name='telegram_id')
    op.create_index(op.f('ix_Registrations_telegram_id'), 'Registrations', ['telegram_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_Registrations_telegram_id'), table_name='Registrations')
    op.alter_column('Registrations', 'telegram_id', new_column_name='id')
    op.create_index('ix_Registrations_id', 'Registrations', ['id'], unique=False)
