from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class Size(BaseModel):
    width: int
    height: int
    depth: int


class Source(BaseModel):
    database: str


class BndBox(BaseModel):
    xmin: int
    xmax: int
    ymin: int
    ymax: int


class Object(BaseModel):
    name: str
    pose: str
    truncated: int
    difficult: int
    occluded: int
    bndbox: BndBox
    polygon: Optional[Dict[str, int]]

    def is_rle(self) -> bool:
        return False

    def is_polygon(self) -> bool:
        return self.polygon is not None

    def polygon_to_list_coordinates(self) -> List[List[int]]:
        if not self.is_polygon():
            raise ValueError("Not a polygon")

        coords = []
        for i in range(1, 1 + len(self.polygon) // 2):
            x = "x" + str(i)
            y = "y" + str(i)
            if x not in self.polygon or y not in self.polygon:
                raise ValueError("{} or {} not found in this polygon.".format(x, y))

            coords.append([self.polygon[x], self.polygon[y]])

        return coords


class Annotation(BaseModel):
    filename: str
    object: Union[Object, List[Object]]
    path: Optional[str]
    folder: Optional[str]
    source: Optional[Source]
    size: Optional[Size]
    segmented: Optional[int]


class PascalVOCFile(BaseModel):
    annotation: Annotation
