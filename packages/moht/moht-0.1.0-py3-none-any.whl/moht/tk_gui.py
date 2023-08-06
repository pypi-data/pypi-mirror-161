import tkinter as tk
from functools import partial
from logging import getLogger
from os import path, removedirs, chdir, walk, remove, sep
from pathlib import Path
from pprint import pformat
from shlex import split
from shutil import move, copy2, rmtree
from subprocess import Popen, PIPE
from sys import platform
from time import time
from tkinter import filedialog, messagebox

from moht import PLUGINS2CLEAN, VERSION
from moht.utils import parse_cleaning

LOG = getLogger(__name__)


class MohtTkGui(tk.Frame):
    def __init__(self, master: tk.Tk,) -> None:
        """
        Create basic GUI for Mod Helper Tool application.

        :param master: Top level widget
        """
        LOG.info(f'moht v{VERSION} https://gitlab.com/modding-openmw/modhelpertool')
        super().__init__(master)
        self.tes3cmd = 'tes3cmd-0.37v.exe' if platform == 'win32' else 'tes3cmd-0.37w'
        self.master = master
        self.master.title('Mod Helper Tool')
        self.statusbar = tk.StringVar()
        self._mods_dir = tk.StringVar()
        self._morrowind_dir = tk.StringVar()
        self.chkbox_backup = tk.BooleanVar()
        self.chkbox_cache = tk.BooleanVar()
        self.stats = {'all': 0, 'cleaned': 0, 'clean': 0, 'error': 0}
        self._init_widgets()
        self.statusbar.set(f'ver. {VERSION}')
        # self._mods_dir.set('/home/emc/.local/share/openmw/data')
        # self._mods_dir.set('/home/emc/CitiesTowns/')  # test linux
        # self._mods_dir.set('D:/CitiesTowns')  # test win
        self._mods_dir.set(str(Path.home()))
        # self._morrowind_dir.set('/home/emc/.wine/drive_c/Morrowind/Data Files/')  # test linux
        # self._morrowind_dir.set('S:/Program Files/Morrowind/Data Files')  # test win
        self._morrowind_dir.set(str(Path.home()))
        self.chkbox_backup.set(True)
        self.chkbox_cache.set(True)
        self._check_clean_bin()

    def _init_widgets(self) -> None:
        self.master.columnconfigure(index=0, weight=10)
        self.master.columnconfigure(index=1, weight=1)
        self.master.rowconfigure(index=0, weight=10)
        self.master.rowconfigure(index=1, weight=1)
        self.master.rowconfigure(index=2, weight=1)
        self.master.rowconfigure(index=3, weight=1)
        self.master.rowconfigure(index=4, weight=1)

        mods_dir = tk.Entry(master=self.master, textvariable=self._mods_dir)
        morrowind_dir = tk.Entry(master=self.master, textvariable=self._morrowind_dir)
        mods_btn = tk.Button(master=self.master, text='Select Mods Dir', width=16, command=partial(self.select_dir, self._mods_dir))
        morrowind_btn = tk.Button(master=self.master, text='Select Morrowind Dir', width=16, command=partial(self.select_dir, self._morrowind_dir))
        self.clean_btn = tk.Button(master=self.master, text='Clean Mods', width=16, command=self.start_clean)
        self.report_btn = tk.Button(master=self.master, text='Report', width=16, state=tk.DISABLED, command=self.report)
        close_btn = tk.Button(master=self.master, text='Close Tool', width=16, command=self.master.destroy)
        statusbar = tk.Label(master=self.master, textvariable=self.statusbar)
        chkbox_backup = tk.Checkbutton(master=self.master, text='Remove backup after successful clean-up', variable=self.chkbox_backup)
        chkbox_cache = tk.Checkbutton(master=self.master, text='Remove cache after successful clean-up', variable=self.chkbox_cache)

        mods_dir.grid(row=0, column=0, padx=2, pady=2, sticky=f'{tk.W}{tk.E}')
        morrowind_dir.grid(row=1, column=0, padx=2, pady=2, sticky=f'{tk.W}{tk.E}')
        chkbox_backup.grid(row=2, column=0, padx=2, pady=2, sticky=tk.W)
        chkbox_cache.grid(row=3, column=0, padx=2, pady=2, sticky=tk.W)
        mods_btn.grid(row=0, column=1, padx=2, pady=2)
        morrowind_btn.grid(row=1, column=1, padx=2, pady=2)
        self.clean_btn.grid(row=2, column=1, padx=2, pady=2)
        self.report_btn.grid(row=3, column=1, padx=2, pady=2)
        close_btn.grid(row=4, column=1, padx=2, pady=2)
        statusbar.grid(row=5, column=0, columnspan=3, sticky=tk.W)

    @staticmethod
    def select_dir(text_var: tk.StringVar) -> None:
        """
        Select directory location.

        :param text_var: StringVar of Entry to update
        """
        directory = filedialog.askdirectory(initialdir=str(Path.home()), title='Select directory')
        LOG.debug(f'Directory: {directory}')
        text_var.set(f'{directory}')

    def start_clean(self) -> None:
        """Start cleaning process."""
        all_plugins = [Path(path.join(root, filename)) for root, _, files in walk(self.mods_dir) for filename in files if filename.lower().endswith('.esp') or filename.lower().endswith('.esm')]
        LOG.debug(f'all_plugins: {len(all_plugins)}: {all_plugins}')
        plugins_to_clean = [plugin_file for plugin_file in all_plugins if str(plugin_file).split(sep)[-1] in PLUGINS2CLEAN]
        no_of_plugins = len(plugins_to_clean)
        LOG.debug(f'to_clean: {no_of_plugins}: {plugins_to_clean}')
        chdir(self.morrowind_dir)
        here = path.abspath(path.dirname(__file__))
        self.stats = {'all': no_of_plugins, 'cleaned': 0, 'clean': 0, 'error': 0}
        start = time()
        for idx, plug in enumerate(plugins_to_clean, 1):
            LOG.debug(f'---------------------------- {idx} / {no_of_plugins} ---------------------------- ')
            LOG.debug(f'Copy: {plug} -> {self.morrowind_dir}')
            copy2(plug, self.morrowind_dir)
            mod_file = str(plug).split(sep)[-1]
            cmd_str = f'{path.join(here, self.tes3cmd)} clean --output-dir --overwrite "{mod_file}"'
            cmd = split(cmd_str) if platform == 'linux' else cmd_str
            LOG.debug(f'CMD: {cmd}')
            stdout, stderr = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()
            out, err = stdout.decode('utf-8'), stderr.decode('utf-8')
            LOG.debug(f'Out: {out}')
            LOG.debug(f'Err: {err}')
            result, reason = parse_cleaning(out, err, mod_file)
            LOG.debug(f'Result: {result}, Reason: {reason}')
            self._update_stats(mod_file, plug, reason, result)
            if self.chkbox_backup.get():
                LOG.debug(f'Remove: {self.morrowind_dir}/{mod_file}')
                remove(f'{self.morrowind_dir}/{mod_file}')
        LOG.debug(f'---------------------------- Done: {no_of_plugins} ---------------------------- ')
        if self.chkbox_cache.get():
            removedirs(f'{self.morrowind_dir}/1')
            cachedir = 'tes3cmd' if platform == 'win32' else '.tes3cmd-3'
            rmtree(f'{self.morrowind_dir}/{cachedir}', ignore_errors=True)
        LOG.debug(f'Total time: {time() - start:.2f} s')
        self.statusbar.set('Done. See report!')
        self.report_btn.config(state=tk.NORMAL)

    def _update_stats(self, mod_file: str, plug: Path, reason: str, result: bool) -> None:
        if result:
            LOG.debug(f'Move: {self.morrowind_dir}/1/{mod_file} -> {plug}')
            move(f'{self.morrowind_dir}/1/{mod_file}', plug)
            self.stats['cleaned'] += 1
        if not result and reason == 'not modified':
            self.stats['clean'] += 1
        if not result and 'not found' in reason:
            self.stats['error'] += 1
            esm = self.stats.get(reason, 0)
            esm += 1
            self.stats.update({reason: esm})

    def report(self) -> None:
        """Show report after clean-up."""
        LOG.debug(f'Report: {self.stats}')
        messagebox.showinfo('Report', pformat(self.stats, width=15))
        self.report_btn.config(state=tk.DISABLED)
        self.statusbar.set(f'ver. {VERSION}')

    def _check_clean_bin(self):
        here = path.abspath(path.dirname(__file__))
        LOG.debug('Checking tes3cmd')
        cmd_str = f'{path.join(here, self.tes3cmd)} -h'
        cmd = split(cmd_str) if platform == 'linux' else cmd_str
        LOG.debug(f'CMD: {cmd}')
        stdout, stderr = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()
        out, err = stdout.decode('utf-8'), stderr.decode('utf-8')
        result, reason = parse_cleaning(out, err, '')
        LOG.debug(f'Result: {result}, Reason: {reason}')
        if not result and 'Config::IniFiles' in reason:
            msg = 'Use your package manager, check for `perl-Config-IniFiles` or a similar package.\n\nOr run from a terminal:\ncpan install Config::IniFiles'
            messagebox.showerror('Missing package', msg)
            self.statusbar.set(f'Error: {reason}')
            self.clean_btn.config(state=tk.DISABLED)

    @property
    def mods_dir(self) -> str:
        """
        Get root of mods directory.

        :return: mods dir as string
        """
        return str(self._mods_dir.get())

    @mods_dir.setter
    def mods_dir(self, value: Path) -> None:
        self._mods_dir.set(str(value))

    @property
    def morrowind_dir(self) -> str:
        """
        Get Morrowind Data Files directory.

        :return: morrowind as sring
        """
        return str(self._morrowind_dir.get())

    @morrowind_dir.setter
    def morrowind_dir(self, value: Path) -> None:
        self._morrowind_dir.set(str(value))
