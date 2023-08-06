from dataclasses import dataclass
from typing import List, Optional, Tuple

from marshmallow import Schema, fields, post_load


@dataclass
class PlotParameters:
    grid: bool = False
    xlim: Tuple[Optional[float], Optional[float]] = (None, None)
    ylim: Tuple[Optional[float], Optional[float]] = (None, None)
    xlabel: str = ""
    ylabel: str = ""
    xticks: Optional[list] = None
    yticks: Optional[list] = None
    title: str = ""
    ticks_direction: str = "in"
    xscale = "linear"
    basex = 10
    yscale = "linear"
    basey = 10


@dataclass
class PanelConfig:
    id: str
    coords: Tuple[float, ...]
    params: PlotParameters


@dataclass
class VisualizerConfig:
    output_dir: str
    title: str
    figsize: Tuple[int, ...]
    pic_filename: str
    panels: List[PanelConfig]


class PlotParametersSchema(Schema):
    grid = fields.Bool()
    xlim = fields.List(fields.Float())
    ylim = fields.List(fields.Float())
    xlabel = fields.Str()
    ylabel = fields.Str()
    xticks = fields.List(fields.Float())
    yticks = fields.List(fields.Float())
    title = fields.Str()
    ticks_direction = fields.Str()
    xscale = fields.Str()
    basex = fields.Int()
    yscale = fields.Str()
    basey = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        return PlotParameters(**data)


class PanelSchema(Schema):
    id = fields.Str(required=True, description="Id of the panel. Should be unique.")
    coords = fields.List(
        fields.Float(),
        load_default=(0, 1, 1, 1),
        description="Position and size of the graph in form of [x, y, width, height]. "
        "Coordinates are counted from the left bottom of the picture.",
    )
    params = fields.Nested(
        PlotParametersSchema,
        description="Parameters of the graph box. They should be given the same names as ones in "
        "matplotlib.pyplot (and proper values) as most of them are just passed along to it.",
    )

    @post_load
    def make(self, data, **kwargs):
        return PanelConfig(**data)


class VisualizerConfigSchema(Schema):
    output_dir = fields.Str(
        required=True, description="Output directiry where the images would be saved."
    )
    title = fields.Str(
        load_default="",
        description="Title template. Use {time} to get time in Myr. One can use standart python "
        "formatters to format number of digits, rounding, etc.",
    )
    figsize = fields.List(fields.Int(), load_default=(16, 9), description="Figure size in inches.")
    pic_filename = fields.Str(
        load_default="img-{i:03d}.png",
        description="Pictures will be saved in output_dir with this filename. "
        "{i} is iteration number.",
    )
    panels = fields.List(
        fields.Nested(PanelSchema),
        required=True,
        description="List of panels, their layouts and properties.",
    )

    @post_load
    def make(self, data, **kwargs):
        return VisualizerConfig(**data)
