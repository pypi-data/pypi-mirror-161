from distutils import filelist
from os import unlink
from shutil import copytree
from time import sleep
from typing import NoReturn

import VBPatcher.appglobals.appglobals
from PyLoadBar import PyLoadBar
from VBPatcher.applogger.applogger import logger, logger_stream
from VBPatcher.subprocessing.subprocessing import _startPrompt

patch_bar = PyLoadBar()
exit_seq = PyLoadBar(False)


class _Patcher:
    """Wrapper to handle patch functionality.

    ---

    - Contains the following patching methods:

        - :func:`_patch(patch_src: str, patch_dst: str, patch_ver: int | str) -> None`
            - Install patch files (`patch_src`) to target directory (`patch_dst`).
            - Static method.

        - :func:`_patch_stable(self) -> None | NoReturn`
            - Install latest BepInEx stable release version to target directory.

        - :func:`_patch_dev(self) -> None | NoReturn`
            - Install latest BepInEx development build version to target directory.

        - :func:`_patch_full(self) -> None | NoReturn`
            - Apply both available BepInEx patches in order of release (Stable -> Development).

        - :func:`_cancel(arg0, arg1) -> None | NoReturn`
            - Cancel patching process and return to menu.
            - Static method.
    """

    @staticmethod
    def _patch(patch_src: str, patch_dst: str, patch_ver: int | str) -> None:
        """Apply patch files (:param:`patch_src`) to target directory (:param:`patch_dst`).

        - Overwrites any existing patch files.

        ---

        :param patch_src: source directory containing patch files.
        :type patch_src: :class:`str`
        :param patch_dst: destination of patch files.
        :type patch_dst: :class:`str`
        :param patch_ver: version/title/build of patch.
        :type patch_ver: :class:`int` | :class:`str`
        :return: transfer patch files from :param:`patch_src` to :param:`patch_dst`.
        :rtype: None
        """

        try:
            logger.info(
                f'Patching BepInEx build {patch_ver} to location: {patch_dst}...'
            )

            copytree(
                patch_src, patch_dst,
                dirs_exist_ok=True)  # Copy patch files to target directory.

            unlink(f'{VBPatcher.appglobals.appglobals.p_targetDir}/.gitkeep'
                   )  # Remove .gitkeep file.

            patch_bar.start(
                f'Patching BepInEx build {patch_ver} to location: {patch_dst}',
                f'Patch build {patch_ver} successfully installed!',
                label='Patching',
                iter_total=len(filelist.findall(patch_src)),
                max_iter=0.2)  # Progress bar.

            logger.info(f'Patch build {patch_ver} successfully installed!\n')

        except Exception as exc:
            logger_stream.error(
                f'Failed to successfully copy BepInEx build {patch_ver} to location: {patch_dst}...\n>> Exception:\n{exc}\n'
            )

    def _patch_stable(self) -> None | NoReturn:
        """Install latest BepInEx stable-build release version to local directory.

        ---

        :return: patched BepInEx installation.
        :rtype: None
        """

        while True:
            logger.info(
                f'Prompting user for installation of BepInEx stable release {VBPatcher.appglobals.appglobals.b_dev} patch...\n'
            )
            confirmStable: str = input(
                f'\nReally patch BepInEx to latest stable-release {VBPatcher.appglobals.appglobals.b_stable} in location:\n\n>> "{VBPatcher.appglobals.appglobals.p_targetDir}"?\n\n> Enter [y] or [n]:\n{VBPatcher.appglobals.appglobals._textborder}\n> '
            )

            if confirmStable.lower() in {'yes', 'y'}:
                self._patch(VBPatcher.appglobals.appglobals.p_stable,
                            VBPatcher.appglobals.appglobals.p_targetDir,
                            VBPatcher.appglobals.appglobals.b_stable)
                return _startPrompt()  # Prompt user to start Valheim

            elif confirmStable.lower() in {'n', 'no'}:
                return self._cancel('>> BepInEx patching process cancelled',
                                    '>> Returning to menu...')

            else:
                logger_stream.warning(
                    f'Invalid Input: "{confirmStable}"\n>> Must ONLY enter either [y] for "YES" or [n] for "NO".\n'
                )
                sleep(1.250)
                continue

    def _patch_dev(self) -> None | NoReturn:
        """Install latest BepInEx development patch version to local directory.

        ---

        :return: patched BepInEx installation.
        :rtype: None
        """

        while True:
            logger.info(
                f'Prompting user for installation of BepInEx development build {VBPatcher.appglobals.appglobals.b_dev} patch...\n'
            )
            confirmLatest: str = input(
                f'\nReally patch BepInEx to latest development build {VBPatcher.appglobals.appglobals.b_dev} in location:\n\n>> "{VBPatcher.appglobals.appglobals.p_targetDir}"?\n\n> Enter [y] or [n]:\n{VBPatcher.appglobals.appglobals._textborder}\n> '
            )

            if confirmLatest.lower() in {'yes', 'y'}:
                self._patch(VBPatcher.appglobals.appglobals.p_dev,
                            VBPatcher.appglobals.appglobals.p_targetDir,
                            VBPatcher.appglobals.appglobals.b_dev)
                return _startPrompt()  # Prompt user to start Valheim

            elif confirmLatest.lower() in {'n', 'no'}:
                return self._cancel('>> BepInEx patching process cancelled',
                                    '>> Returning to menu...')

            else:
                logger_stream.warning(
                    f'Invalid Input: "{confirmLatest}"\n>> Must ONLY enter either [y] for "YES" or [n] for "NO".\n'
                )
                sleep(1.250)
                continue

    def _patch_full(self) -> None | bool:
        """Apply both stable and dev BepInEx patches in order of release (Stable -> Development).

        ---

        :return: patched BepInEx installation.
        :rtype: None
        """

        while True:
            logger.info(
                'Displaying confirmation prompt to install full-upgrade patch (install both stable and development builds in order of release)...\n'
            )
            confirmFull: str = input(
                f'\nReally apply both latest stable release {VBPatcher.appglobals.appglobals.b_stable}, and latest development build {VBPatcher.appglobals.appglobals.b_dev}?\n> Enter [y] or [n]:\n{VBPatcher.appglobals.appglobals._textborder}\n> '
            )
            if confirmFull.lower() in {'yes', 'y'}:
                self._patch(VBPatcher.appglobals.appglobals.p_stable,
                            VBPatcher.appglobals.appglobals.p_targetDir,
                            VBPatcher.appglobals.appglobals.b_stable)
                self._patch(VBPatcher.appglobals.appglobals.p_dev,
                            VBPatcher.appglobals.appglobals.p_targetDir,
                            VBPatcher.appglobals.appglobals.b_dev)
                return _startPrompt()  # Prompt user to start Valheim

            elif confirmFull.lower() in {'n', 'no'}:
                return self._cancel('>> BepInEx patching process cancelled',
                                    '>> Returning to menu...')

            else:
                logger_stream.warning(
                    f'Invalid Input: "{confirmFull}"\n>> Must ONLY enter either [y] for "YES" or [n] for "NO".\n'
                )
                sleep(1.250)
                continue

    @staticmethod
    def _cancel(arg0, arg1) -> None | NoReturn:
        """Cancel patching process and return to menu.

        ---

        :param arg0: text to pass to :func:`PyLoadBar.start(msg_loading: str)`.
        :type arg0: :class:`str`
        :param arg1: text to pass to :func:`PyLoadBar.start(msg_complete: str)`.
        :type arg1: :class:`str`
        :return: cancelled patching process.
        :rtype: None | :class:`NoReturn`
        """

        logger.info(
            'BepInEx patching process cancelled...\n>> Returning to menu...\n')
        return exit_seq.start(arg0, arg1, iter_total=3, txt_seq_speed=0.25)
