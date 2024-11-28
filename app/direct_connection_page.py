import logging
import os
import subprocess
from enum import IntEnum
from typing import Any

import yaml
from PyQt5.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    pyqtSignal,
)
from PyQt5.QtGui import QContextMenuEvent, QFont
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.common import ViewBase
from app.connection import DirectConnection
from app.direct_connection_dialog import DirectConnectionDialog

DIRECT_CONNECTIONS_PATH = os.path.join(os.environ["APPDATA"], "StaSSH", "direct_connections.yaml")


class DirectConnectionsHeader(IntEnum):
    """Headers for the direct connections table."""

    NAME = 0
    USER = 1
    HOST = 2
    PORT = 3
    KEY = 4


class DirectConnectionsModel(QAbstractTableModel):
    """Model for the direct connections table."""

    def __init__(self):
        self.direct_connections: list[DirectConnection] = []
        super().__init__()

        self.headers = {
            DirectConnectionsHeader.NAME: "Name",
            DirectConnectionsHeader.USER: "User",
            DirectConnectionsHeader.HOST: "Host Name",
            DirectConnectionsHeader.PORT: "Port",
            DirectConnectionsHeader.KEY: "Key",
        }
        assert len(self.headers) == len(DirectConnectionsHeader)
        self.load()

    def add_direct_connection(self, direct_connection: DirectConnection) -> None:
        """Add a direct connection to the model.

        Args:
            direct_connection (DirectConnection): The direct connection to add.
        """
        row = len(self.direct_connections)
        self.beginInsertRows(QModelIndex(), row, row)
        self.direct_connections.append(direct_connection)
        self.endInsertRows()
        self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))
        self.save()

    def delete_connection(self, row: int) -> None:
        """Delete a direct connection from the model.

        Args:
            row (int): The row of the direct connection to delete.
        """
        self.beginRemoveRows(QModelIndex(), row, row)
        self.direct_connections.pop(row)
        self.endRemoveRows()
        self.save()

    def get_direct_connection(self, row: int) -> DirectConnection:
        """Get a direct connection from the model by row."""
        return self.direct_connections[row]

    def update_direct_connection(self, row: int, direct_connection: DirectConnection) -> None:
        """Update a direct connection in the model."""

        self.direct_connections[row] = direct_connection
        self.save()
        self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.direct_connections)

    def columnCount(self, parent: QModelIndex) -> int:
        return len(DirectConnectionsHeader)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return

        col = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole:  # What's displayed to the user
            if col == DirectConnectionsHeader.NAME:
                return self.direct_connections[row].name
            if col == DirectConnectionsHeader.USER:
                return self.direct_connections[row].user
            if col == DirectConnectionsHeader.HOST:
                return self.direct_connections[row].host
            if col == DirectConnectionsHeader.PORT:
                return self.direct_connections[row].port
            if col == DirectConnectionsHeader.KEY:
                return self.direct_connections[row].key

        if role == Qt.ItemDataRole.UserRole:  # Application-specific purposes
            if col == DirectConnectionsHeader.NAME:
                return self.direct_connections[row].name
            if col == DirectConnectionsHeader.USER:
                return self.direct_connections[row].user
            if col == DirectConnectionsHeader.HOST:
                return self.direct_connections[row].host
            if col == DirectConnectionsHeader.PORT:
                return self.direct_connections[row].port
            if col == DirectConnectionsHeader.KEY:
                return self.direct_connections[row].key

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[DirectConnectionsHeader(section)]
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font

    def load(self):
        if not os.path.exists(DIRECT_CONNECTIONS_PATH):
            return
        with open(DIRECT_CONNECTIONS_PATH) as file:
            loaded_direct_connections = yaml.safe_load(file)
            if loaded_direct_connections is not None:
                for connection in loaded_direct_connections:
                    self.direct_connections.append(DirectConnection.from_dict(connection))

    def save(self):
        if not os.path.exists(DIRECT_CONNECTIONS_PATH):
            os.makedirs(os.path.dirname(DIRECT_CONNECTIONS_PATH), exist_ok=True)
        with open(DIRECT_CONNECTIONS_PATH, "w") as file:
            yaml.dump([conn.to_dict() for conn in self.direct_connections], file)


class DirectConnectionsView(ViewBase):
    new_direct_connection = pyqtSignal()
    edit_direct_connection = pyqtSignal(int)
    duplicate_direct_connection = pyqtSignal(int)
    delete_direct_connection = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.new_action = QAction("New")
        self.edit_action = QAction("Edit")
        self.duplicate_action = QAction("Duplicate")
        self.delete_action = QAction("Delete")
        self.menu = QMenu(self)
        self.menu.addAction(self.new_action)
        self.menu.addAction(self.edit_action)
        self.menu.addAction(self.duplicate_action)
        self.menu.addAction(self.delete_action)

        self.new_action.triggered.connect(self.new_direct_connection.emit)
        self.edit_action.triggered.connect(lambda: self.edit_direct_connection.emit(self.currentIndex().row()))
        self.duplicate_action.triggered.connect(
            lambda: self.duplicate_direct_connection.emit(self.currentIndex().row())
        )
        self.delete_action.triggered.connect(lambda: self.delete_direct_connection.emit(self.currentIndex().row()))

    def attach_model(self, proxy_model: QSortFilterProxyModel) -> None:
        self.setModel(proxy_model)
        header = self.horizontalHeader()
        assert isinstance(header, QHeaderView)
        header.setSectionResizeMode(DirectConnectionsHeader.NAME.value, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(DirectConnectionsHeader.USER.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(DirectConnectionsHeader.HOST.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(DirectConnectionsHeader.PORT.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(DirectConnectionsHeader.KEY.value, QHeaderView.ResizeMode.ResizeToContents)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        index = self.indexAt(event.pos())
        is_valid = index.isValid()
        self.edit_action.setEnabled(is_valid)
        self.duplicate_action.setEnabled(is_valid)
        self.delete_action.setEnabled(is_valid)
        self.menu.exec_(event.globalPos())


class DirectConnectionsWidget(QWidget):
    def __init__(self):
        super().__init__()

        view = DirectConnectionsView()
        self.model = DirectConnectionsModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self.proxy_model.setSourceModel(self.model)
        view.attach_model(self.proxy_model)
        view.doubleClicked.connect(self._on_row_double_clicked)
        view.new_direct_connection.connect(self._on_new_direct_connection)
        view.edit_direct_connection.connect(self._on_edit_direct_connection)
        view.duplicate_direct_connection.connect(self._on_duplicate_direct_connection)
        view.delete_direct_connection.connect(self._on_delete_direct_connection)

        new_button = QPushButton("New")
        new_button.clicked.connect(self._on_new_direct_connection)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(new_button)
        buttons_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(buttons_layout)
        layout.addWidget(view)
        self.setLayout(layout)

    def _on_row_double_clicked(self, index: QModelIndex):
        """Open a new terminal window and connect to the host."""
        source_index = self.proxy_model.mapToSource(index)
        conn = self.model.get_direct_connection(source_index.row())

        key_arg = f"-i {conn.key}" if conn.key else ""
        command = f"ssh {key_arg} {conn.user}@{conn.host} -p{conn.port}"
        logging.info(f"Running: {command}")
        subprocess.Popen(["start", "cmd", "/k", command], shell=True)

    def _on_new_direct_connection(self):
        """Open the new direct connection dialog."""
        dialog = DirectConnectionDialog("New Direct Connection")
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            new_direct_connection = dialog.to_direct_connection()
            self.model.add_direct_connection(new_direct_connection)

    def _on_edit_direct_connection(self, row: int):
        """Open the edit direct connection dialog."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        direct_connection = self.model.get_direct_connection(source_index.row())

        dialog = DirectConnectionDialog("Edit Direct Connection")
        dialog.populate_fields(direct_connection)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            edited_direct_connection = dialog.to_direct_connection()
            self.model.update_direct_connection(source_index.row(), edited_direct_connection)

    def _on_duplicate_direct_connection(self, row: int):
        """Duplicate a direct connection."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        direct_connection = self.model.get_direct_connection(source_index).copy()
        direct_connection.name += " (Copy)"
        self.model.add_direct_connection(direct_connection)
        self._on_edit_direct_connection(self.model.direct_connections.index(direct_connection))

    def _on_delete_direct_connection(self, row: int):
        """Delete a direct connection."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        self.model.delete_connection(source_index.row())