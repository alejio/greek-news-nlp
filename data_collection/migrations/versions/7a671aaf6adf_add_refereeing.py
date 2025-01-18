"""add refereeing

Revision ID: 7a671aaf6adf
Revises: 97bebe0d4a5f
Create Date: 2025-01-17 15:11:31.285325

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic
revision = "7a671aaf6adf"
down_revision = "97bebe0d4a5f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add new columns as nullable first
    op.add_column(
        "stance_predictions", sa.Column("target", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "stance_predictions",
        sa.Column("target_type", sa.String(length=20), nullable=True),
    )

    # 2. Copy data from target_club to target
    op.execute(
        "UPDATE stance_predictions SET target = target_club, target_type = 'club'"
    )

    # 3. Make new columns non-nullable now that they have data
    op.alter_column(
        "stance_predictions",
        "target",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.alter_column(
        "stance_predictions",
        "target_type",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    # 4. Update constraints
    op.drop_constraint(
        "unique_article_club_prediction", "stance_predictions", type_="unique"
    )
    op.create_unique_constraint(
        "unique_article_target_prediction",
        "stance_predictions",
        ["article_id", "target", "target_type"],
    )

    # 5. Drop old column only after data is migrated
    op.drop_column("stance_predictions", "target_club")


def downgrade() -> None:
    # 1. Add back target_club column
    op.add_column(
        "stance_predictions",
        sa.Column(
            "target_club", sa.VARCHAR(length=100), autoincrement=False, nullable=True
        ),
    )

    # 2. Copy data back
    op.execute(
        "UPDATE stance_predictions SET target_club = target WHERE target_type = 'club'"
    )

    # 3. Make target_club non-nullable
    op.alter_column(
        "stance_predictions",
        "target_club",
        existing_type=sa.VARCHAR(length=100),
        nullable=False,
    )

    # 4. Update constraints
    op.drop_constraint(
        "unique_article_target_prediction", "stance_predictions", type_="unique"
    )
    op.create_unique_constraint(
        "unique_article_club_prediction",
        "stance_predictions",
        ["article_id", "target_club"],
    )

    # 5. Drop new columns
    op.drop_column("stance_predictions", "target_type")
    op.drop_column("stance_predictions", "target")
