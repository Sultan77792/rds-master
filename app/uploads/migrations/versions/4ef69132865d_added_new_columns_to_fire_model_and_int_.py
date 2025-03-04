"""Added new columns to Fire model and int to text

Revision ID: 4ef69132865d
Revises: 1e5142ce68b1
Create Date: 2024-11-27 16:45:13.678008

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4ef69132865d'
down_revision = '1e5142ce68b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fires', schema=None) as batch_op:
        batch_op.add_column(sa.Column('LO_flag', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('LO_people_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('LO_tecnic_count', sa.Integer(), nullable=True))
        batch_op.alter_column('quarter',
               existing_type=mysql.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=True)
        batch_op.alter_column('allotment',
               existing_type=mysql.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fires', schema=None) as batch_op:
        batch_op.alter_column('allotment',
               existing_type=sa.String(length=255),
               type_=mysql.INTEGER(),
               existing_nullable=True)
        batch_op.alter_column('quarter',
               existing_type=sa.String(length=255),
               type_=mysql.INTEGER(),
               existing_nullable=True)
        batch_op.drop_column('LO_tecnic_count')
        batch_op.drop_column('LO_people_count')
        batch_op.drop_column('LO_flag')

    # ### end Alembic commands ###
