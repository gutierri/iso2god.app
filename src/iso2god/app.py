import shlex
import shutil
import os
import subprocess
import logging
import threading
import time
import platform
import ctypes
from pathlib import Path

import toga
from toga.paths import Paths
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


logging.basicConfig(level=logging.DEBUG)


class Iso2GOD(toga.App):
    def startup(self):
        main_box = self.gui()

        self._t = None
        self._p = None
        self.iso_file = None
        self.god_dir = None
        self.os = platform.system()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    async def dialog_choose_iso_file(self, e):
        logging.info('Open ISO File Picker')

        if self.os == 'Android':
            logging.debug('..Android')

            from android.content import Intent

            fileChose = Intent(Intent.ACTION_GET_CONTENT)
            fileChose.addCategory(Intent.CATEGORY_OPENABLE)
            fileChose.setType("*/*")
            results = await self._impl.intent_result(
                Intent.createChooser(fileChose, "Choose a file")
            )

            s = results['resultData'].getData().toString()

            logging.debug('In Android File=%s', s)

        else:
            if f := await self.main_window.dialog(toga.OpenFileDialog(title='')):
                self.iso_label.text = str(f)
                self.iso_file = Path(str(f))

    async def dialog_choose_god_folder(self, e):
        logging.debug('Open Folder Picker')

        if self.os == 'Android':

            logging.debug('..Android')

            from android.content import Intent

            fileChose = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
            results = await self._impl.intent_result(
                Intent.createChooser(fileChose, "Choose a file")
            )

            s = results['resultData'].getData().toString()

            logging.debug('In Android Folder=%s', s)

        else:
            if f := await self.main_window.dialog(toga.SelectFolderDialog(title='')):
                self.god_label.text = str(f)
                self.god_dir = Path(str(f))

    def gui(self):
        self.m = toga.Box(direction=COLUMN)

        self.iso_label = toga.Label('Select ISO files')
        self.iso_input_label = toga.Button('Choose', on_press=self.dialog_choose_iso_file)
        iso_box = toga.Box(direction=ROW)

        iso_box.add(self.iso_label)
        iso_box.add(self.iso_input_label)

        self.god_label = toga.Label('Select Folder to GOD')
        self.god_input_label = toga.Button('Choose', on_press=self.dialog_choose_god_folder)

        god_box = toga.Box(direction=ROW)
        god_box.add(self.god_label)
        god_box.add(self.god_input_label)

        self.submit_btn = toga.Button('Submit', on_press=self._submit)
        self.x = toga.Box(direction=COLUMN)

        #c = toga.Button('Cancel', on_press=self._cancel)
        p = toga.ProgressBar(max=None)
        p.start()

        self.x.add(p)
        #self.x.add(c)

        self.m.add(iso_box)
        self.m.add(god_box)

        self.m.add(self.submit_btn)

        return self.m

    def __disabled(self):
        self.m.remove(self.submit_btn)
        self.m.add(self.x)

        self.iso_input_label.enabled = False
        self.god_input_label.enabled = False
        self.submit_btn.enabled = False

    def __enabled(self):
        self.m.add(self.submit_btn)
        self.m.remove(self.x)
        self.iso_input_label.enabled = True
        self.god_input_label.enabled = True
        self.submit_btn.enabled = True

    def _submit(self, e):
        logging.debug('self.iso_file=%s self.god_dir=%s', self.iso_file, self.god_dir)

        logging.debug('Disabled fields and actions...')
        self.__disabled()

        logging.debug('Enable thread task...')

        self._t = threading.Thread(target=self._task, args=(self.iso_file, self.god_dir))
        self._t.start()

    def _cancel(self, e):
        logging.debug('Cancel called...')

        self.__enabled()

        if self._p:
            logging.debug('Kill action')
            self._p.terminate()

    def _task(self, iso_path, dest_dir):
        logging.debug('Start task thread...')

        logging.debug('platform=%s', self.os)

        match self.os:
            case 'Windows':
                lib = 'iso2god-x86_64-windows.dll'

            case 'Linux':
                lib = 'iso2god-x86_64-linux.so'

            case 'Android':
                lib = 'iso2god-aarch64-android.so'

        lib_path = Paths().app / 'resources' / lib
        iso2god = ctypes.CDLL(str(lib_path))

        iso_path = Path(iso_path).absolute().as_posix()
        dest_dir = Path(dest_dir).absolute().as_posix()
        args = (f'. {iso_path} {dest_dir}').encode('utf-8')

        logging.debug('Call DLL lib function from Ctypes...')

        iso2god.run_iso2god(ctypes.c_char_p(args))

        logging.debug('Enable fields and actions...')

        self.__enabled()


def main():
    return Iso2GOD()
