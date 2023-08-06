#
# Copyright 2022 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import webbrowser


class BrowserMixin:
    """A mixin to allow opening a class' relevant URI in a web browser.

    Class must implement get_uri()
    """

    def get_uri(self) -> str:
        raise NotImplementedError

    def open_in_browser(self) -> bool:
        """
        Opens class' relevant web browser location.

        Note:
        If text-mode browsers are used, the calling process will block
        until the user exits the browser.

        Returns
        -------
        bool
            Whether or not the browser open action was successful

        """
        return webbrowser.open(self.get_uri())
