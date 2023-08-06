import typing
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import numpy
from .environment import http_get
from .utils import bucket_key

TEMPORARY_MAPPING = {
    "Wave_directional_width": "meanDirectionalSpread",
    "Mean_period_of_wind_waves": "peakPeriodWindWaves",
    "Mean_wave_period_of_first_swell_partition": "peakPeriodFirstSwell",
    "Mean_wave_period_of_second_swell_partition": "peakPeriodSecondSwell",
    "Mean_wave_period_of_third_swell_partition": "peakPeriodThirdSwell",
}

NAME_GFS = "GFS"
NAME_WW3 = "SofarOperationalWaveModel"
NAME_HYCOM = "HYCOM"

DEFAULT_MODEL_PER_CATAGORY = {
    "surfaceIce": NAME_GFS,
    "circulation": NAME_HYCOM,
    "surfaceWaves": NAME_WW3,
    "atmospheric": NAME_GFS,
}


@dataclass
class VariableInformation:
    sofar_name: str
    model_id: str
    catagory: str

    @property
    def model_cycle_period_hours(self):
        if self.model_id == "HYCOM":
            return 24
        elif self.model_id == "SofarOperationalWaveModel":
            return 6
        elif self.model_id == "GFS":
            return 6
        elif self.model_id == "GDAS":
            return 6
        else:
            Exception(f"unknown model {self.model_id}")

    @property
    def max_lead_time(self) -> timedelta:
        if self.model_id == "HYCOM":
            return timedelta(days=5)
        elif self.model_id == "SofarOperationalWaveModel":
            return timedelta(days=16)
        elif self.model_id == "GFS":
            return timedelta(days=16)
        elif self.model_id == "GDAS":
            return timedelta(days=1)
        else:
            Exception(f"unknown model {self.model_id}")

    @property
    def model_cycle_period_seconds(self):
        return self.model_cycle_period_hours * 3600

    def model_cycle_start_hours_zulu(self):
        if self.model_id == "HYCOM":
            return 12
        elif self.model_id == "SofarOperationalWaveModel":
            return 0
        elif self.model_id == "GFS":
            return 0
        elif self.model_id == "GDAS":
            return 0
        else:
            Exception(f"unknown model {self.model_id}")

    def nearest_init_time(self, valid_time: datetime) -> datetime:
        valid_time = valid_time.astimezone(timezone.utc)
        timestamp = valid_time.timestamp()
        init_time_timestamp = (
            int(
                int((timestamp - self.model_cycle_start_hours_zulu() * 3600) / self.model_cycle_period_seconds)
                * self.model_cycle_period_seconds
            )
            + self.model_cycle_start_hours_zulu() * 3600
        )
        return datetime.fromtimestamp(init_time_timestamp, tz=timezone.utc)

    def nearest_valid_time(self, valid_time: datetime) -> datetime:
        timestamp = valid_time.astimezone(tz=timezone.utc).timestamp()
        return datetime.fromtimestamp(
            (timestamp // (self.output_interval_hours() * 3600)) * self.output_interval_hours() * 3600
        )

    def valid_time_to_forecast_hour(self, time: datetime, lead_time: timedelta = None) -> typing.Tuple[datetime, int]:

        timestamp = time.astimezone(timezone.utc).timestamp()
        init_time = self.nearest_init_time(time)

        def round(i):
            # Avoid bankers rounding
            f = numpy.floor(i)
            return f if i - f < 0.5 else f + 1

        if lead_time:

            number_of_cycles = round(lead_time.total_seconds() / self.model_cycle_period_seconds)

            init_time = init_time - timedelta(seconds=number_of_cycles * self.model_cycle_period_seconds)

            if (
                time - init_time
            ).total_seconds() % self.model_cycle_period_seconds >= 0.5 * self.model_cycle_period_seconds:
                init_time = init_time + timedelta(seconds=self.model_cycle_period_seconds)

        hour = (timestamp - init_time.timestamp()) // 3600
        return init_time, int(hour)

    def output_interval_hours(self):
        if self.model_id == "HYCOM":
            return 3
        elif self.model_id == "SofarOperationalWaveModel":
            return 1
        elif self.model_id == "GFS":
            return 1
        elif self.model_id == "GDAS":
            return 1
        else:
            Exception(f"unknown model {self.model_id}")

    def variable_resolution(self):
        if self.model_id == "HYCOM":
            return "0p08"
        elif self.model_id == "SofarOperationalWaveModel":
            return "0p5"
        elif self.model_id == "GFS":
            return "0p25"
        elif self.model_id == "GDAS":
            return "0p25"
        else:
            Exception(f"unknown model {self.model_id}")


class raster:
    def __init__(self, data_dict):
        self.available = data_dict["available"]
        if self.available:
            self.dataRange = data_dict["dataRange"]
        else:
            self.dataRange = None


class OutputTimes:
    def __init__(self, data_dict):
        self.frequencyHours = data_dict["frequencyHours"]
        self.offset = data_dict["offset"]


class Stub:
    def __init__(self, data_dict):
        self.available = data_dict["available"]


class StormglassVariable:
    def __init__(self, data_dict):
        self.variableID = data_dict["variableID"]
        self.variableName = data_dict["variableName"]
        self.defaultPhysicalUnit = data_dict["defaultPhysicalUnit"]
        self.dataCategory = data_dict["dataCategory"]
        self.json = Stub(data_dict["json"])
        self.netcdf = Stub(data_dict["netcdf"])


class StormglassModelInfo:
    def __init__(self, data_dict):
        self.outputTimes = OutputTimes(data_dict["outputTimes"])
        self.modelID = data_dict["modelID"]
        self.description = data_dict["description"]
        self.variables = []
        for variable in data_dict["variables"]:
            self.variables.append(StormglassVariable(variable))

    def __str__(self):
        data = [x.variableName for x in self.variables]
        return "\n".join(data)


class InitTimes:
    def __init__(self, data_dict):
        self.variableID = data_dict["variableID"]
        self.variableName = data_dict["variableName"]
        self.initTime = data_dict["initTime"]
        self.availableAt = data_dict["availableAt"]

    def initTimeEpoch(self):
        formatting = "%Y-%m-%dT%H:%M:%S.%f%z"
        return int(datetime.timestamp(datetime.strptime(self.initTime, formatting)))


class StormglassInitTime:
    def __init__(self, data_dict):
        self.initTimes = [InitTimes(initTime) for initTime in data_dict["initTimes"]]
        self.dataFormat = data_dict["dataFormat"]
        self.requestTime = data_dict["requestTime"]
        self.modelID = data_dict["modelID"]


def get_gfs_info() -> StormglassModelInfo:
    return get_info(NAME_GFS)


def get_ww3_info() -> StormglassModelInfo:
    return get_info(NAME_WW3)


def get_hycom_info() -> StormglassModelInfo:
    return get_info(NAME_HYCOM)


def get_output_times(model_id, start: datetime, end: datetime, environment=None):
    start = datetime_to_iso_time_string(start)
    end = datetime_to_iso_time_string(end)

    result = http_get(
        f"models/{model_id}/outputTimes?" f"start={start}&end={end}",
        environment,
    ).json()
    return [to_datetime(output_time) for output_time in result["outputTimes"]]


def get_models():
    return http_get("models?dataFormat=netcdf").json()


def get_info(model) -> StormglassModelInfo:
    response = http_get(f"models/{model}?dataFormat=netcdf").json()
    return StormglassModelInfo(response)


def get_init_time_stormglass(
    model_id,
    variableIDs,
    timestamp: datetime,
    data_environment="production",
    cache=OrderedDict(),
    environment=None,
) -> StormglassInitTime:
    if not isinstance(variableIDs, str):
        variableIDs = ",".join(variableIDs)

    string_timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    hash = model_id + timestamp.strftime("%Y-%m-%dT%H")

    # Use a simple ordered dict as a fifo cache to cache queries.
    if hash in cache:
        return cache[hash]

    endpoint = (
        f"models/"
        f"{model_id}/init-times?"
        f"variableIDs={variableIDs}&"
        f"timestamp={string_timestamp}&"
        f"dataFormat=netcdf&"
        f"environment={data_environment}"
    )

    result = http_get(endpoint, environment).json()

    if len(cache) > 100:
        cache.pop(list(cache.keys())[0])

    cache[hash] = StormglassInitTime(result)
    return StormglassInitTime(result)


def get_init_time(
    model_id,
    variableIDs,
    valid_time: datetime = None,
    environment="production",
):
    """
    Get the closest model init time for a given valid_time. If no valid_time is
    given use _now_ as the valid time.

    :param model_id:
    :param variableIDs:
    :param valid_time:
    :param environment:
    :return:
    """
    if valid_time is None:
        valid_time = datetime.now(tz=timezone.utc)

    init_times_sg = get_init_time_stormglass(model_id, variableIDs, valid_time, environment)
    init_times_str = [x.initTime for x in init_times_sg.initTimes]

    return [to_datetime(t) for t in init_times_str]


def download_netcdf(
    file,
    variable: VariableInformation,
    init_time: datetime,
    forecastHour="full_forecast",
    domain="global",
    legacy=False,
    environment="production",
    data_environment="production",
    experiment=None,
):
    resolution = variable.variable_resolution()
    variable_id = variable.sofar_name
    model_id = variable.model_id

    if experiment or data_environment != "production":
        # for "experiments" we construct the key/bucket ourselves
        bucket, key = bucket_key(
            variable_id,
            model_id,
            init_time,
            forecastHour,
            data_environment,
            resolution,
            domain,
            experiment,
        )
        _ = download_file_from_bucket(key, file, bucket)
    else:
        if forecastHour is None:
            hour = "full_forecast"
        else:
            if forecastHour == "full_forecast":
                hour = "full_forecast"
            else:
                hour = "f%03i" % (forecastHour)

        init_time_string = datetime_to_iso_time_string(init_time)

        endpoint = (
            f"models/{model_id}/"
            f"forecast/netcdf/{variable_id}/"
            f"{init_time_string}/"
            f"{domain}?forecastHour={hour}&resolution={resolution}"
        )

        response = http_get(endpoint, environment=environment)
        with open(file, "wb") as f:
            f.write(response.content)

    if legacy == True:
        convert_to_legacy_netcdf(file, file)

    return file


def get_sofar_name(variable):
    endpoint = f"terms/variable?term={variable}"
    return http_get(endpoint).json()["sofarName"]


def get_variable_information(variable, model_id=None, environment=None) -> VariableInformation:
    if variable in TEMPORARY_MAPPING:
        # A Hack to resolve some missing mappings in the api.
        variable = TEMPORARY_MAPPING[variable]

    endpoint = f"terms/variable?term={variable}"
    data = http_get(endpoint, environment=environment).json()

    if model_id is None:
        model_id = DEFAULT_MODEL_PER_CATAGORY[data["category"]]
    else:
        for model in data["models"]:
            if model["soferName"] == model_id:
                break
        else:
            raise Exception(f"no model found for {variable} with model id {model_id}")

    return VariableInformation(
        sofar_name=data["sofarName"],
        model_id=model_id,
        catagory=data["category"],
    )
