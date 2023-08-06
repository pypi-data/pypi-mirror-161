# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
import requests, warnings, os

if 'MQ_URL' not in os.environ:
    warnings.warn('if use distributed calculating, please configure MQ_URL')
    os.environ['MQ_URL'] = 'guet:guet@127.0.0.1:12345'

if 'NTN_URL' not in os.environ:
    warnings.warn('if use distributed calculating, please configure NTN_URL')
    os.environ['NTN_URL'] = 'guet:guet@127.0.0.1:12345/jdw'

if 'KN_MG' not in os.environ:
    warnings.warn('if use memory database, please configure KN_MG')
    os.environ['KN_MG'] = 'guet:guet@127.0.0.1:12345/jdw'

if 'DB_URL' not in os.environ:
    warnings.warn('if use sql database, please configure DB_URL')
    os.environ['DB_URL'] = 'guet:guet@127.0.0.1:12345/jdw'

if 'ATL_URL' not in os.environ:
    warnings.warn('if use trader, please configure KN_MG')
    os.environ['ATL_URL'] = 'guet:guet@127.0.0.1:12345/jdw'

import jdw.mfc.oss as OSSAPI
import jdw.data.DataAPI.mg as MGAPI
import jdw.data.DataAPI.db as DBAPI
import jdw.mfc.experimental.DataAPI.mg as ExperimentalAPI
try:
    import jdw.mfc.anode as AnodeAPI
except ImportError:
    warnings.warn("the environment cannot be traded")

from jdw.mfc.neutron.factory import Factory

from .version import __version__

try:
    unicode
except:
    unicode = str

session = requests.Session()

NeutronAPI = Factory()