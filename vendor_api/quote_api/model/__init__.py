# -*- coding: utf-8 -*-

try:
    from .spk_util import *
    from .spk_util import (
        SEndpointContextT as MdsAsyncApiContextT,
        SEndpointChannelT as MdsAsyncApiChannelT,
        SEndpointChannelCfgT as MdsAsyncApiChannelCfgT,
        SGeneralClientAddrInfoT as MdsApiAddrInfoT,
        SGeneralClientRemoteCfgT as MdsApiRemoteCfgT,
    )
except ImportError:
    from sutil.spk_util import *
    from sutil.spk_util import (
        SEndpointContextT as MdsAsyncApiContextT,
        SEndpointChannelT as MdsAsyncApiChannelT,
        SEndpointChannelCfgT as MdsAsyncApiChannelCfgT,
        SGeneralClientAddrInfoT as MdsApiAddrInfoT,
        SGeneralClientRemoteCfgT as MdsApiRemoteCfgT,
    )

from .mds_base_model import *
from .mds_mkt_packets import *
from .mds_qry_packets import *
