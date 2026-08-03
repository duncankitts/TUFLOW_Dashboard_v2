from plugins.cfl_dt import CFLDTPlugin
from plugins.checks_2d_x1d import Checks2DX1DPlugin
from plugins.eof import EOFPlugin
from plugins.fv_flux import FVFluxPlugin
from plugins.fv_mass import FVMassPlugin
from plugins.fv_points import FVPoints_Plugin
from plugins.fv_structflux import FVSTRUCTFlux_Plugin
from plugins.fvwq_mass_balance import FV_wq_mb_Plugin
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
from plugins.fv_log import FVlog_Plugin

PLUGIN_CLASSES = [
    OnedMBPlugin,
    HPCDTPlugin,
    MBPlugin,
    MB2DPlugin,
    MBHPCPlugin,
    MB1DPlugin,
    POPlugin,
    Checks2DX1DPlugin,
    TSFSummaryPlugin,
    TLFSummaryPlugin,
    RunStats,
    StartStats,
    Messages,
    SimulationsLog,
    FVlog_Plugin,
    EOFPlugin,
    FVMassPlugin,
    FVFluxPlugin,
    FVSTRUCTFlux_Plugin,
    FVPoints_Plugin,
    FV_wq_mb_Plugin,
    CFLDTPlugin,
]

PLUGINS = [plugin_class() for plugin_class in PLUGIN_CLASSES]

def find_plugin(filename: str):
    filename = filename.lower().strip()

    for plugin in PLUGINS:
        if plugin.matches(filename):
            return plugin
    return None