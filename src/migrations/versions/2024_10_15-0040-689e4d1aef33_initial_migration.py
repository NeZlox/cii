"""initial_migration

Revision ID: 689e4d1aef33
Revises: 
Create Date: 2024-10-15 00:40:46.667848

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '689e4d1aef33'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pictures',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Идентификатор изображения'),
    sa.Column('resolution_width', sa.Integer(), nullable=False, comment='Ширина разрешения изображения'),
    sa.Column('resolution_height', sa.Integer(), nullable=False, comment='Высота разрешения изображения'),
    sa.Column('url_page', sa.Text(), nullable=False, comment='URL страницы с изображением'),
    sa.Column('url_image', sa.Text(), nullable=False, comment='URL самого изображения'),
    sa.Column('path', sa.Text(), nullable=False, comment='Путь к изображению на сервере'),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url_image', name='unique_pictures_url_image'),
    comment='Таблица изображений с разрешениями и ссылками'
    )
    op.create_table('tags',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Идентификатор тега'),
    sa.Column('name', sa.String(), nullable=False, comment='Название тега'),
    sa.PrimaryKeyConstraint('id'),
    comment='Таблица тегов, которые могут быть связаны с изображениями'
    )
    op.create_table('picture_to_tags',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('id_tag', sa.Integer(), nullable=False, comment='Идентификатор тега'),
    sa.Column('id_picture', sa.Integer(), nullable=False, comment='Идентификатор изображения'),
    sa.ForeignKeyConstraint(['id_picture'], ['pictures.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_tag'], ['tags.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_tag', 'id_picture', name='unique_picture_to_tags_id_tag_id_picture'),
    comment='Таблица связи между изображениями и тегами (многие ко многим)'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('picture_to_tags')
    op.drop_table('tags')
    op.drop_table('pictures')
    # ### end Alembic commands ###
