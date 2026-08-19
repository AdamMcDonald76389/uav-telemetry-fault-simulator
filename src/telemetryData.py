from pydantic import BaseModel, Field, ConfigDict

# telemtry data structure for UAV simulation
# enforces strict type matching and removes coercion
class telemetryData(BaseModel):

    #strict construction so no invalid params
    model_config = ConfigDict(
        strict=True,
        validate_assignment=True)  #revalidate assignments to verify in bounds
    #Regex that acts as a bandaid fix for *some data corruption
    #Ensures that Valid UAV names are in format UAV-numbers 000-999
    deviceName: str Field(pattern=r"^UAV-\d{3}$")
    sequence: int = Field(..., ge=1)
    altitude: int = Field(..., ge=0, le=30000)
    speed: float = Field(..., ge=0.0, le=500.0)
