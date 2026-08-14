from pydantic import BaseModel, Field, ConfigDict

# telemtry data structure for UAV simulation
# enforces strict type matching and removes coercion
class telemetryData(BaseModel):

    #strict construction so no invalid params
    model_config = ConfigDict(
        strict=True,
        validate_assignment=True)  #disallow assignments so something like telemetryData.alt = -5 throws an exception

    deviceName: str
    sequence: int = Field(..., ge=0)
    altitude: int = Field(..., ge=0)
    speed: float = Field(..., ge=0.0)