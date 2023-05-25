from dataclasses import dataclass

from pyproj import CRS
from pystac import Item
from pystac_client import Client


@dataclass
class EPTData:
    workunit: str
    crs: CRS
    ept_json_url: str


def _get_first_matching_stac_item(stac_catalog_url: str, workunit: str) -> Item:
    client = Client.open(stac_catalog_url)
    item_links = [link for link in client.get_item_links() if workunit in link.href]
    return Item.from_file(item_links[0].href)


def fetch_ept_data(workunit: str) -> EPTData:
    stac_catalog_url = (
        "https://usgs-lidar-stac.s3-us-west-2.amazonaws.com/ept/catalog.json"
    )
    item = _get_first_matching_stac_item(stac_catalog_url, workunit)
    return EPTData(
        workunit=workunit,
        crs=CRS.from_epsg(item.properties["proj:epsg"]),
        ept_json_url=item.assets["ept.json"].href,
    )
