"""uniq-notion-id

Revision ID: 43315bdbe41f
Revises: 467132e028dd
Create Date: 2021-10-26 11:34:08.660140

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '43315bdbe41f'
down_revision = '467132e028dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'Cohorts', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Cohorts', type_='unique')
    # ### end Alembic commands ###