"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "presets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("business_model", sa.String(128)),
        sa.Column("niche", sa.String(128)),
        sa.Column("design_type", sa.String(128)),
        sa.Column("style", sa.String(128)),
        sa.Column("aspect_ratio", sa.String(32)),
        sa.Column("gen_params", postgresql.JSONB()),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "uploads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("original_name", sa.String(512), nullable=False),
        sa.Column("stored_path", sa.String(1024), nullable=False),
        sa.Column("mime_type", sa.String(128), nullable=False),
        sa.Column("width", sa.Integer()),
        sa.Column("height", sa.Integer()),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false")),
    )

    op.create_table(
        "generation_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("original_prompt", sa.Text(), nullable=False),
        sa.Column("enhanced_prompt", sa.Text()),
        sa.Column("generation_params", postgresql.JSONB()),
        sa.Column("preset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("presets.id")),
        sa.Column("status", sa.String(32), server_default="pending"),
        sa.Column("progress", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_generation_tasks_status", "generation_tasks", ["status"])

    op.create_table(
        "generated_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("generation_tasks.id"), nullable=False),
        sa.Column("stored_path", sa.String(1024), nullable=False),
        sa.Column("width", sa.Integer()),
        sa.Column("height", sa.Integer()),
        sa.Column("size_bytes", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "settings",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("default_model", sa.String(128)),
        sa.Column("default_num_images", sa.Integer()),
        sa.Column("api_keys", postgresql.JSONB()),
    )


def downgrade() -> None:
    op.drop_table("settings")
    op.drop_table("generated_images")
    op.drop_index("ix_generation_tasks_status", table_name="generation_tasks")
    op.drop_table("generation_tasks")
    op.drop_table("uploads")
    op.drop_table("presets")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
