import urllib
from pathlib import Path
from logging import Logger
from penvy.setup.SetupStepInterface import SetupStepInterface
from benvy.mutex.Mutex import Mutex


class PoetryInstallScriptDownloader(SetupStepInterface):
    def __init__(
        self,
        download_url: str,
        download_path: str,
        logger: Logger,
    ):
        self._download_url = download_url
        self._download_path = download_path
        self._logger = logger

    def run(self):
        with Mutex("benvy_poetry_install_script_downloader_mutex", timeout=180):
            if not self.should_be_run():
                return

            self._logger.info("Downloading poetry install script")
            Path(self._download_path).parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(self._download_url, self._download_path)

    def get_description(self):
        return "Download poetry installation script"

    def should_be_run(self) -> bool:
        return not Path(self._download_path).exists()
