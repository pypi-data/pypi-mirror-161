import os
from typing import List, Tuple

import boto3
import botocore.client
from boto3.s3.transfer import S3Transfer
from botocore.credentials import RefreshableCredentials
from botocore.session import Session as BotocoreSession

from vessl import vessl_api
from vessl.cli._util import sizeof_fmt
from vessl.util.common import remove_prefix
from vessl.util.exception import VesslApiException, InvalidParamsError, InvalidVolumeFileError


class FileTransmission:
    def __init__(self, source_path, source_abs_path, dest_abs_path, size):
        self.source_path = source_path
        self.source_abs_path = source_abs_path
        self.dest_abs_path = dest_abs_path
        self.size = size


class VolumeFileTransfer:
    def __init__(self, volume_id: int):
        self.volume = vessl_api.volume_read_api(volume_id=volume_id)
        self.provider = None
        self.region_name = None
        self.bucket_name = None
        self.prefix = None
        self._update_federation_credentials()

    def download(self, source_path, dest_path):
        s3_client = self._get_s3_client()
        file_transmissions, total_size = self._get_download_file_transmissions_and_total_size(source_path, dest_path)
        total_file_count = len(file_transmissions)
        if total_file_count == 0:
            print("No files to download.")
            return

        formatted_total_size = sizeof_fmt(total_size)
        print(f"Downloading {total_file_count} file(s) ({formatted_total_size})...")

        succeeded_count = 0
        succeeded_size = 0
        for file_transmission in file_transmissions:
            dirname = os.path.dirname(file_transmission.dest_abs_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            try:
                s3_client.download_file(
                    self.bucket_name,
                    file_transmission.source_abs_path,
                    file_transmission.dest_abs_path,
                    Callback=self._create_callback(succeeded_size, total_size),
                )
                succeeded_count += 1
                succeeded_size += file_transmission.size
            except BaseException as e:
                print(f"Failed to download {file_transmission.source_path}.")
                raise e

        print(f"Total {succeeded_count} file(s) downloaded.")

    def upload(self, source_path, dest_path):
        if self.volume.is_read_only:
            print("Cannot upload to read-only volume.")
            return

        s3_client = self._get_s3_client()
        file_transmissions, total_size = self._get_upload_file_transmissions_and_total_size(source_path, dest_path)
        total_file_count = len(file_transmissions)
        if total_file_count == 0:
            print("No files to upload.")
            return

        formatted_total_size = sizeof_fmt(total_size)
        print(f"Uploading {total_file_count} file(s) ({formatted_total_size})...")

        succeeded_count = 0
        succeeded_size = 0
        for file_transmission in file_transmissions:
            try:
                s3_client.upload_file(
                    file_transmission.source_abs_path,
                    self.bucket_name,
                    file_transmission.dest_abs_path,
                    Callback=self._create_callback(succeeded_size, total_size),
                )
                succeeded_count += 1
                succeeded_size += file_transmission.size
            except BaseException as e:
                print(f"Failed to upload {file_transmission.source_path}.")
                raise e

        print(f"Total {succeeded_count} file(s) uploaded.")

    def copy(self, source_path, dest_path):
        # TODO
        return

    def remove(self, path):
        # TODO
        return

    def _create_callback(self, current_size, total_size):
        if total_size < 100*1024*1024:
            return None

        total_transmitted = current_size
        last_percent = int(total_transmitted/total_size*100)
        formatted_size = sizeof_fmt(total_size)
        interval = max(int(31*1024*1024/total_size * 100), 3)

        def callback(transmitted_bytes):
            nonlocal total_transmitted, last_percent
            total_transmitted += transmitted_bytes
            percent = int(total_transmitted/total_size*100)
            if percent-interval >= last_percent or percent == 100:
                print(f"{sizeof_fmt(total_transmitted)}/{formatted_size} ({percent}%) completed.")
                last_percent = percent

        return callback

    def _update_federation_credentials(self):
        federation_credentials = vessl_api.volume_federate_api(volume_id=self.volume.id)
        self.region_name = federation_credentials.region
        self.bucket_name = federation_credentials.bucket
        self.prefix = federation_credentials.prefix
        self.provider = federation_credentials.token.provider

    def _get_s3_client(self) -> S3Transfer:
        refreshable_credentials = RefreshableCredentials.create_from_metadata(
            metadata=self.__get_s3_session_credentials(),
            refresh_using=self.__get_s3_session_credentials,
            method="sts-assume-role",
        )

        botocore_session = BotocoreSession()
        botocore_session._credentials = refreshable_credentials
        botocore_session.set_config_variable("region", self.region_name)
        session = boto3.session.Session(botocore_session=botocore_session)
        config = botocore.client.Config(connect_timeout=120, read_timeout=120)
        return session.client("s3", config=config)

    def _get_download_file_transmissions_and_total_size(self, source_path: str, dest_path: str) -> Tuple[List[FileTransmission], int]:
        source_abs_path = f"{self.prefix}/{source_path}" if self.prefix else source_path
        dest_abs_path = os.path.abspath(dest_path)
        try:
            source_file = vessl_api.volume_file_read_api(volume_id=self.volume.id, path=source_path)
        except VesslApiException:
            files = vessl_api.volume_file_list_api(
                volume_id=self.volume.id,
                recursive=True,
                path=source_path,
                need_download_url=False,
            ).results
            # source path is a directory (if not, raise an error)

            if os.path.exists(dest_abs_path):
                if os.path.isfile(dest_abs_path):
                    raise InvalidVolumeFileError(
                        f"Destination path is not a directory: {dest_path}."
                    )
            else:
                os.makedirs(dest_abs_path)

            file_transmissions = []
            total_size = 0
            for file in files:
                if file.is_dir:
                    continue
                file_transmissions.append(FileTransmission(
                    file.path,
                    os.path.join(self.prefix, file.path.lstrip("/")),
                    os.path.join(dest_abs_path, remove_prefix(file.path, source_path).lstrip("/")),
                    file.size,
                ))
                total_size += file.size
            return file_transmissions, total_size

        # source path is a file
        file_name = os.path.basename(source_file.path)
        if os.path.isdir(dest_abs_path):
            dest_abs_path = os.path.join(dest_abs_path, file_name)
            if os.path.isdir(dest_abs_path):
                # Case where `source_path` is "a.txt", `dest_abs_path` is "dir/", and
                # "dir/a.txt/" exists as a directory
                raise InvalidParamsError(
                    f"Cannot overwrite directory {dest_abs_path} with non-directory {file_name}."
                )

        return [FileTransmission(
            source_path,
            source_abs_path,
            dest_abs_path,
            source_file.size,
        )], source_file.size

    def _get_upload_file_transmissions_and_total_size(self, source_path: str, dest_path: str) -> Tuple[List[FileTransmission], int]:
        source_path = os.path.relpath(source_path)
        if not os.path.exists(source_path):
            raise InvalidParamsError(f"{source_path} does not exist.")

        source_file_name = os.path.basename(source_path)
        if os.path.isfile(source_path):
            try:
                vessl_api.volume_file_read_api(volume_id=self.volume.id, path=dest_path)
                dest_abs_path = dest_path
            except VesslApiException as e:
                if e.code == "NotAFile":
                    dest_abs_path = f"{dest_path}/{source_file_name}"
                elif e.code == "NotFound":
                    dest_abs_path = dest_path
                else:
                    raise

            if self.prefix:
                dest_abs_path = os.path.join(self.prefix, dest_abs_path.lstrip("/"))

            source_abs_path = os.path.abspath(source_path)
            file_size = os.path.getsize(source_abs_path)
            return [FileTransmission(
                source_path,
                source_abs_path,
                dest_abs_path,
                file_size,
            )], file_size
        else:
            try:
                vessl_api.volume_file_read_api(volume_id=self.volume.id, path=dest_path)
            except VesslApiException as e:
                if e.code not in ("NotAFile", "NotFound"):
                    raise

                result = []
                total_size = 0
                for root_path, _, file_names in os.walk(source_path):
                    for file_name in file_names:
                        source_abs_path = os.path.join(root_path, file_name)
                        dest_abs_path = os.path.join(dest_path, remove_prefix(source_abs_path, source_path).lstrip("/"))
                        if self.prefix:
                            dest_abs_path = os.path.join(self.prefix, dest_abs_path.lstrip("/"))
                        file_size = os.path.getsize(source_abs_path)
                        result.append(FileTransmission(
                            source_path,
                            source_abs_path,
                            dest_abs_path,
                            file_size,
                        ))
                        total_size += file_size

                return result, total_size

            raise InvalidVolumeFileError(
                f"Destination path is not a directory: {dest_path}."
            )

    def __get_s3_session_credentials(self):
        federation_credentials = vessl_api.volume_federate_api(volume_id=self.volume.id)
        creds = federation_credentials.token.s3
        return {
            "access_key": creds.access_key_id,
            "secret_key": creds.secret_access_key,
            "token": creds.session_token,
            "expiry_time": creds.expiration.isoformat(),
        }
