"""Seconf migration

Revision ID: 2593ed4de533
Revises: 8f16a609391b
Create Date: 2024-10-29 19:46:17.072213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2593ed4de533'
down_revision: Union[str, None] = '8f16a609391b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comments')
    op.add_column('posts', sa.Column('auto_replay_enabled', sa.Boolean(), nullable=True))
    op.add_column('posts', sa.Column('auto_replay_delay', sa.Integer(), nullable=True))
    op.add_column('posts', sa.Column('created_at', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'created_at')
    op.drop_column('posts', 'auto_replay_delay')
    op.drop_column('posts', 'auto_replay_enabled')
    op.create_table('comments',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=True),
    sa.Column('post_id', sa.INTEGER(), nullable=True),
    sa.Column('author_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
