"""Editable signal descriptions and saved scenario definitions (no execution engine)."""

from alembic import op
import sqlalchemy as sa

revision = "003_device_editor_scenarios"
down_revision = "002_iot_runtime"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "signals",
        sa.Column("value_type", sa.String(10), nullable=False, server_default="string"),
    )
    op.add_column(
        "signals",
        sa.Column(
            "source_is_writable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "signals",
        sa.Column(
            "is_customized", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.execute(
        "UPDATE signals SET source_is_writable = COALESCE(is_writable, false), value_type = CASE WHEN signal_type IN ('range', 'graph', 'list', 'number', 'temperature', 'humidity', 'switch') OR min_value IS NOT NULL OR max_value IS NOT NULL THEN 'number' ELSE 'string' END"
    )
    op.create_table(
        "scenarios",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("object_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("match_mode", sa.String(3), nullable=False),
        sa.Column("conditions", sa.JSON(), nullable=False),
        sa.Column("actions", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_scenarios_object_id", "scenarios", ["object_id"])


def downgrade():
    op.drop_table("scenarios")
    for name in ("is_customized", "source_is_writable", "value_type"):
        op.drop_column("signals", name)
