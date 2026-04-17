from plugins.checks_2d_x1d import Checks2DX1DPlugin
from plugins.hpc_dt import HPCDTPlugin
from plugins.mb import MBPlugin
from plugins.mb1d import MB1DPlugin
from plugins.mb2d import MB2DPlugin
from plugins.mb_hpc import MBHPCPlugin
from plugins.messages import Messages
from plugins.oned_mb import OnedMBPlugin
from plugins.po import POPlugin
from plugins.run_stats import RunStats
from plugins.simulations_log import SimulationsLog
from plugins.start_stats import StartStats
from plugins.tlf_defaults import TLFSummaryPlugin
from plugins.tsf_summary import TSFSummaryPlugin

# Add any additional plugins here (after importing them above)
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
    TLFSummaryPlugin(),
    RunStats(),
    StartStats(),
    Messages(),
    SimulationsLog()
]

def find_plugin(filename: str):
    filename = filename.lower().strip()

    for plugin in PLUGINS:
        if plugin.matches(filename):
            return plugin
    return None