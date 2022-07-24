from __future__ import absolute_import, unicode_literals
from flask import request

from .helpers import assert_user_has_any_permission


def user_has_any_tokens(redis, app_conf, token_prefix, req=request, *tokens):

    def decorated(func):

        def inner(*args, **kwargs):
            assert_user_has_any_permission(redis, app_conf, token_prefix, req, tokens)
            return func(*args, **kwargs)
        return inner

    return decorated









