from plugins.hpc_dt import HPCDTPlugin
from plugins.oned_mb import OnedMBPlugin
from plugins.mb import MBPlugin
from plugins.mb2d import MB2DPlugin
from plugins.mb_hpc import MBHPCPlugin
from plugins.mb1d import MB1DPlugin
from plugins.po import POPlugin
from plugins.checks_2d_x1d import Checks2DX1DPlugin
from plugins.tsf_summary import TSFSummaryPlugin
from plugins.tlf_defaults import TLFSummaryPlugin


PLUGINS = [
    OnedMBPlugin(),
    HPCDTPlugin(),
    MBPlugin(),
    MB2DPlugin(),
    MBHPCPlugin(),
    MB1DPlugin(),
    POPlugin(),
    Checks2DX1DPlugin(),
    TSFSummaryPlugin(),
    TLFSummaryPlugin()
]



def find_plugin(filename: str):
    filename = filename.lower().strip()

    for plugin in PLUGINS:
        if plugin.matches(filename):
            return plugin
    return None