from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional
from ..Models import AresSchemaEntry

@dataclass
class VisualizationDataPoint:
    """A single indexed point supplied to a visualization callback."""

    index: int
    values: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VisualizationRequest:
    """Native representation of a visualization update request."""

    visualization_name: str
    visualization_data: list[VisualizationDataPoint] = field(default_factory=list)


@dataclass
class VisualizationOption:
    """Describes a visualization advertised to ARES."""

    visualization_name: str
    visualization_input_schema: Optional[Mapping[str, AresSchemaEntry]] = None
    visualization_settings_schema: Optional[Mapping[str, AresSchemaEntry]] = None
    chart_type: str = ""