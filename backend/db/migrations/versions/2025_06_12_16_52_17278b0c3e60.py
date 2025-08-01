"""enhance group schema and models

Revision ID: 17278b0c3e60
Revises: ff401bf5a34d
Create Date: 2025-06-12 16:52:36.756219

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17278b0c3e60'
down_revision = 'ff401bf5a34d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('error_groups', sa.Column('grouping_key', sa.String(length=255), nullable=False))
    op.add_column('error_groups', sa.Column('environment', sa.String(length=100), nullable=False))
    op.add_column('error_groups', sa.Column('title', sa.Text(), nullable=False))
    op.add_column('error_groups', sa.Column('culprit', sa.Text(), nullable=True))
    op.add_column('error_groups', sa.Column('level', sa.String(length=20), nullable=False))
    op.add_column('error_groups', sa.Column('status', sa.String(length=20), nullable=False))
    op.add_column('error_groups', sa.Column('users_affected', sa.BigInteger(), nullable=False))
    op.create_index('idx_fingerprint_status', 'error_groups', ['fingerprint', 'status'], unique=False)
    op.create_index('idx_last_seen_status', 'error_groups', ['last_seen', 'status'], unique=False)
    op.create_index('idx_service_env_status', 'error_groups', ['service', 'environment', 'status'], unique=False)
    op.create_index(op.f('ix_error_groups_environment'), 'error_groups', ['environment'], unique=False)
    op.create_index(op.f('ix_error_groups_grouping_key'), 'error_groups', ['grouping_key'], unique=False)
    op.alter_column('raw_errors', 'id',
               existing_type=sa.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False,
               autoincrement=True)
    op.drop_index(op.f('ix_raw_error_environment'), table_name='raw_errors')
    op.drop_index(op.f('ix_raw_error_id'), table_name='raw_errors')
    op.drop_index(op.f('ix_raw_error_service'), table_name='raw_errors')
    op.drop_index(op.f('ix_raw_error_user_id'), table_name='raw_errors')
    op.create_index(op.f('ix_raw_errors_environment'), 'raw_errors', ['environment'], unique=False)
    op.create_index(op.f('ix_raw_errors_service'), 'raw_errors', ['service'], unique=False)
    op.create_index(op.f('ix_raw_errors_user_id'), 'raw_errors', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_raw_errors_user_id'), table_name='raw_errors')
    op.drop_index(op.f('ix_raw_errors_service'), table_name='raw_errors')
    op.drop_index(op.f('ix_raw_errors_environment'), table_name='raw_errors')
    op.create_index(op.f('ix_raw_error_user_id'), 'raw_errors', ['user_id'], unique=False)
    op.create_index(op.f('ix_raw_error_service'), 'raw_errors', ['service'], unique=False)
    op.create_index(op.f('ix_raw_error_id'), 'raw_errors', ['id'], unique=False)
    op.create_index(op.f('ix_raw_error_environment'), 'raw_errors', ['environment'], unique=False)
    op.alter_column('raw_errors', 'id',
               existing_type=sa.Integer(),
               type_=sa.BIGINT(),
               existing_nullable=False,
               autoincrement=True)
    op.drop_index(op.f('ix_error_groups_grouping_key'), table_name='error_groups')
    op.drop_index(op.f('ix_error_groups_environment'), table_name='error_groups')
    op.drop_index('idx_service_env_status', table_name='error_groups')
    op.drop_index('idx_last_seen_status', table_name='error_groups')
    op.drop_index('idx_fingerprint_status', table_name='error_groups')
    op.drop_column('error_groups', 'users_affected')
    op.drop_column('error_groups', 'status')
    op.drop_column('error_groups', 'level')
    op.drop_column('error_groups', 'culprit')
    op.drop_column('error_groups', 'title')
    op.drop_column('error_groups', 'environment')
    op.drop_column('error_groups', 'grouping_key')
    # ### end Alembic commands ###
