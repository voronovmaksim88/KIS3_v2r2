"""add status_id TaskPaymentStatus_id 

Revision ID: c224ba1efb45
Revises: 255a25b48285
Create Date: 2025-03-17 15:14:54.567908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c224ba1efb45'
down_revision: Union[str, None] = '255a25b48285'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('status_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('TaskPaymentStatus_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tasks', 'task_statuses', ['status_id'], ['id'])
    op.create_foreign_key(None, 'tasks', 'payment_statuses', ['TaskPaymentStatus_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'TaskPaymentStatus_id')
    op.drop_column('tasks', 'status_id')
    # ### end Alembic commands ###
