from __future__ import annotations

import logging
import sys
from typing import Optional

from vectice.api import Client
from vectice.models import GitVersion, ApiToken
from vectice.models.integration import AbstractIntegration


class IntegrationFactory:
    @staticmethod
    def create_adapter(
        lib: object,
        vectice_client: Client,
        *args,
        **kwargs,
    ) -> AbstractIntegration:
        if lib is not None:
            if "mlflow" in sys.modules:
                from mlflow.tracking.client import MlflowClient

                if isinstance(lib, MlflowClient):
                    from vectice.mlflow import MLflowIntegration

                    return MLflowIntegration(lib, vectice_client, *args, **kwargs)
        raise RuntimeError(f"There is no support library for {lib}")


class Integrations:
    """
    Factory class for Artifacts
    """

    @classmethod
    def create_code_version(cls, path: str = ".", check_remote_repository: bool = True) -> Optional[GitVersion]:
        """
        Create a code artifact based on the git information relative to the given local path.

        :param path: The path to look for the git repository
        :param check_remote_repository: if we should check remote repository for file existence
        :return: A CodeVersion or None if a git repository was not found locally
        """
        git_version = GitVersion.create(path, check_remote_repository)
        if git_version is not None:
            return git_version
        else:
            logging.warning(
                "Automatic code detection failed because the .git couldn't be found or file wasn't found by Github"
            )
            return None

    @classmethod
    def create_code_version_with_uri(
        cls, uri: str, script_relative_path: str, login_or_token=None, password=None, oauth2_token=None
    ) -> Optional[GitVersion]:
        if "github" in uri:
            code_version = Integrations.create_code_version_with_github_uri(
                uri, script_relative_path, login_or_token, password, oauth2_token
            )
        elif "bitbucket" in uri:
            code_version = Integrations.create_code_version_with_bitbucket_uri(
                uri, script_relative_path, login_or_token, password
            )
        else:
            code_version = Integrations.create_code_version_with_gitlab_uri(
                uri, script_relative_path, login_or_token, oauth2_token
            )
        if code_version is None:
            raise ValueError("Code Version was not created. Please check the provided uri and entrypoint.")
        return code_version

    @classmethod
    def create_code_version_with_github_uri(
        cls, uri: str, script_relative_path: str, login_or_token=None, password=None, oauth2_token=None
    ) -> Optional[GitVersion]:
        """
        Create a code artifact based on the github information relative to the given URI and relative path.

        Note: The URI given can include the branch you are working on. otherwise, the default repository branch will be used.

        sample :
            https://github.com/my-organization/my-repository (no branch given so using default branch)
            https://github.com/my-organization/my-repository/tree/my-current-branch (branch given is my-current-branch)

        To access private repositories, you need to authenticate with your credentials.
        see https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/about-authentication-to-github

        :param uri: The uri of the repository with a specific branch if needed.
        :param script_relative_path:  The file that is executed
        :param login_or_token: A real login or personal access token
        :param password: The password
        :param oauth2_token: The Oauth2 access token
        :return: A CodeVersion or None if the github repository was not found or is not accessible
        """
        git_version = GitVersion.create_from_github_uri(
            uri, script_relative_path, login_or_token, password, oauth2_token
        )
        return git_version

    @classmethod
    def create_code_version_with_gitlab_uri(
        cls,
        uri: str,
        script_relative_path: str,
        private_token: Optional[str] = None,
        oauth2_token: Optional[str] = None,
    ) -> Optional[GitVersion]:
        """
        Create an artifact that contains a version of a code

        :param uri: The uri of the repository with a specific branch if needed.
        :param script_relative_path:  The file that is executed
        :param private_token: A real login or a personal access token
        :param oauth2_token: The OAuth2 access token
        :return: A CodeVersion or None if the GitHub repository was not found or is not accessible
        """
        git_version = GitVersion.create_from_gitlab_uri(uri, script_relative_path, private_token, oauth2_token)
        return git_version

    @classmethod
    def create_code_version_with_bitbucket_uri(
        cls,
        uri: str,
        script_relative_path: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Optional[GitVersion]:
        """
        Create a code artifact based on the Bitbucket information relative to the given URI and relative path.

        Note: The URI given can include the branch you are working on. otherwise, the default repository branch will be used.

        sample :
            https://bitbucket.org/workspace/project/ (no branch given so using default branch)
            https://bitbucket.org/workspace/project/src/branch (branch given is my-current-branch)

        To access private repositories, you need to authenticate with your credentials.
        see Bitbucket Cloud: https://atlassian-python-api.readthedocs.io/index.html

        :param uri: The uri of the repository with a specific branch if needed.
        :param script_relative_path:  The file that is executed
        :param username: Bitbucket email
        :param password: Bitbucket password
        :return: A CodeVersion or None if the Bitbucket repository was not found or is not accessible
        """
        git_version = GitVersion.create_from_bitbucket_uri(uri, script_relative_path, username, password)
        return git_version

    @classmethod
    def parse_api_token(cls, token_file: str) -> ApiToken:
        """
        Parses the the API Token json file and sets the os environmental variable for the "VECTICE_API_TOKEN"
        for the user.

        :param token_file: The filepath to the json file containing the "VECTICE_API_TOKEN", found on the Vectice App
        :return: ApiToken or None if the json file can not be parsed or found
        """
        return ApiToken.parse_api_token_json(token_file)
