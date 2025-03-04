"""Initial migration

Revision ID: b81f729fe5b4
Revises: 
Create Date: 2024-10-14 23:02:01.070455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b81f729fe5b4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fire',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('region', sa.String(length=255), nullable=False),
    sa.Column('location', sa.String(length=255), nullable=False),
    sa.Column('damage_area', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('damage_les', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('damage_les_verh', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('damage_not_les', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('people_count', sa.Integer(), nullable=True),
    sa.Column('aps', sa.Integer(), nullable=True),
    sa.Column('tecnic', sa.Integer(), nullable=True),
    sa.Column('airship', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('file_path', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=150), nullable=False),
    sa.Column('password', sa.String(length=150), nullable=False),
    sa.Column('roles', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('fire')
    # ### end Alembic commands ###
