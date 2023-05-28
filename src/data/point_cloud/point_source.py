from src.data.point_cloud.ept import EPTData
from src.data.point_cloud.tile import TileData

PDALStage = dict


def vendor_classified_ground_points(
    ept_data: EPTData,
    tile_data: TileData,
) -> list[PDALStage]:
    return [
        {
            "tag": "raw_points",
            "type": "readers.ept",
            "filename": ept_data.ept_json_url,
            "polygon": tile_data.ept_filter_as_wkt,
        },
        {
            "tag": "ground_only",
            "inputs": ["raw_points"],
            "type": "filters.range",
            "limits": "Classification[2:2]",
        },
        {
            "tag": "vendor_classified_ground_points",
            "inputs": ["ground_only"],
            "type": "filters.reprojection",
            "out_srs": f"EPSG:{tile_data.epsg}",
        },
    ]
