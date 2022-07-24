from __future__ import absolute_import, unicode_literals
import json
import unittest

from flask import Flask, request
from flask_babel import Babel, gettext, refresh, get_locale, get_translations, gettext
from six.moves.http_client import NOT_FOUND

from flask.ext.appsfoundry.dummy_app import dummy_app, babel
from flask_appsfoundry.exceptions import NotFound


class TestTranslations(unittest.TestCase):

    def test_bahasa_localization(self):
        """ BASIC: Make sure the language can be switched to bahasa indonesia
        """
        c = localized_app.test_client(use_cookies=False)

        indonesian_response = c.get('/not-found-in-bahasa', headers=[("Accept-Language", "id")])

        self.assertEqual(
            indonesian_response.status_code,
            NOT_FOUND
        )

        self.assertEqual(
            json.loads(indonesian_response.data)['user_message'],
            'Data tidak ditemukan.'
        )

    def test_english_localization(self):
        """ BASIC: Make sure the language can be switched to bahasa indonesia
        """
        c = localized_app.test_client(use_cookies=False)
        english_response = c.get('/not-found-in-english')

        self.assertEqual(
            english_response.status_code,
            NOT_FOUND
        )

        self.assertEqual(
            json.loads(english_response.data)['user_message'],
            'The requested resource could not be found.'
        )

    def test_english_via_header(self):
        """ BASIC: Make sure the language can be switched to bahasa indonesia
        """
        c = localized_app.test_client(use_cookies=False)
        english_response = c.get('/not-found-in-english-via-header',
                                 headers=[("Accept-Language", "da, en-gb;q=0.8, en;q=0.7")])

        self.assertEqual(
            english_response.status_code,
            NOT_FOUND
        )

        self.assertEqual(
            json.loads(english_response.data)['user_message'],
            'The requested resource could not be found.'
        )


localized_app = dummy_app


# @babel.localeselector
# def get_locale():
#     return 'id'

@babel.localeselector
def get_locale():
    translations = [str(translation) for translation in babel.list_translations()]
    selected_language = request.accept_languages.best_match(translations)
    return selected_language if selected_language else 'en'


@localized_app.route('/not-found-in-bahasa')
def not_found_indonesian():
    raise NotFound


@localized_app.route('/not-found-in-english')
def not_found_english():
    raise NotFound


@localized_app.route('/not-found-in-english-via-header')
def not_found_english2():
    raise NotFound
