from cmath import exp
import os
from threading import local
import urllib
import logging
import urllib.request
import shutil
import hashlib
from contextlib import closing
from pathlib import Path, PurePath
from Configs import getConfig
import time
import random
import gzip
import io

config = getConfig()

log = logging.getLogger("PubmedSuckerETLProcessToFile")


class PubMedSourceFileHandler:
    file_obtain_retry_count = config.MAX_RETRIES_ON_DOWNLOAD_ERRORS

    def __init__(self, file_url: str):
        self.file_url = file_url
        self.is_remote_file: bool = self._url_is_remote_file(file_url)
        self.storage_dir = os.path.abspath(config.PUBMED_XML_DOWNLOAD_DIR)
        if not self.is_remote_file:
            self._file_exists_and_is_accessable(file_url, raise_on_false=True)
            self.local_url = Path(file_url)
        else:
            self.local_url = None

    def open_file(self, mode: str = "rb") -> io.FileIO:
        if self.is_remote_file:
            self.local_url = self._obtain_remote_file()
        return open(self.local_url, mode)

    def get_target_filename(self, exclude_gz_extention_if_exists: bool = True):
        path = Path(self.file_url)
        if path.suffix == ".gz" and exclude_gz_extention_if_exists:
            return path.stem
        else:
            return path.name

    def _url_is_remote_file(self, file_url: str) -> bool:
        return urllib.parse.urlparse(file_url).scheme in [
            "ftp",
            "http",
            "https",
            "ftps",
        ]

    def _file_exists_and_is_accessable(
        self, file_url: str, raise_on_false: bool = False
    ) -> bool:
        try:
            f = open(file_url)
            f.close()
            return True
        except:
            if raise_on_false:
                raise FileNotFoundError(f"Can not access '{Path(file_url).resolve()}'")
            else:
                return False

    def _obtain_remote_file(self) -> Path:
        self._create_target_path_if_not_exists()
        target = self._get_target_filepath_for_remote_file(exclude_gz_extention=True)
        if self._file_exists_and_is_accessable(target):
            # file was allready downloaded
            if config.REDOWNLOAD_EXTISTING_PUBMED_XMLS:
                self._delete_file(target)
            else:
                log.info(f"File '{target}' allready exists. No download needed.")
                return Path(target)
        obtained = False
        obtain_tries = 0
        log.info(f"Start downloading file '{self.file_url}' to '{target}'")
        while not obtained:
            downloaded_source_file: Path = self._download(
                self.file_url,
                self._get_target_filepath_for_remote_file(exclude_gz_extention=False),
            )
            file_validation = self._validate_file(
                self.file_url,
                downloaded_source_file,
                ignore_if_validation_not_possible=False,
            )
            if file_validation == False:
                if obtain_tries >= self.file_obtain_retry_count:
                    raise ValueError(
                        f"Not able to download and validate file '{self.file_url}' to '{target}' after {obtain_tries} tries"
                    )
                else:
                    log.warning(
                        f"Failed to download and validate file '{self.file_url}' to '{target}'. Will retry {self.file_obtain_retry_count - obtain_tries} times"
                    )
                    # delete file that could not be validated. we consider this file garbage
                    self._delete_file(downloaded_source_file)
                    obtain_tries += 1
            elif file_validation == True:
                log.info(
                    f"Downloading and validation of file '{self.file_url}' to '{target}' successfull"
                )
                obtained = True
            elif file_validation is None:
                log.warning(
                    f"Downloading of file '{self.file_url}' to '{target}' successfull but could not validate"
                )
                obtained = True
        extracted = False
        extract_tries = 0
        if self._is_gz_file(downloaded_source_file):
            while not extracted:
                try:
                    with gzip.open(downloaded_source_file, "rb") as f_in:
                        with open(target, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    extracted = True
                except:
                    if extract_tries >= self.file_obtain_retry_count:
                        log.error(
                            f"Error extracting {downloaded_source_file} to {target}"
                        )
                        raise
                    else:
                        log.warning(
                            f"Failed to extract file '{self.file_url}' to '{target}'. Will retry {self.file_obtain_retry_count - extract_tries} times"
                        )
                        self._delete_file(target, not_exists_ok=True)
                        extract_tries += 1
                        time.sleep(random.randint(10, 30))
            self._delete_file(downloaded_source_file)
        return target

    def _validate_file(
        self, source_url, local_url, ignore_if_validation_not_possible: bool = True
    ):
        try:
            downloaded_source_file_hash = self._download(
                source_url + ".md5",
                self._get_target_filepath_for_remote_file(exclude_gz_extention=False)
                + ".md5",
                retry_count=3,
            )
        except Exception as err:
            if ignore_if_validation_not_possible:
                log.info(err)
                return None
            else:
                log.error(
                    f"Download of validation hash for file {local_url} not possible."
                )
                raise
        result = self._compare_file_to_hash(local_url, downloaded_source_file_hash)
        self._delete_file(downloaded_source_file_hash)
        return result

    def _compare_file_to_hash(self, local_path_source_file, file_with_hash):

        hash_inst = hashlib.md5()

        with open(local_path_source_file, "rb") as file_to_check:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: file_to_check.read(4096), b""):
                hash_inst.update(byte_block)
            hash_source = hash_inst.hexdigest()

        with open(file_with_hash) as file_with_hash:
            hash_file_content = file_with_hash.read()
        # hash_file_content will look like
        """
        MD5(pubmed22n0002.xml.gz)= 246e75874963b153bfd517320f4e891e
        """
        hash_for_verification = hash_file_content.split()[-1]
        if hash_source == hash_for_verification:
            return True
        else:
            return False

    def _remote_file_exists(self, url: str):
        try:
            response = urllib.request.urlopen(url)
            status_code = response.getcode()
            if status_code == 200:
                return True
            else:
                return False
        except urllib.request.HTTPError:
            return False

    def _is_gz_file(self, file_path: Path):
        return file_path.suffix == ".gz"

    def _delete_file(self, file, not_exists_ok: bool = False):
        if not os.path.exists(file) and not not_exists_ok:
            raise ValueError(f"Can not delete '{file}'. It does not exists")
        elif not os.path.exists(file):
            return
        os.remove(file)

    def _create_target_path_if_not_exists(self):
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_target_filepath_for_remote_file(
        self, exclude_gz_extention: bool = True
    ) -> str:
        source_filename = os.path.basename(self.file_url)
        file_name, file_extension = os.path.splitext(source_filename)
        if file_extension == ".gz" and exclude_gz_extention:
            return os.path.join(self.storage_dir, file_name)
        else:
            return os.path.join(self.storage_dir, source_filename)

    def _download(self, source_url, target_filenpath, retry_count: int = 4) -> Path:

        downloaded: bool = False
        tries = 0
        while not downloaded:
            try:
                # with requests.get(source_url, stream=True) as r:
                #    with open(target_filenpath, "wb") as f:
                #        shutil.copyfileobj(r.raw, f)
                response = urllib.request.urlopen(source_url)
                CHUNK = 16 * 1024
                with open(target_filenpath, "wb") as f:
                    while True:
                        chunk = response.read(CHUNK)
                        if not chunk:
                            break
                        f.write(chunk)
                downloaded = True
            except Exception as err:
                if tries < retry_count:
                    log.warning(
                        f"Failed downloading file '{source_url}' to  '{target_filenpath}' on {tries}th try. Will try {retry_count-tries} more times..."
                    )
                    log.error(err)
                    tries += 1
                    time.sleep(random.randint(10, 30))
                else:
                    log.error(
                        f"Failed downloading file '{source_url}' to '{target_filenpath}'"
                    )
                    raise

        return Path(target_filenpath)
