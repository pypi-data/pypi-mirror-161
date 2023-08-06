# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import warnings
from . import seleya
from .DataAPI.db.fetch_engine import FetchEngine as DBFetchEngine
from .DataAPI.db.db_factory import *

from .DataAPI import REST as SeleyaAPI

#import .DataAPI.REST as SeleyaAPI

from .Toolset import *

try:
    from ultron.factor.data.standardize import standardize
    from ultron.factor.data.winsorize import winsorize_normal
    from ultron.factor.data.neutralize import neutralize
    from ultron.factor.data.processing import factor_processing
    from ultron import sentry
except ImportError:
    warnings.warn("If you need high-performance computing，please install Finance-Ultron.First make sure that the C++ compilation environment has been installed")

from .version import __version__