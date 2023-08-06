# -*- coding: utf-8 -*-
"""Projection mapping for French area
Utility fuction for guessing projection from (median) X and Y coords
Utility function for retrieving CRS from model"""
import os.path as OP
import re


class FrenchProjMapping:
    """Mapping symbolic name to / EPSG:xxxx"""

    def __init__(self) -> None:
        self.mapping = {
            "wgs84": "EPSG:4326",  # geoCRS 2D
            "lamb93": "EPSG:2154",  # RGF93 / Lambert93 (projCRS)
            "rgf93": "EPSG:4171",  # RGF93 2D
            "lambN": "EPSG:27561",
            "lambC": "EPSG:27562",
            "lambS": "EPSG:27563",
            "lambCorse": "EPSG:27564",
            "ntf": "EPSG:4275",
            "ntfparis": "EPSG:4807",
            "lamb1": "EPSG:27571",
            "lamb2": "EPSG:27572",
            "lamb3": "EPSG:27573",
            "utm20n": "EPSG:4559",  # Martinique - Guadeloupe
            "rgaf09": "EPSG:5490",  # MArtinique RGAF09 (EPSG5490).
            "utm40s": "EPSG:2975",  # Réunion
            "utm22n": "EPSG:2972",  # Guyanne
            # 'autre': "EPSG:0000",
            "macao": "EPSG:8433",
            # 'macau': b'+ellps=intl +proj=tmerc +lat_0=22.212222 +lon_0=113.536389 +k=1.000000 +x_0=20000.0 +y_0=20000.0 +units=m'
            "macau": "+ellps=intl +proj=tmerc +lat_0=22.212222 +lon_0=113.536389 +k=1.000000 +x_0=19685.0 +y_0=20115.0 +units=m",
        }
        for lat in range(42, 51):
            self.mapping["rgf93-cc" + str(lat)] = f"EPSG:{3900+lat:4d}"
        self.inv_map = {v: k for k, v in self.mapping.items()}

    def __getitem__(self, symb: str, owner=None) -> str:
        """epsg getter"""
        return self.mapping[symb]

    def __setitem__(self, symb: str, value: str) -> None:
        """epsg setter - remove duplicates"""
        if symb and value:
            value = value.upper()
            if symb in self.mapping:
                del self.inv_map[value]
            if value in self.inv_map:
                del self.mapping[symb]
            self.mapping[symb] = value
            self.inv_map[value] = symb

    def keys(self):
        """Returns symbolic CRS as keys"""
        return self.mapping.keys()

    def values(self):
        """Returns CRS as values"""
        return self.mapping.values()

    def epsg2symb(self, epsg: str, default="autre") -> str:
        """Returns symb associated to epsg if present; or 'autre'"""
        if not epsg:
            return ""
        epsg = epsg.upper()
        if epsg not in self.inv_map and default:
            # self[default] = epsg
            self.__setitem__(default, epsg)
        return self.inv_map[epsg]


def guess_proj(point_or_module, as_epsg: bool = False) -> str:
    """Projection guess according to an x, y point or average model coords"""
    if isinstance(point_or_module, (tuple, list)):
        x, y, *_ = point_or_module
    else:
        # get median coords from the model
        pic = point_or_module
        if not pic.nbobjects(pic.NODE):
            return "aucune"
        x = float(pic.getvar("Q50:NOEUD.X"))
        y = float(pic.getvar("Q50:NOEUD.Y"))

    if x < 1200000:
        if x < 180 and y < 85 or y < 180 and x < 85:
            theprj = "wgs84"
        elif y < 600000:
            if x < 350000:
                theprj = "lambCorse"
            else:
                theprj = "lambN"
        elif y < 2800000:
            theprj = "lamb2"
        else:
            theprj = "lamb93"
    else:  # lambert CC42 à 50
        theprj = "rgf93-cc" + str(42 + (int(y) - 700000) // 1000000)

    return FrenchProjMapping()[theprj] if as_epsg else theprj


def get_spatial_ref(pic_module, model_file: str = "") -> str:
    """Returns model CRS (spatial-ref)"""
    crs = pic_module.getvar("SPATIAL-REF")
    if crs and "#" not in crs:
        return crs
    # if getvar not implemented, try finding SPATIAL-REF in model file
    model_name, model_type = OP.splitext(model_file)
    if model_type.lower() == ".bin":
        for mtype in (".dat", ".pic"):
            if OP.exists(mfile := model_name + mtype):
                model_type, model_file = mtype, mfile
                break
    if model_type.lower() in (".dat", ".pic"):
        if not OP.exists(model_file):
            return crs
        with open(model_file, "r", encoding="cp1252") as fmod:
            for line in fmod:
                if m := re.search(r'SPATIAL-REF\s+"?(EPSG:\d+)', line, re.IGNORECASE):
                    print("CRS found for model file:", OP.basename(model_file))
                    return m[1].upper()
    return crs
