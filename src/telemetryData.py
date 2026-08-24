from pydantic import BaseModel, ConfigDict, Field


class telemetryData(BaseModel):
    """Validated telemetry packet for a simulated UAV."""

    model_config = ConfigDict(
        strict=True,
        validate_assignment=True
    )

    deviceName: str = Field(pattern=r"^UAV-\d{3}$")
    sequence: int = Field(ge=1)
    altitude: int = Field(ge=0, le=30000)
    speed: float = Field(ge=0.0, le=500.0)