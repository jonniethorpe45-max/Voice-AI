"""initial surplus ops schema

Revision ID: 202603300001
Revises:
Create Date: 2026-03-30
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "202603300001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)
    op.create_index("ix_refresh_tokens_token", "refresh_tokens", ["token"], unique=True)

    op.create_table(
        "county_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("state", sa.String(length=2), nullable=False),
        sa.Column("county_name", sa.String(length=120), nullable=False),
        sa.Column("county_key", sa.String(length=40), nullable=False),
        sa.Column("sale_type", sa.String(length=120), nullable=False),
        sa.Column("source_urls_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("assignment_supported", sa.Boolean(), nullable=False),
        sa.Column("assignment_confidence", sa.Float(), nullable=False),
        sa.Column("manual_review_required", sa.Boolean(), nullable=False),
        sa.Column("active_for_ingestion", sa.Boolean(), nullable=False),
        sa.Column("active_for_outreach", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_county_configs_county_key", "county_configs", ["county_key"], unique=True)
    op.create_index("ix_county_configs_state", "county_configs", ["state"], unique=False)

    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("state", sa.String(length=2), nullable=False),
        sa.Column("county", sa.String(length=80), nullable=False),
        sa.Column("owner_name", sa.String(length=255), nullable=False),
        sa.Column("mailing_address", sa.Text(), nullable=True),
        sa.Column("property_address", sa.Text(), nullable=True),
        sa.Column("parcel_number", sa.String(length=120), nullable=True),
        sa.Column("sale_date", sa.Date(), nullable=True),
        sa.Column("surplus_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("lob_verification_status", sa.String(length=40), nullable=False),
        sa.Column("manual_review_required", sa.Boolean(), nullable=False),
        sa.Column("legal_review_cleared", sa.Boolean(), nullable=False),
        sa.Column("assignment_confidence", sa.Float(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_hash", sa.String(length=128), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=False),
        sa.Column("probate_risk", sa.Boolean(), nullable=False),
        sa.Column("duplicate_owner", sa.Boolean(), nullable=False),
        sa.Column("duplicate_property", sa.Boolean(), nullable=False),
        sa.Column("florida_manual_only", sa.Boolean(), nullable=False),
        sa.Column("california_assignment_possible", sa.Boolean(), nullable=False),
        sa.Column("extraction_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_leads_state", "leads", ["state"], unique=False)
    op.create_index("ix_leads_county", "leads", ["county"], unique=False)
    op.create_index("ix_leads_status", "leads", ["status"], unique=False)
    op.create_index("ix_leads_source_hash", "leads", ["source_hash"], unique=False)

    op.create_table(
        "lead_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
    )
    op.create_index("ix_lead_notes_lead_id", "lead_notes", ["lead_id"], unique=False)

    op.create_table(
        "lead_timeline",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_lead_timeline_lead_id", "lead_timeline", ["lead_id"], unique=False)
    op.create_index("ix_lead_timeline_event_type", "lead_timeline", ["event_type"], unique=False)

    op.create_table(
        "letters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_key", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("preview_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("lob_letter_id", sa.String(length=255), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("hold_reason", sa.Text(), nullable=True),
        sa.Column("approved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_letters_lead_id", "letters", ["lead_id"], unique=False)
    op.create_index("ix_letters_status", "letters", ["status"], unique=False)
    op.create_index("ix_letters_lob_letter_id", "letters", ["lob_letter_id"], unique=False)

    op.create_table(
        "tracking_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("letter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("external_id", sa.String(length=128), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["letter_id"], ["letters.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_tracking_events_lead_id", "tracking_events", ["lead_id"], unique=False)
    op.create_index("ix_tracking_events_status", "tracking_events", ["status"], unique=False)
    op.create_index("ix_tracking_events_external_id", "tracking_events", ["external_id"], unique=False)
    op.create_index("ix_tracking_events_event_time", "tracking_events", ["event_time"], unique=False)

    op.create_table(
        "response_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("operator_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_response_events_lead_id", "response_events", ["lead_id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_notifications_event_type", "notifications", ["event_type"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_label", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"], unique=False)
    op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"], unique=False)
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"], unique=False)
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"], unique=False)

    op.create_table(
        "import_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("county_key", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("records_seen", sa.Integer(), nullable=False),
        sa.Column("records_inserted", sa.Integer(), nullable=False),
        sa.Column("records_flagged", sa.Integer(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_import_runs_county_key", "import_runs", ["county_key"], unique=False)

    op.create_table(
        "raw_source_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("import_run_id", sa.Integer(), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_type", sa.String(length=16), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("extraction_metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["import_run_id"], ["import_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_raw_source_snapshots_import_run_id", "raw_source_snapshots", ["import_run_id"], unique=False)
    op.create_index("ix_raw_source_snapshots_lead_id", "raw_source_snapshots", ["lead_id"], unique=False)


def downgrade() -> None:
    op.drop_table("raw_source_snapshots")
    op.drop_table("import_runs")
    op.drop_table("audit_logs")
    op.drop_table("notifications")
    op.drop_table("response_events")
    op.drop_table("tracking_events")
    op.drop_table("letters")
    op.drop_table("lead_timeline")
    op.drop_table("lead_notes")
    op.drop_table("leads")
    op.drop_table("county_configs")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
