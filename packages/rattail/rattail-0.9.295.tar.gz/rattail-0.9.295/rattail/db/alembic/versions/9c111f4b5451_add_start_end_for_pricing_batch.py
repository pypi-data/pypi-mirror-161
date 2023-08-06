# -*- coding: utf-8; -*-
"""add start/end for pricing batch

Revision ID: 9c111f4b5451
Revises: 11fe87e4cd5f
Create Date: 2022-06-14 12:41:59.320748

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '9c111f4b5451'
down_revision = '11fe87e4cd5f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing
    op.add_column('batch_pricing', sa.Column('start_date', sa.Date(), nullable=True))


def downgrade():

    # batch_pricing
    op.drop_column('batch_pricing', 'start_date')
