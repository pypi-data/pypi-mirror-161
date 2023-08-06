import json
import xml.etree.ElementTree as ET

import numpy as np


class cziArray:
    _dim_trans = {"X": "x", "Y": "y", "M": "tile", "C": "channel", "S": "z"}

    def __init__(self, czifile):
        self._czi = czifile

    def __getitem__(self, *args):
        sec = {}
        for d, v in zip(list(self._czi.dims), args[0]):
            if d in ["X", "Y"]:  # X and Y are special and read_image returns full tiles
                continue
            sec[d] = v.start
        try:
            img = self._czi.read_image(**sec)[0]
        except Exception:  # PylibCZI_CDimCoordinatesOverspecifiedException
            return np.zeros(self.chunks, self.dtype)
        return img.astype(self.dtype)

    @property
    def shape(self):
        return self._czi.size

    @property
    def dtype(self):
        return "uint16"

    @property
    def ndim(self):
        return len(self.shape)

    @property
    def dimensions(self):
        dim = {}
        dims_shape = self._czi.get_dims_shape()[0]
        for item in list(self._czi.dims):
            name = self._dim_trans[item]
            shape = dims_shape[item]
            dim[name] = range(shape[0], shape[1])
        return dim

    @property
    def chunks(self):
        return (1,) * len(self.shape[:-2]) + self.shape[-2:]

    def _boundingboxes(self):
        """
        Return the X,Y position of all the tiles inside a
        czi file as a dict
        """

        dims = self._czi.get_dims_shape()[0]

        mosaic_positions = []

        for i_t in range(dims["M"][1]):  # tile
            bb = self._czi.get_mosaic_tile_bounding_box(C=0, M=i_t, S=0)
            temp = [bb.y, bb.x, bb.h, bb.w]
            mosaic_positions.append(temp)
        return mosaic_positions

    def mosaic_bounding_box(self):
        bb = self._czi.get_mosaic_bounding_box()
        return [bb.y, bb.x, bb.h, bb.w]

    @property
    def scale(self, unit=1.0e6):
        try:
            scale_y = (
                float(
                    self._czi.meta.findall(".//Distance[@Id='Y']")[0]
                    .find("./Value")
                    .text
                )
                * unit
            )
            scale_x = (
                float(
                    self._czi.meta.findall(".//Distance[@Id='X']")[0]
                    .find("./Value")
                    .text
                )
                * unit
            )
        except Exception:
            scale_y = scale_x = 0.0
        return {"x": scale_x, "y": scale_y}

    @property
    def metadata(self):
        xmlmeta = ET.tostring(self._czi.meta)
        mosaic_positions = self._boundingboxes()
        raw_meta = {
            "Metadata": xmlmeta.decode(),
            "mosaic_positions": mosaic_positions,
            "mosaic_boundingbox": self.mosaic_bounding_box(),
            "scale": json.dumps(self.scale),
        }
        return raw_meta
