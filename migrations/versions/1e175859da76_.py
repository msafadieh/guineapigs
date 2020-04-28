"""empty message

Revision ID: 1e175859da76
Revises: b0fdf277700e
Create Date: 2020-04-28 15:55:16.103632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e175859da76'
down_revision = 'b0fdf277700e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('food_entry', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint('food_entry_user_fkey', 'food_entry', type_='foreignkey')
    op.create_foreign_key(None, 'food_entry', 'user', ['user_id'], ['id'])
    op.drop_column('food_entry', 'user')
    op.add_column('vitamin_c_entry', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint('vitamin_c_entry_user_fkey', 'vitamin_c_entry', type_='foreignkey')
    op.create_foreign_key(None, 'vitamin_c_entry', 'user', ['user_id'], ['id'])
    op.drop_column('vitamin_c_entry', 'user')
    op.add_column('weight_entry', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint('weight_entry_user_fkey', 'weight_entry', type_='foreignkey')
    op.create_foreign_key(None, 'weight_entry', 'user', ['user_id'], ['id'])
    op.drop_column('weight_entry', 'user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('weight_entry', sa.Column('user', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'weight_entry', type_='foreignkey')
    op.create_foreign_key('weight_entry_user_fkey', 'weight_entry', 'user', ['user'], ['id'])
    op.drop_column('weight_entry', 'user_id')
    op.add_column('vitamin_c_entry', sa.Column('user', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'vitamin_c_entry', type_='foreignkey')
    op.create_foreign_key('vitamin_c_entry_user_fkey', 'vitamin_c_entry', 'user', ['user'], ['id'])
    op.drop_column('vitamin_c_entry', 'user_id')
    op.add_column('food_entry', sa.Column('user', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'food_entry', type_='foreignkey')
    op.create_foreign_key('food_entry_user_fkey', 'food_entry', 'user', ['user'], ['id'])
    op.drop_column('food_entry', 'user_id')
    # ### end Alembic commands ###