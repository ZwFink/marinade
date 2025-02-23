import sauerkraut as skt
import greenlet
class RegionInfo:
    def __init__(self, region_name: str, serialized_frame: bytes, frame_file: str, frame_lineno: int):
        self.region_name = region_name
        self.serialized_frame = serialized_frame
        self.frame_file = frame_file
        self.frame_lineno = frame_lineno
        self.is_complete = False
        self.is_replay = False

    def mark_end(self):
        self.is_complete = True

    def __str__(self):
        return f"RegionInfo(region_name={self.region_name}," \
               f"frame_file={self.frame_file}," \
               f"frame_lineno={self.frame_lineno}," \
               f"is_complete={self.is_complete})"

class MarinadeState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarinadeState, cls).__new__(cls)
            cls._instance._regions = dict()
        return cls._instance

    def mark_region_begin(self, region_name: str, _serialized_frame: bytes, frame_file: str, frame_lineno: int):
        self._regions[region_name] = RegionInfo(region_name, _serialized_frame, frame_file, frame_lineno)

        print(f"Marking region begin: {region_name}")

    def mark_region_end(self, region_name: str):
        print(f"Marking region end: {region_name}")
        self._regions[region_name].mark_end()

    def get_region_info(self, region_name: str):
        return self._regions[region_name]

    def replay_region(self, region_name: str):
        self._regions[region_name].is_replay = True

def mark_region_begin(region_name: str):
    import inspect
    this_frame = inspect.currentframe()
    _serialized_frame = skt.copy_frame(this_frame, serialize=True)
    frame_file = this_frame.f_code.co_filename
    frame_lineno = this_frame.f_lineno

    MarinadeState().mark_region_begin(region_name, _serialized_frame, frame_file, frame_lineno)

def mark_region_end(region_name: str):
    region_info = MarinadeState().get_region_info(region_name)
    if region_info.is_replay:
        region_info.is_replay = False
        greenlet.getcurrent().parent.switch()
    else:
        MarinadeState().mark_region_end(region_name)

def get_region_info(region_name: str):
    return MarinadeState().get_region_info(region_name)

def replay_region(region_name: str, overrides: dict = None):
    region_info = MarinadeState().get_region_info(region_name)
    if not region_info.is_complete:
        error_str = "Attempt to replay region "
        error_str += f"{region_name} that is not complete"
        raise Exception(error_str)
    else:
        print(f"Replaying region {region_name}")
        region_info.is_replay = True
        frame = region_info.serialized_frame
        grlt_fn = lambda: skt.deserialize_frame(frame, run=True, replace_locals=overrides)
        grlt = greenlet.greenlet(grlt_fn)
        grlt.switch()
        print(f"Finished replaying region {region_name}")
        region_info.is_replay = False

