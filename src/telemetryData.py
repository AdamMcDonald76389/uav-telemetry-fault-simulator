from pydantic import BaseModel, Field, ConfigDict

# telemtry data structure for UAV simulation
# enforces strict type matching and removes coercion
class telemetryData(BaseModel):

    model_config = ConfigDict(strict=True)

    deviceName: str
    sequence: int = Field(..., ge=0)
    altitude: int = Field(..., ge=0)
    speed: float = Field(..., ge=0.0)