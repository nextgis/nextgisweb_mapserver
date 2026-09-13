from mapscript import MS_VERSION

from nextgisweb.core.sys_info import SysInfoResult, sys_info_hook

from .component import MapserverComponent


@sys_info_hook()
def sys_info(comp: MapserverComponent) -> SysInfoResult:
    yield (
        "MapServer",
        MS_VERSION,
    )
