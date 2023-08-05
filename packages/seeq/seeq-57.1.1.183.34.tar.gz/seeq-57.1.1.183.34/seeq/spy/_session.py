from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, List

from seeq import spy
from seeq.sdk import *
from seeq.sdk.configuration import ClientConfiguration
from seeq.spy import _url
from seeq.spy._config import Options

SEEQ_SDK_RETRY_TIMEOUT_IN_SECONDS_ENV_VAR_NAME = 'SEEQ_SDK_RETRY_TIMEOUT_IN_SECONDS'


@dataclass(repr=False)
class Session:
    """
    Used to segregate Seeq Server logins and allows for multi-server /
    multi-user concurrent logins. This object encapsulates all server-
    specific state, SPy options and API client configuration.

    Examples
    --------
    Log in to two different servers at the same time:

    >>> session1 = Session()
    >>> session2 = Session()
    >>> spy.login(url='https://server1.seeq.site', username='mark', password='markpassword', session=session1)
    >>> spy.login(url='https://server2.seeq.site', username='alex', password='alexpassword', session=session2)
    """
    _options: Options = None
    client_configuration: ClientConfiguration = None
    _client: Optional[ApiClient] = None
    _user: Optional[UserOutputV1] = None
    _public_url: Optional[str] = None
    _private_url: Optional[str] = None
    _server_version: Optional[str] = None
    supported_units: Optional[set] = None
    corporate_folder: Optional[FolderOutputV1] = None
    auth_providers: Optional[List[DatasourceOutputV1]] = None
    https_verify_ssl: bool = True
    https_key_file: Optional[str] = None
    https_cert_file: Optional[str] = None

    def __init__(self, options: Options = None, client_configuration: ClientConfiguration = None):
        self.client_configuration = client_configuration if client_configuration is not None else ClientConfiguration()
        self.options = options if options is not None else Options(self.client_configuration)

        # We have this mechanism so that test_run_notebooks() is able to increase the timeout for the child kernels
        if Session.get_global_sdk_retry_timeout_in_seconds() is not None:
            self.options.retry_timeout_in_seconds = Session.get_global_sdk_retry_timeout_in_seconds()

    def __repr__(self):
        if not self.client:
            return 'Not logged in'
        url_part = self.public_url
        if self.private_url != self.public_url:
            url_part += f' ({self.private_url})'
        return f'{url_part} as {self.user.name} ({self.user.username})'

    def __getstate__(self):
        # We can only pickle certain members. This has to mirror __setstate__().
        return self.options

    def __setstate__(self, state):
        self.options = state

    @staticmethod
    def validate(session):
        return spy.session if session is None else session

    @staticmethod
    def set_global_sdk_retry_timeout_in_seconds(timeout: Optional[int]):
        """
        This is used to set the SDK's retry timeout (see
        "retry_timeout_in_seconds" in api_client.py) for all
        child Python kernels, such as those spawned by executing
        notebooks via nbformat is in test_run_notebook().
        :param timeout: Timeout (in seconds)

        :meta private:
        """
        if timeout is None and SEEQ_SDK_RETRY_TIMEOUT_IN_SECONDS_ENV_VAR_NAME in os.environ:
            del os.environ[SEEQ_SDK_RETRY_TIMEOUT_IN_SECONDS_ENV_VAR_NAME]
        else:
            os.environ[SEEQ_SDK_RETRY_TIMEOUT_IN_SECONDS_ENV_VAR_NAME] = str(timeout)

    @staticmethod
    def get_global_sdk_retry_timeout_in_seconds() -> Optional[int]:
        """
        See set_global_sdk_retry_timeout_in_seconds()
        :return: Timeout (in seconds)

        :meta private:
        """
        if SEEQ_SDK_RETRY_TIMEOUT_IN_SECONDS_ENV_VAR_NAME in os.environ:
            return int(os.environ[SEEQ_SDK_RETRY_TIMEOUT_IN_SECONDS_ENV_VAR_NAME])
        else:
            return None

    def clear(self):
        """
        Re-initializes the object to a "logged out" state. Note that this
        function does NOT reset API client configuration or SPy options.
        """
        self.client = None
        self.user = None
        self.public_url = None
        self.private_url = None
        self.server_version = None
        self.supported_units = None
        self.corporate_folder = None
        self.auth_providers = None
        self.https_verify_ssl = True
        self.https_key_file = None
        self.https_cert_file = None

    # Prior to the advent of Session objects, the spy.client, spy.user and spy.server_version module-level variables
    # were exposed to end-users as a convenience. The setters below copy those (now) Session variables to those
    # legacy module-level locations for backward compatibility purposes. (Only if this Session object is the default
    # Session.)
    @property
    def client(self) -> Optional[ApiClient]:
        """
        Get the API client object for this session
        """
        return self._client

    @client.setter
    def client(self, value):
        self._client = value
        if self._client is not None:
            self._client.user_agent = f'Seeq-Python-SPy/{spy.__version__}/python'
        if self is spy.session:
            spy.client = self._client

    @property
    def user(self) -> Optional[UserOutputV1]:
        """
        Get the user that is logged into this session
        """
        return self._user

    @user.setter
    def user(self, value):
        self._user = value
        if self is spy.session:
            spy.user = self._user

    @property
    def server_version(self) -> Optional[str]:
        """
        Get the version of the Seeq server
        this session is logged into
        """
        return self._server_version

    @server_version.setter
    def server_version(self, value):
        self._server_version = value
        if self is spy.session:
            spy.server_version = self._server_version

    @property
    def public_url(self):
        return self._public_url

    @public_url.setter
    def public_url(self, value):
        self._public_url = _url.cleanse_url(value)

    @property
    def private_url(self):
        return self._private_url

    @private_url.setter
    def private_url(self, value):
        self._private_url = _url.cleanse_url(value)

    def get_api_url(self):
        """
        Returns the URL to use for API calls, which ends up being the
        private URL (if specified) or the public URL.

        :meta private:
        """
        return f'{self.private_url}/api'

    @property
    def options(self):
        """
        Assign a new value to the following variables if you would like to adjust them.

        ``spy.options.search_page_size`` (default: 1000)

            The number of items retrieved on each round-trip to the Seeq Server during
            a spy.search() call. If you have a fast system and fast connection, you can
            make this higher.

        ``spy.options.pull_page_size`` (default: 1000000)

            The number of samples/capsules retrieved on each round-trip to the Seeq
            Server during a spy.pull() call. If you have a slow system or slow
            connection, you may wish to make this lower. It is not recommended to
            exceed 1000000.

        ``spy.options.push_page_size`` (default: 100000)

            The number of samples/capsules uploaded during each round-trip to the Seeq
            Server during a spy.push() call. If you have a slow system or slow
            connection, you may wish to make this lower. It is not recommended to
            exceed 1000000.

        ``spy.options.max_concurrent_requests`` (default: 8)

            The maximum number of simultaneous requests made to the Seeq Server during
            spy.pull() and spy.push() calls. The higher the number, the more you can
            monopolize the Seeq Server. If you keep it low, then other users are less
            likely to be impacted by your activity.

        ``spy.options.retry_timeout_in_seconds`` (default: 5)

            The amount of time to spend retrying a failed Seeq Server API call in an
            attempt to overcome network flakiness.

        ``spy.options.clear_content_cache_before_render`` (default: False)

            When using spy.workbooks.pull(include_rendered_content=True), always
            re-render the content even if it had been previously rendered and cached.

        ``spy.options.allow_version_mismatch`` (default: False)

            Allow a major version mismatch between SPy and Seeq Server. (Normally,
            a mismatch raises a RuntimeError.)

        ``spy.options.friendly_exceptions`` (default: True if running in Data Lab, otherwise False)

            If True, exceptions raised in a Jupyter notebook will be displayed in a
            friendlier format. Stack traces will not be shown by default for most
            errors; error messages will precede the stack trace; and internal SPy
            code will be omitted from the stack trace.

        ``spy.options.default_timezone`` (default: None)

            If set to a timezone, this will be understood as the intended timezone
            for all naive datetimes passed as input to SPy. This will not override
            the timezone of any timezone-aware datetime. If set to None, naive
            datetimes will be interpreted as being in the logged-in user's preferred
            timezone. Timezone can be specified as str, pytz.timezone or dateutil.tzinfo.
        """
        return self._options

    @options.setter
    def options(self, value):
        self._options = value
