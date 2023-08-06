from typing import Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)
    altitude: Optional[float] = Field(None)


class ImageMediaMetadata(BaseModel):
    width: Optional[int] = Field(None)
    height: Optional[int] = Field(None)
    rotation: Optional[int] = Field(None)
    location: Optional[Location] = Field(None)
    time: Optional[str] = Field(None)
    camera_make: Optional[str] = Field(None, alias="cameraMake")
    camera_model: Optional[str] = Field(None, alias="cameraModel")
    exposure_time: Optional[float] = Field(None, alias="exposureTime")
    aperture: Optional[float] = Field(None)
    flash_used: Optional[bool] = Field(None, alias="flashUsed")
    focal_length: Optional[float] = Field(None, alias="focalLength")
    iso_speed: Optional[int] = Field(None, alias="isoSpeed")
    metering_mode: Optional[str] = Field(None, alias="meteringMode")
    sensor: Optional[str] = Field(None)
    exposure_mode: Optional[str] = Field(None, alias="exposureMode")
    color_space: Optional[str] = Field(None, alias="colorSpace")
    white_balance: Optional[str] = Field(None, alias="whiteBalance")
    exposure_bias: Optional[float] = Field(None, alias="exposureBias")
    max_aperture_value: Optional[float] = Field(None, alias="maxApertureValue")
    subject_distance: Optional[int] = Field(None, alias="subjectDistance")
    lens: Optional[str] = Field(None)
