from __future__ import absolute_import, unicode_literals

import gettext
import os

# python3 /opt/Python-3.6.0b2/Tools/i18n/pygettext.py --extract-all --verbose flask_appsfoundry/*
# python3 /opt/Python-3.6.0b2/Tools/i18n/msgfmt.py translations/*/LC_MESSAGES/messages.po
TRANSLATION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'translations'))

english = gettext.translation('messages', TRANSLATION_DIR, ['en'])
indonesian = gettext.translation('messages', TRANSLATION_DIR, ['id'])



