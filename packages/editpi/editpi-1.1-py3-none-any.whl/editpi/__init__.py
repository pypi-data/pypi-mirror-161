"""
Copyright (C) 2022  Alexey Pavlov

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""

# MCPIEdit
# This is a different editor from revival's MCPIedit!
# This one is intended to work with Planet but it can work on its own

import sys
import os
import pathlib
import gettext

LOCALE = os.getenv("LANG")

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

try:
    from . import nbt_utils as nbt
except:
    import nbt_utils as nbt

USER = os.getenv("USER")  # Get the username, used for later

absolute_path = pathlib.Path(__file__).parent.absolute()

if not os.path.exists(f"/home/{USER}/.minecraft-pi/games/com.mojang/minecraftWorlds/"):
    os.makedirs(f"/home/{USER}/.minecraft-pi/games/com.mojang/minecraftWorlds/")


_ = gettext.translation(
    "mcpiedit",
    localedir=str(absolute_path) + "/assets/translations/",
    languages=[LOCALE],
).gettext


GAME_TYPES = {"Survival": nbt.pynbt.TAG_Int(0), "Creative": nbt.pynbt.TAG_Int(1)}

GAME_INTREGERS = {"0": "Survival", "1": "Creative"}

BOOLEAN_INTREGERS = {0: False, 1: True}
BOOLEAN_INTREGERS_REVERSED = {False: 0, True: 1}


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        label = QLabel("About MCPIedit")
        label.setAlignment(Qt.AlignHCenter)
        font = label.font()  # Font used
        font.setPointSize(15)  # Set the font size
        label.setFont(font)  # Aplly the font onto the label

        desc_label = QLabel(
            _(
                "The default built-in NBT editor for Planet.\n\nMCPIedit makes use of Pi-NBT\n from the original MCPIedit project\nby TheBrokenRail, which is\nlicensed under the MIT license.\nPlanet's MCPiedit is licensed under the AGPL.\nA copy of source code is located in /usr/lib/planet-launcher"
            )
        )
        desc_label.setAlignment(Qt.AlignHCenter)

        layout.addWidget(label)
        layout.addWidget(desc_label)

        self.setLayout(layout)


class FileSelectorTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        info_label = QLabel(
            _(
                "NBT editors allow you to edit your world\nfiles to change game modes, time,\nand even the world name. Select an NBT\nfile to edit using the button below."
            )
        )
        info_label.setAlignment(Qt.AlignHCenter)

        self.load_button = QPushButton(_("Select NBT File"))

        self.about_button = QPushButton(_("About"))
        self.about_button.clicked.connect(self.about_window)

        layout.addWidget(info_label)
        layout.addWidget(self.load_button)
        layout.addWidget(self.about_button)

        self.setLayout(layout)

    def about_window(self):
        self.window = AboutWindow()
        self.window.show()


class EditorTab(QWidget):
    def __init__(self, filename):
        super().__init__()

        layout = QVBoxLayout()

        self.nbt = nbt.load_nbt(filename, True)

        self.filename = filename

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setMovable(True)

        self.tabs.addTab(self.main_tab(), _("General"))
        self.tabs.addTab(self.world_tab(), _("World"))

        self.name_edit.setText(str(self.nbt["LevelName"].value))
        self.timestamp_box.setValue(int(self.nbt["LastPlayed"].value))
        self.game_box.setCurrentText(
            GAME_INTREGERS[str(int(self.nbt["GameType"].value))]
        )
        self.seed_edit.setText(str(int(self.nbt["RandomSeed"].value)))
        self.time_edit.setText(str(int(self.nbt["Time"].value)))
        # self.mobs_toggle.setChecked(BOOLEAN_INTREGERS[int(self.nbt["SpawnMobs"])]) # REMOVED BECAUSE DOES NOT WORK

        self.spawn_x_box.setValue(int(self.nbt["SpawnX"].value))
        self.spawn_y_box.setValue(int(self.nbt["SpawnY"].value))
        self.spawn_z_box.setValue(int(self.nbt["SpawnZ"].value))

        self.player_spawn_x_box.setValue(int(self.nbt["Player"]["SpawnX"].value))
        self.player_spawn_y_box.setValue(int(self.nbt["Player"]["SpawnY"].value))
        self.player_spawn_z_box.setValue(int(self.nbt["Player"]["SpawnZ"].value))

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def main_tab(self):

        widget = QWidget()

        layout = QGridLayout()

        self.name_label = QLabel(_("World name"))

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(_("OneChunk"))

        self.seed_label = QLabel("World Seed")

        self.seed_edit = QLineEdit()
        self.seed_edit.setPlaceholderText("-121542953")
        self.seed_edit.setValidator(QIntValidator())

        self.timestamp_label = QLabel(_("Last Played Timestamp"))

        self.timestamp_box = QSpinBox()
        self.timestamp_box.setMaximum(2147483647)

        self.game_label = QLabel(_("Game mode"))

        self.game_box = QComboBox()
        self.game_box.addItems(["Survival", "Creative"])

        # self.mobs_toggle = AnimatedToggle(
        #    checked_color="#59b8e0",
        #    pulse_checked_color="#92cee8"
        # )

        self.time_label = QLabel(_("Time (In Ticks)"))

        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("1770")
        self.time_edit.setValidator(QIntValidator())

        self.back_button = QPushButton(_("Back"))

        self.save_button = QPushButton(_("Save"))
        self.save_button.clicked.connect(self.save)

        layout.addWidget(self.name_label, 0, 0)
        layout.addWidget(self.name_edit, 0, 1)

        layout.addWidget(self.seed_label, 1, 0)
        layout.addWidget(self.seed_edit, 1, 1)

        layout.addWidget(self.timestamp_label, 2, 0)
        layout.addWidget(self.timestamp_box, 2, 1)

        layout.addWidget(self.game_label, 3, 0)
        layout.addWidget(self.game_box, 3, 1)

        layout.addWidget(self.time_label, 4, 0)
        layout.addWidget(self.time_edit, 4, 1)

        layout.addWidget(self.back_button, 5, 0)
        layout.addWidget(self.save_button, 5, 1)

        widget.setLayout(layout)

        return widget

    def world_tab(self):

        layout = QGridLayout()

        x_label = QLabel(_("Spawnpoint X"))

        self.spawn_x_box = QSpinBox()
        self.spawn_x_box.setMinimum(-128)
        self.spawn_x_box.setMaximum(128)

        y_label = QLabel(_("Spawnpoint Y"))

        self.spawn_y_box = QSpinBox()
        self.spawn_y_box.setMinimum(-64)
        self.spawn_y_box.setMaximum(64)

        z_label = QLabel(_("Spawnpoint Z"))

        self.spawn_z_box = QSpinBox()
        self.spawn_z_box.setMinimum(-128)
        self.spawn_z_box.setMaximum(128)

        player_x_label = QLabel(_("Player Spawnpoint X"))

        self.player_spawn_x_box = QSpinBox()
        self.player_spawn_x_box.setMinimum(-128)
        self.player_spawn_x_box.setMaximum(128)

        player_y_label = QLabel(_("Player Spawnpoint Y"))

        self.player_spawn_y_box = QSpinBox()
        self.player_spawn_y_box.setMinimum(-64)
        self.player_spawn_y_box.setMaximum(64)

        player_z_label = QLabel(_("Player Spawnpoint Z"))

        self.player_spawn_z_box = QSpinBox()
        self.player_spawn_z_box.setMinimum(-128)
        self.player_spawn_z_box.setMaximum(128)

        layout.addWidget(x_label, 0, 0)
        layout.addWidget(y_label, 1, 0)
        layout.addWidget(z_label, 2, 0)

        layout.addWidget(player_x_label, 3, 0)
        layout.addWidget(player_y_label, 4, 0)
        layout.addWidget(player_z_label, 5, 0)

        note_label = QLabel(
            _(
                "Note:\nPlayer spawnpoints are very buggy!\nYou might spawn in the wrong\nplace or even outside the world!\nDo not use on valuable worlds."
            )
        )

        layout.addWidget(self.spawn_x_box, 0, 1)
        layout.addWidget(self.spawn_y_box, 1, 1)
        layout.addWidget(self.spawn_z_box, 2, 1)

        layout.addWidget(self.player_spawn_x_box, 3, 1)
        layout.addWidget(self.player_spawn_y_box, 4, 1)
        layout.addWidget(self.player_spawn_z_box, 5, 1)

        layout.addWidget(note_label, 6, 0, 1, 2)

        widget = QWidget()
        widget.setLayout(layout)

        self.scroll = QScrollArea()

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(widget)

        return self.scroll

    def save(self):
        self.nbt["LevelName"] = nbt.pynbt.TAG_String(self.name_edit.text())
        self.nbt["LastPlayed"] = nbt.pynbt.TAG_Long(self.timestamp_box.value())
        self.nbt["GameType"] = GAME_TYPES[self.game_box.currentText()]
        self.nbt["RandomSeed"] = nbt.pynbt.TAG_Long(int(self.seed_edit.text()))
        self.nbt["Time"] = nbt.pynbt.TAG_Long(int(self.time_edit.text()))

        self.nbt["SpawnX"] = nbt.pynbt.TAG_Int(self.spawn_x_box.value())
        self.nbt["SpawnY"] = nbt.pynbt.TAG_Int(self.spawn_y_box.value())
        self.nbt["SpawnZ"] = nbt.pynbt.TAG_Int(self.spawn_z_box.value())

        self.nbt["Player"]["SpawnX"] = nbt.pynbt.TAG_Int(
            self.player_spawn_x_box.value()
        )
        self.nbt["Player"]["SpawnY"] = nbt.pynbt.TAG_Int(
            self.player_spawn_y_box.value()
        )
        self.nbt["Player"]["SpawnZ"] = nbt.pynbt.TAG_Int(
            self.player_spawn_z_box.value()
        )

        nbt.save_nbt(self.nbt, self.filename)


class NBTEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QStackedLayout()

        selector = FileSelectorTab()
        selector.load_button.clicked.connect(self.load_nbt)

        self.layout.addWidget(selector)

        self.setLayout(self.layout)

    def load_nbt(self):
        fname = QFileDialog.getOpenFileName(
            self,
            _("Open NBT File"),
            f"/home/{USER}/.minecraft-pi/games/com.mojang/minecraftWorlds/",
            _("Minecraft Pi Level NBT (level.dat)"),
        )

        if fname[0] == "":
            return

        editor = EditorTab(fname[0])
        editor.back_button.clicked.connect(lambda: self.layout.setCurrentIndex(0))

        self.layout.insertWidget(1, editor)
        self.layout.setCurrentIndex(1)
        self.setLayout(self.layout)


def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setCentralWidget(NBTEditor())
    window.setWindowTitle(_("MCPIEdit"))
    window.setWindowIcon(QIcon(f"{absolute_path}/assets/img/mcpiedit.png"))

    window.show()
    app.exec()


__all__ = ["main", "nbt"]
