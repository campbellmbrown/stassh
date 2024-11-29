import json
import logging
import os
import subprocess
from enum import IntEnum
from typing import Any

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.common import ViewBase
from app.connection import ProxyJump
from app.proxy_jump_dialog import ProxyJumpDialog

PROXY_JUMPS_PATH = os.path.join(os.environ["APPDATA"], "StaSSH", "proxy_jumps.json")


class ProxyJumpsHeader(IntEnum):
    """Headers for the proxy jumps table."""

    NAME = 0
    TARGET_USER = 1
    TARGET_HOST = 2
    TARGET_PORT = 3
    JUMP_USER = 4
    JUMP_HOST = 5
    JUMP_PORT = 6
    KEY = 7


class ProxyJumpsModel(QAbstractTableModel):
    """Model for the proxy jumps table."""

    def __init__(self):
        self.proxy_jumps: list[ProxyJump] = []
        super().__init__()

        self.headers = {
            ProxyJumpsHeader.NAME: "Name",
            ProxyJumpsHeader.TARGET_USER: "Target User",
            ProxyJumpsHeader.TARGET_HOST: "Target Host",
            ProxyJumpsHeader.TARGET_PORT: "Target Port",
            ProxyJumpsHeader.JUMP_USER: "Jump User",
            ProxyJumpsHeader.JUMP_HOST: "Jump Host",
            ProxyJumpsHeader.JUMP_PORT: "Jump Port",
            ProxyJumpsHeader.KEY: "Key",
        }
        assert len(self.headers) == len(ProxyJumpsHeader)
        self._load()

    def add_proxy_jump(self, proxy_jump: ProxyJump) -> None:
        """Add a proxy jump to the model.

        Args:
            proxy_jump (ProxyJump): The proxy jump to add.
        """
        row = len(self.proxy_jumps)
        self.beginInsertRows(QModelIndex(), row, row)
        self.proxy_jumps.append(proxy_jump)
        self.endInsertRows()
        self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))
        self._save()

    def delete_proxy_jump(self, row: int) -> None:
        """Delete a proxy jump from the model.

        Args:
            row (int): The row of the proxy jump to delete.
        """
        self.beginRemoveRows(QModelIndex(), row, row)
        self.proxy_jumps.pop(row)
        self.endRemoveRows()
        self._save()

    def get_proxy_jump(self, row: int) -> ProxyJump:
        """Get a proxy jump from the model by row."""
        return self.proxy_jumps[row]

    def update_proxy_jump(self, row: int, proxy_jump: ProxyJump) -> None:
        """Update a proxy jump in the model."""
        self.proxy_jumps[row] = proxy_jump
        self._save()
        self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.headers) - 1))

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.proxy_jumps)

    def columnCount(self, parent: QModelIndex) -> int:
        return len(ProxyJumpsHeader)

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return

        col = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole:  # What's displayed to the user
            if col == ProxyJumpsHeader.NAME:
                return self.proxy_jumps[row].name
            if col == ProxyJumpsHeader.TARGET_USER:
                return self.proxy_jumps[row].target_user
            if col == ProxyJumpsHeader.TARGET_HOST:
                return self.proxy_jumps[row].target_host
            if col == ProxyJumpsHeader.TARGET_PORT:
                return self.proxy_jumps[row].target_port
            if col == ProxyJumpsHeader.JUMP_USER:
                return self.proxy_jumps[row].jump_user
            if col == ProxyJumpsHeader.JUMP_HOST:
                return self.proxy_jumps[row].jump_host
            if col == ProxyJumpsHeader.JUMP_PORT:
                return self.proxy_jumps[row].jump_port
            if col == ProxyJumpsHeader.KEY:
                return self.proxy_jumps[row].key

        if role == Qt.ItemDataRole.UserRole:  # Application-specific purposes
            if col == ProxyJumpsHeader.NAME:
                return self.proxy_jumps[row].name
            if col == ProxyJumpsHeader.TARGET_USER:
                return self.proxy_jumps[row].target_user
            if col == ProxyJumpsHeader.TARGET_HOST:
                return self.proxy_jumps[row].target_host
            if col == ProxyJumpsHeader.TARGET_PORT:
                return self.proxy_jumps[row].target_port
            if col == ProxyJumpsHeader.JUMP_USER:
                return self.proxy_jumps[row].jump_user
            if col == ProxyJumpsHeader.JUMP_HOST:
                return self.proxy_jumps[row].jump_host
            if col == ProxyJumpsHeader.JUMP_PORT:
                return self.proxy_jumps[row].jump_port
            if col == ProxyJumpsHeader.KEY:
                return self.proxy_jumps[row].key

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> Any:
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.headers[ProxyJumpsHeader(section)]
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font

    def _load(self):
        if not os.path.exists(PROXY_JUMPS_PATH):
            return
        with open(PROXY_JUMPS_PATH) as file:
            try:
                loaded_proxy_jumps = json.load(file)
            except json.JSONDecodeError:
                loaded_proxy_jumps = None
            if loaded_proxy_jumps is not None and "proxy_jumps" in loaded_proxy_jumps:
                proxy_jumps = loaded_proxy_jumps["proxy_jumps"]
                for proxy_jump in proxy_jumps:
                    self.proxy_jumps.append(ProxyJump.from_dict(proxy_jump))

    def _save(self):
        if not os.path.exists(PROXY_JUMPS_PATH):
            os.makedirs(os.path.dirname(PROXY_JUMPS_PATH), exist_ok=True)
        with open(PROXY_JUMPS_PATH, "w") as file:
            json.dump({"proxy_jumps": [pj.to_dict() for pj in self.proxy_jumps]}, file, indent=4)


class ProxyJumpsView(ViewBase):
    def __init__(self):
        super().__init__()

    def attach_model(self, proxy_model: QSortFilterProxyModel) -> None:
        self.setModel(proxy_model)
        header = self.horizontalHeader()
        assert isinstance(header, QHeaderView)
        header.setSectionResizeMode(ProxyJumpsHeader.NAME.value, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(ProxyJumpsHeader.TARGET_USER.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.TARGET_HOST.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.TARGET_PORT.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.JUMP_USER.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.JUMP_HOST.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.JUMP_PORT.value, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(ProxyJumpsHeader.KEY.value, QHeaderView.ResizeMode.ResizeToContents)


class ProxyJumpsWidget(QWidget):
    def __init__(self):
        super().__init__()

        view = ProxyJumpsView()
        self.model = ProxyJumpsModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self.proxy_model.setSourceModel(self.model)
        view.attach_model(self.proxy_model)
        view.doubleClicked.connect(self._on_row_double_clicked)
        view.new_item.connect(self._on_new_proxy_jump)
        view.edit_item.connect(self._on_edit_proxy_jump)
        view.duplicate_item.connect(self._on_duplicate_proxy_jump)
        view.delete_item.connect(self._on_delete_proxy_jump)

        new_button = QPushButton("New")
        new_button.clicked.connect(self._on_new_proxy_jump)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(new_button)
        buttons_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(buttons_layout)
        layout.addWidget(view)
        self.setLayout(layout)

    def _on_row_double_clicked(self, index: QModelIndex):
        """Open a new terminal window and connect to the host through the proxy jump."""
        source_index = self.proxy_model.mapToSource(index)
        pj = self.model.get_proxy_jump(source_index.row())

        key_arg = f"-i {pj.key}" if pj.key else ""
        jump_arg = f"-J {pj.jump_user}@{pj.jump_host}:{pj.jump_port}"
        target_arg = f"{pj.target_user}@{pj.target_host} -p{pj.target_port}"
        command = f"ssh {key_arg} {jump_arg} {target_arg}"
        logging.info(f"Running: {command}")
        subprocess.Popen(["start", "cmd", "/k", command], shell=True)

    def _on_new_proxy_jump(self):
        """Open a new proxy jump dialog."""
        dialog = ProxyJumpDialog("New proxy jump")
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.add_proxy_jump(dialog.to_proxy_jump())

    def _on_edit_proxy_jump(self, row: int):
        """Open an edit proxy jump dialog."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        proxy_jump = self.model.get_proxy_jump(source_index.row())

        dialog = ProxyJumpDialog("Edit proxy jump")
        dialog.populate_fields(proxy_jump)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.update_proxy_jump(source_index.row(), dialog.to_proxy_jump())

    def _on_duplicate_proxy_jump(self, row: int):
        """Duplicate a proxy jump into a new proxy jump dialog."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        proxy_jump = self.model.get_proxy_jump(source_index.row()).copy()
        proxy_jump.name += " (Copy)"
        dialog = ProxyJumpDialog("New proxy jump")
        dialog.populate_fields(proxy_jump)
        result = dialog.exec_()
        if result == QDialog.DialogCode.Accepted:
            self.model.add_proxy_jump(dialog.to_proxy_jump())

    def _on_delete_proxy_jump(self, row: int):
        """Delete a proxy jump."""
        source_index = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        self.model.delete_proxy_jump(source_index.row())