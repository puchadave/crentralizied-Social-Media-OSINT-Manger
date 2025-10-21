"""Widgets that surface social media activity across networks."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.social.base import SocialConnector


class SocialMonitorWidget(QWidget):
    def __init__(self, connectors: list[SocialConnector], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._connectors = connectors
        self._posts_list = QListWidget()
        self._details = QTextEdit()
        self._details.setReadOnly(True)

        splitter = QSplitter()
        splitter.addWidget(self._posts_list)
        splitter.addWidget(self._details)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

        self._posts_list.currentItemChanged.connect(self._on_post_selected)

        self._populate_posts()

    def update_connectors(self, connectors: list[SocialConnector]) -> None:
        self._connectors = connectors
        self._populate_posts()

    def _populate_posts(self) -> None:
        self._posts_list.clear()
        for connector in self._connectors:
            for post in connector.fetch_recent_posts():
                item = QListWidgetItem(f"[{connector.network}] {post.author}: {post.content[:60]}")
                item.setData(Qt.ItemDataRole.UserRole, (connector, post))
                self._posts_list.addItem(item)
        if self._posts_list.count():
            self._posts_list.setCurrentRow(0)

    def _on_post_selected(self, current: QListWidgetItem | None, _: QListWidgetItem | None) -> None:
        if not current:
            self._details.clear()
            return
        connector, post = current.data(Qt.ItemDataRole.UserRole)
        comments = list(connector.fetch_comments(post.id))
        details = [
            f"Netzwerk: {connector.network}",
            f"Autor: {post.author}",
            f"Erstellt: {post.created_at}",
            f"URL: {post.url}",
            f"Reaktionen: {post.reactions}",
            f"Antworten: {post.replies}",
            "",
            post.content,
            "",
            "Kommentare:",
        ]
        for comment in comments:
            details.append(f"- {comment.author}: {comment.content}")
        self._details.setPlainText("\n".join(details))

