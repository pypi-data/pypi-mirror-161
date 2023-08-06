# -*- coding: utf-8 -*-
# flake8: noqa : F401
"""
jf-ext.__init__.py
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

# pragma mark - BasicType
# --------------------------------------------------------------------------------
from .BasicType.DictExt import *
from .BasicType.FloatExt import *
from .BasicType.JsonExt import *
from .BasicType.ListExt import *
from .BasicType.StringExt import *

# pragma mark - Time
# --------------------------------------------------------------------------------
from .Time.DateExt import *
from .Time.TimeExt import *

# pragma mark - Mgr
# --------------------------------------------------------------------------------
from .Mgr.mailMgr import MailMgr
from .Mgr.redisMgr import RedisMgr
from .Mgr.responseMgr import APIResponse, APIResponseType


from .CommonExt import *
from .CurencyExt import *
from .EncryptExt import *
from .IpExt import *
from .PrintExt import *
from .RequestExt import *
from .SingletonExt import *
from .ValidExt import *
from .fileExt import *
