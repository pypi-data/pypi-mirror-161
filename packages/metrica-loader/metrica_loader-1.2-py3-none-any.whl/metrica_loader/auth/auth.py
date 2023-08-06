#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 14:12:12 2022.

@author: gp
"""
import requests


class OAuth(
        requests.auth.AuthBase
        ):
    """
    Headers for future requests.

    Parameters
    ----------
    requests.auth.AuthBase : object

    Returns
    -------
    None.
    """

    def __init__(self, token):
        """
        Инициализатор коннектора.

        Parameters
        ----------
        token : str
            Токен для аутентификации.

        Returns
        -------
        None.

        """
        self.token = token

    def __call__(self, r):
        """
        Возвращает измененный request.

        Parameters
        ----------
        r : obj
            Request запрос.

        Returns
        -------
        r : obj
            Request запрос..

        """
        r.headers["authorization"] = "OAuth " + self.token
        return r
