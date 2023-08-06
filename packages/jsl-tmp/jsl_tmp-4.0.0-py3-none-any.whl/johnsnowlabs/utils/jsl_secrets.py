from dataclasses import dataclass
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Optional, Union, Dict, List
from abc import ABC, abstractmethod
import glob

import requests
import json
from johnsnowlabs.utils.enums import LibVersionIdentifier, Secret
import os

from johnsnowlabs.utils.my_jsl_api import get_user_licenses, download_license, get_access_token, \
    get_access_key_from_browser
from os.path import expanduser
from johnsnowlabs import settings

secret_json_keys = ['JSL_SECRET', 'SECRET', 'SPARK_NLP_LICENSE', 'JSL_LICENSE', 'JSL_VERSION', 'PUBLIC_VERSION',
                    'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
                    'SPARK_OCR_LICENSE', 'SPARK_OCR_SECRET', 'OCR_VERSION',
                    'HC_SECRET', 'HC_LICENSE', 'HC_VERSION', 'OCR_SECRET', 'OCR_LICENSE',

                    ]


@dataclass
class JslSecrets:
    """Representation of a JSL credentials and helper
    methods for reading/storing secrets and managing .jslhome folder
    """
    HC_SECRET: Secret = None
    HC_LICENSE: Secret = None
    HC_VERSION: Optional[LibVersionIdentifier] = None
    OCR_SECRET: Secret = None
    OCR_LICENSE: Secret = None
    OCR_VERSION: Optional[LibVersionIdentifier] = None
    NLP_VERSION: Optional[LibVersionIdentifier] = None
    AWS_ACCESS_KEY_ID: Secret = None
    AWS_SECRET_ACCESS_KEY: Secret = None

    @staticmethod
    def build_or_try_find_secrets(
            browser_login: bool = True,
            access_token: Optional[str] = None,
            license_number: int = 0,
            secrets_file: Optional[str] = None,
            hc_license: Optional[str] = None,
            hc_secret: Optional[str] = None,
            ocr_secret: Optional[str] = None,
            ocr_license: Optional[str] = None,
            aws_access_key: Optional[str] = None,
            aws_key_id: Optional[str] = None,
            return_empty_secrets_if_none_found=False) -> Union['JslSecrets', bool]:
        """
        Builds JslSecrets object if any secrets supplied or if none supplied,
         tries out every default resolution method defined to find secrets
        and build a JSlSecrets object
        :return: JslSecrets if any secrets found otherwise False
        """
        secrets = None
        if any([hc_license, hc_secret, ocr_secret, ocr_license, aws_access_key, aws_key_id]):
            # Some secrets are supplied
            secrets = JslSecrets(HC_SECRET=hc_secret, HC_LICENSE=hc_license, OCR_SECRET=ocr_secret,
                                 OCR_LICENSE=ocr_license,
                                 AWS_ACCESS_KEY_ID=aws_key_id, AWS_SECRET_ACCESS_KEY=aws_access_key)
        elif access_token:
            secrets = JslSecrets.from_access_token(access_token, license_number)

        # elif email and passw:
        #     secrets = JslSecrets.from_email_and_pass(email, passw,license_number)

        elif secrets_file:
            # Load from JSON file from provided secret file
            secrets = JslSecrets.from_json_file_path(secrets_file)

        if not secrets:
            # Try auto Resolve credentials if none are supplied
            secrets = JslSecrets.search_default_locations()
        if not secrets:
            # Search Env Vars
            secrets = JslSecrets.search_env_vars()
        if browser_login and not secrets:
            # TODO exception handling? And pick License from UI?
            access_token = get_access_key_from_browser()
            secrets = JslSecrets.from_access_token(access_token, license_number)


        if not secrets and return_empty_secrets_if_none_found:
            # Return empty secrets object
            return JslSecrets()
        if secrets:
            # We found some secrets
            # if not JslSecrets.from_jsl_home(False):
            # JSLHome handling this now
            #     # If this is the first time JSL-Creds are loaded on this machine
            #     # we store them in JSL home
            #     JslSecrets.store_in_jsl_home(secrets)
            return secrets

        return False

    @staticmethod
    def dict_has_jsl_secrets(secret_dict: Dict[str, str]) -> bool:

        for key in secret_json_keys:
            if key in secret_dict:
                return True
        return False

    @staticmethod
    def search_env_vars() -> Union['JslSecrets', bool]:
        """
        Search env vars for valid JSL-Secret values
        :return: JslSecrets if secret found, False otherwise
        """
        # We define max json size, anything above this will not be checked
        secrets = JslSecrets()

        hc_secret = os.environ['JSL_SECRET'] if 'JSL_SECRET' in os.environ else None
        if not hc_secret:
            hc_secret = os.environ['SECRET'] if 'SECRET' in os.environ else None
        if not hc_secret:
            hc_secret = os.environ['HC_SECRET'] if 'HC_SECRET' in os.environ else None

        hc_license = os.environ['SPARK_NLP_LICENSE'] if 'SPARK_NLP_LICENSE' in os.environ else None
        if not hc_license:
            hc_license = os.environ['JSL_LICENSE'] if 'JSL_LICENSE' in os.environ else None
        if not hc_license:
            hc_license = os.environ['HC_LICENSE'] if 'HC_LICENSE' in os.environ else None

        hc_version = os.environ['JSL_VERSION'] if 'JSL_VERSION' in os.environ else None
        if not hc_version:
            hc_version = os.environ['HC_VERSION'] if 'HC_VERSION' in os.environ else None

        nlp_version = os.environ['PUBLIC_VERSION'] if 'PUBLIC_VERSION' in os.environ else None
        aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'] if 'AWS_ACCESS_KEY_ID' in os.environ else None
        aws_access_key = os.environ['AWS_SECRET_ACCESS_KEY'] if 'AWS_SECRET_ACCESS_KEY' in os.environ else None

        ocr_license = os.environ['SPARK_OCR_LICENSE'] if 'SPARK_OCR_LICENSE' in os.environ else None
        if not ocr_license:
            ocr_license = os.environ['OCR_LICENSE'] if 'OCR_LICENSE' in os.environ else None

        ocr_secret = os.environ['SPARK_OCR_SECRET'] if 'SPARK_OCR_SECRET' in os.environ else None
        if not ocr_secret:
            ocr_secret = os.environ['OCR_SECRET'] if 'OCR_SECRET' in os.environ else None

        ocr_version = os.environ['OCR_VERSION'] if 'OCR_VERSION' in os.environ else None

        if any([hc_secret, hc_license, hc_license, hc_version, nlp_version, aws_access_key_id, aws_access_key,
                ocr_license, ocr_secret, ocr_version]):
            return JslSecrets(
                HC_SECRET=hc_secret,
                HC_LICENSE=hc_license,
                HC_VERSION=hc_version,
                OCR_SECRET=ocr_secret,
                OCR_LICENSE=ocr_license,
                OCR_VERSION=ocr_version,
                NLP_VERSION=nlp_version,
                AWS_ACCESS_KEY_ID=aws_access_key_id,
                AWS_SECRET_ACCESS_KEY=aws_access_key,
            )

        return False

    @staticmethod
    def json_path_as_dict(path):
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def search_default_locations() -> Union['JslSecrets', bool]:
        """
        Search default google colab folder and current working dir for
        for JSL Secret json file
        :return: JslSecrets if secret found, False otherwise
        """
        # We define max json size, anything above this will not be checked
        max_json_file_size = 10000

        # 1. Check colab content folder
        if os.path.exists('/content'):
            j_files = glob.glob('/content/*.json')
            for f_path in j_files:
                if os.path.getsize(f_path) > max_json_file_size:
                    continue
                json_dict = JslSecrets.json_path_as_dict(f_path)
                if JslSecrets.dict_has_jsl_secrets(json_dict):
                    print(f'Detected secret file {f_path}👌')  # ✅
                    return JslSecrets.from_json_file_path(f_path)

        # 2. Check current working dir
        j_files = glob.glob(f'{os.getcwd()}/*.json')
        for f_path in j_files:
            if os.path.getsize(f_path) > max_json_file_size:
                continue

            json_dict = JslSecrets.json_path_as_dict(f_path)
            if JslSecrets.dict_has_jsl_secrets(json_dict):
                print(f'Detected secret file {f_path}👌')  # ✅
                return JslSecrets.from_json_file_path(f_path)
        # 3. Check JSL home
        return JslSecrets.from_jsl_home()

    @staticmethod
    def from_json_file_path(secrets_path):
        if not os.path.exists(secrets_path):
            raise FileNotFoundError(f'No file found for secrets_path={secrets_path}')
        f = open(secrets_path)
        creds = JslSecrets.from_json_dict(json.load(f))
        f.close()
        return creds

    @staticmethod
    def from_access_token(access_token, license_number=0):
        licenses = get_user_licenses(access_token)
        data = download_license(licenses[license_number], access_token)
        secrets = JslSecrets.from_json_dict(data)
        return secrets

    @staticmethod
    def from_email_and_pass(email, passw, license_number=0):
        # TODO test and wait for PR !
        access_token = get_access_token(email, passw)
        licenses = get_user_licenses(access_token)
        data = download_license(licenses[license_number], access_token)
        secrets = JslSecrets.from_json_dict(data)
        return secrets

    @staticmethod
    def from_json_dict(secrets) -> 'JslSecrets':
        hc_secret = secrets['JSL_SECRET'] if 'JSL_SECRET' in secrets else None
        if not hc_secret:
            hc_secret = secrets['SECRET'] if 'SECRET' in secrets else None
        if not hc_secret:
            hc_secret = secrets['HC_SECRET'] if 'HC_SECRET' in secrets else None

        hc_license = secrets['SPARK_NLP_LICENSE'] if 'SPARK_NLP_LICENSE' in secrets else None
        if not hc_license:
            hc_license = secrets['JSL_LICENSE'] if 'JSL_LICENSE' in secrets else None
        if not hc_license:
            hc_license = secrets['HC_LICENSE'] if 'HC_LICENSE' in secrets else None

        hc_version = secrets['JSL_VERSION'] if 'JSL_VERSION' in secrets else None
        if not hc_version:
            hc_version = secrets['HC_VERSION'] if 'HC_VERSION' in secrets else None

        nlp_version = secrets['PUBLIC_VERSION'] if 'PUBLIC_VERSION' in secrets else None
        aws_access_key_id = secrets['AWS_ACCESS_KEY_ID'] if 'AWS_ACCESS_KEY_ID' in secrets else None
        aws_access_key = secrets['AWS_SECRET_ACCESS_KEY'] if 'AWS_SECRET_ACCESS_KEY' in secrets else None

        ocr_license = secrets['SPARK_OCR_LICENSE'] if 'SPARK_OCR_LICENSE' in secrets else None
        if not ocr_license:
            ocr_license = secrets['OCR_LICENSE'] if 'OCR_LICENSE' in secrets else None

        ocr_secret = secrets['SPARK_OCR_SECRET'] if 'SPARK_OCR_SECRET' in secrets else None
        if not ocr_secret:
            ocr_secret = secrets['OCR_SECRET'] if 'OCR_SECRET' in secrets else None

        ocr_version = secrets['OCR_VERSION'] if 'OCR_VERSION' in secrets else None

        return JslSecrets(
            HC_SECRET=hc_secret,
            HC_LICENSE=hc_license,
            HC_VERSION=hc_version,
            OCR_SECRET=ocr_secret,
            OCR_LICENSE=ocr_license,
            OCR_VERSION=ocr_version,
            NLP_VERSION=nlp_version,
            AWS_ACCESS_KEY_ID=aws_access_key_id,
            AWS_SECRET_ACCESS_KEY=aws_access_key,
        )

    @staticmethod
    def from_jsl_home(log=True) -> Union['JslSecrets', bool]:
        if os.path.exists(settings.creds_file):
            if log:
                print(f'📋 Found secrets in {settings.creds_file}')
            json_dict = JslSecrets.json_path_as_dict(settings.creds_file)
            creds = JslSecrets.from_json_dict(json_dict)
            return creds
        return False

    @staticmethod
    def store_in_jsl_home(secrets: 'JslSecrets') -> None:
        Path(settings.py_dir).mkdir(parents=True, exist_ok=True)
        if os.path.exists(settings.creds_file):
            # TODO overwrite old creds?
            return
        with open(settings.creds_file, 'w') as json_file:
            json.dump(secrets.__dict__, json_file)
        print(f'📋 Stored secrets in {settings.creds_file}')

