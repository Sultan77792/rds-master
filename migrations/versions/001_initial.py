from alembic import op
import sqlalchemy as sa

def upgrade():
    # Создание таблицы ролей
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(64), unique=True),
        sa.Column('permissions', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание таблицы пользователей
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(64), unique=True),
        sa.Column('email', sa.String(120), unique=True),
        sa.Column('password_hash', sa.String(128)),
        sa.Column('role_id', sa.Integer()),
        sa.Column('region', sa.String(100)),
        sa.Column('kgu_oopt', sa.String(100)),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание таблицы пожаров
    op.create_table(
        'fires',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date_reported', sa.DateTime(), nullable=False),
        sa.Column('region', sa.String(100), nullable=False),
        sa.Column('kgu_oopt', sa.String(100), nullable=False),
        # ... остальные поля из модели Fire
        sa.Column('created_by_id', sa.Integer()),
        sa.Column('updated_by_id', sa.Integer()),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('fires')
    op.drop_table('users')
    op.drop_table('roles')