import requests


class HarpiaException(Exception):
    pass


class HarpiaConnector:
    def __init__(self, API_BASE_URL="http://localhost:20050/v1/"):
        self._API_BASE_URL = API_BASE_URL

    def _api(self, method="get", path="/", json_body=None, error_message=None):
        assert method in ("get", "put", "post")
        assert isinstance(path, str)
        assert not (
            method == "get" or json_body is not None
        ), "GET requests cannot have a body"
        assert not (
            method == "put" and json_body is None
        ), "PUT requests must have a body"

        url = self._API_BASE_URL + path.lstrip("/")

        if method == "get":
            response = requests.get(url)
        elif method == "put":
            response = requests.put(
                url, json=json_body, headers={"Content-Type": "application/json"}
            )
        elif method == "post":
            response = requests.post(url, json=json_body)

        if not response.ok:
            if error_message:
                raise HarpiaException(error_message)
            else:
                raise HarpiaException(
                    f"Request to {path} failed with status code {response.status_code}"
                )

        return response.json()  # Return the JSON response


class Shutters(HarpiaConnector):
    all_shutters = ("pump", "probe", "gate")

    def open(self, shutter):
        assert (
            shutter in self.all_shutters
        ), f"Invalid shutter. Use one of {self.all_shutters}"
        self._api(
            "post",
            f"Shutters/Open{shutter.capitalize()}Shutter",
            error_message=f"Failed to open {shutter} shutter",
        )

    def close(self, shutter):
        assert (
            shutter is None or shutter in self.all_shutters
        ), f"Invalid shutter. Use one of {self.all_shutters}"

        if not shutter:
            for s in self.all_shutters:
                self._api(
                    "post",
                    f"Shutters/Close{s.capitalize()}Shutter",
                    error_message=f"Failed to close {s} shutter",
                )
        else:
            self._api(
                "post",
                f"Shutters/Close{shutter.capitalize()}Shutter",
                error_message=f"Failed to close {shutter} shutter",
            )


class DelayLine(HarpiaConnector):
    def set(self, delay):
        self._api(
            "put", "DelayLine/TargetDelay", delay, error_message="Failed to set delay"
        )


class Harpia(HarpiaConnector):
    def read_PumpProbeSpectrum(self, delay):
        if delay is None:
            return self._api("get", "Basic/PumpProbeSpectrum/false")

        return self._api("get", f"Basic/PumpProbeSpectrum/{delay}/false")

    def set_spa(self, spectra_per_acquisition):
        assert (
            isinstance(spectra_per_acquisition, int) and spectra_per_acquisition > 0
        ), "Invalid spectra_per_acquisition"
        self._api(
            "put",
            "Basic/NumberOfSpectraPerAcquisition",
            str(spectra_per_acquisition),
            error_message="Failed to set spectra_per_acquisition",
        )
