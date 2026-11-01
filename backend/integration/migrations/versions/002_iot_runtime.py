"""Device addresses and integer auth identities; preserve legacy command actors."""

from alembic import op
import sqlalchemy as sa

revision = "002_iot_runtime"
down_revision = "001_initial_integration"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("devices", sa.Column("base_url", sa.String(), nullable=True))
    op.add_column(
        "command_logs", sa.Column("actor_user_id", sa.Integer(), nullable=True)
    )
    op.alter_column("command_logs", "user_id", nullable=True)
    op.drop_index("ix_command_logs_idempotency_key", table_name="command_logs")
    op.create_index(
        "ix_command_logs_idempotency_key", "command_logs", ["idempotency_key"]
    )
    op.create_unique_constraint(
        "uq_user_idempotency", "command_logs", ["actor_user_id", "idempotency_key"]
    )
    op.create_index("ix_command_logs_actor_user_id", "command_logs", ["actor_user_id"])
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE devicestatus ADD VALUE IF NOT EXISTS 'ERROR'")


def downgrade():
    raise RuntimeError(
        "Preserve command history: restore a database backup to downgrade"
    )
