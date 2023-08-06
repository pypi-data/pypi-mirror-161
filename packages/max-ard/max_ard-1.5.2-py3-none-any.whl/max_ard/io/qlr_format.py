""" Convert ARDCollections to QGIS Layer format"""


from collections import defaultdict
from uuid import uuid4

from pyproj import Proj

from max_ard.dependency_support import HAS_FIONA
from max_ard.exceptions import MissingDependency

if HAS_FIONA:
    import fiona

__all__ = ("QlrDoc",)


def QlrDoc(collection, public=False):
    """Return a an ARDCollection as a QGIS layer file

    Parameters
    ----------
    collection : ARDCollection
    public : bool, optional
      True if the data is in a public S3 bucket location (see Notes)

    Returns
    -------
    str
      QLR document contents of the ARDCollection

    Notes
    -----
    Passing `public=true` will convert s3:// URLs to the public http:// S3 endpoints.
    This functionality does not work yet for other storage types. It's functionality
    is primarily for creating QLRs of the official Maxar ARD sample datasets at
    http://maxar-ard-samples.s3-website-us-east-1.amazonaws.com/
    """

    return QLayer(collection, public).as_text()


def vsify(tile, asset, public):
    if public:
        if "s3" in tile.gdal_prefix:
            bucket, key = tile.asset_paths[asset].split("/", 1)
            return f"/vsicurl/https://{bucket}.s3.amazonaws.com/{key}"
        else:
            raise ValueError("Public files in Azure and Google Cloud not supported yet")
    else:
        return f"{tile.gdal_prefix}{tile.asset_paths[asset]}"


class ItemLayer:
    def __init__(self, tile, uuid, public=False):
        self.tile = tile
        self.name = f"{self.tile.acq_id} STAC Item"
        self.uuid = uuid
        self.proj = Proj(tile.cell.proj)
        self.public = public

    def as_treelayer(self):

        # source="{self.tile.gdal_prefix}{self.tile.asset_paths['item']}|layername={self.tile.acq_id}">
        return f"""<layer-tree-layer checked="Qt::Checked" 
            id="{self.tile.acq_id}_json_{self.uuid}" 
            expanded="1" name="{self.name}" 
            legend_exp="" providerKey="ogr" 
            source="{vsify(self.tile, 'item', self.public)}|layername={self.tile.acq_id}">
        <customproperties/>
        </layer-tree-layer>"""

    def as_maplayer(self):
        # <datasource>{self.tile.gdal_prefix}{self.tile.asset_paths['item']}|layername={self.tile.acq_id}</datasource>

        return f"""

    <maplayer geometry="Polygon" simplifyLocal="1" autoRefreshEnabled="0" minScale="100000000" refreshOnNotifyEnabled="0" simplifyDrawingTol="1" refreshOnNotifyMessage="" maxScale="0" type="vector" hasScaleBasedVisibilityFlag="0" simplifyDrawingHints="1" readOnly="0" simplifyAlgorithm="0" styleCategories="AllStyleCategories" simplifyMaxScale="1" autoRefreshTime="0" labelsEnabled="0" wkbType="Polygon">
      <id>{self.tile.acq_id}_json_{self.uuid}</id>
      <datasource>{vsify(self.tile, 'item', self.public)}|layername={self.tile.acq_id}</datasource>
      <keywordList>
        <value></value>
      </keywordList>
      <layername>{self.name}</layername>
       <srs>
        <spatialrefsys>
          <wkt>GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]</wkt>
          <proj4>+proj=longlat +datum=WGS84 +no_defs</proj4>
          <srsid>3452</srsid>
          <srid>4326</srid>
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
          <projectionacronym>longlat</projectionacronym>
          <ellipsoidacronym>WGS84</ellipsoidacronym>
          <geographicflag>true</geographicflag>
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <legend type="default-vector"/>
      <map-layer-style-manager current="default">
        <map-layer-style name="default"/>
      </map-layer-style-manager>
      <flags>
        <Identifiable>1</Identifiable>
        <Removable>1</Removable>
        <Searchable>1</Searchable>
      </flags>
      <renderer-v2 forceraster="0" symbollevels="0" enableorderby="0" type="singleSymbol">
        <symbols>
          <symbol name="0" alpha="1" force_rhr="0" clip_to_extent="1" type="fill">
            <layer enabled="1" class="SimpleFill" pass="0" locked="0">
              <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
              <prop v="164,113,88,255" k="color"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="35,35,35,255" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0.26" k="outline_width"/>
              <prop v="MM" k="outline_width_unit"/>
              <prop v="no" k="style"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option name="name" type="QString" value=""/>
                  <Option name="properties"/>
                  <Option name="type" type="QString" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </symbols>
        <rotation/>
        <sizescale/>
      </renderer-v2>
      <labeling type="simple">
        <settings calloutType="simple">
          <text-style fontSize="10" textOrientation="horizontal" fontKerning="1" isExpression="1" useSubstitutions="0" previewBkgrdColor="255,255,255,255" fontLetterSpacing="0" textOpacity="1" multilineHeight="1" fontFamily=".SF NS Text" fontStrikeout="0" fontCapitals="0" fontWeight="50" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSizeUnit="Point" fieldName="&quot;catalog_id&quot;  +  '\n'  + &#xa; format_date( &quot;datetime&quot;, 'yyyy-MM-dd' ) +  '\n'  + &#xa; &quot;quadkey&quot;  +  '\n'  + &#xa; 'Platform: '  +  &quot;platform&quot;  +  '\n'  + &#xa; 'GSD: '  +  to_string(&quot;gsd_avg&quot;)  +  '\n'    + &#xa; 'Clouds: ' +  to_string(&quot;tile:clouds_percent&quot;)&#xa; " fontWordSpacing="0" namedStyle="Regular" textColor="0,0,0,255" fontItalic="0" fontUnderline="0" blendMode="0">
            <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferJoinStyle="128" bufferSizeUnits="MM" bufferOpacity="1" bufferBlendMode="0" bufferNoFill="1" bufferSize="0.9" bufferDraw="1" bufferColor="255,255,255,255"/>
            <text-mask maskOpacity="1" maskEnabled="0" maskSizeUnits="MM" maskJoinStyle="128" maskedSymbolLayers="" maskType="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSize="1.5"/>
            <background shapeRotationType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="MM" shapeRadiiUnit="MM" shapeSVGFile="" shapeOpacity="1" shapeSizeType="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeRotation="0" shapeBorderWidth="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetY="0" shapeFillColor="255,255,255,255" shapeRadiiX="0" shapeOffsetX="0" shapeBlendMode="0" shapeBorderColor="128,128,128,255" shapeType="0" shapeSizeY="0.7" shapeBorderWidthUnit="MM" shapeOffsetUnit="MM" shapeRadiiY="0" shapeDraw="1" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0.7">
              <symbol name="markerSymbol" alpha="1" force_rhr="0" clip_to_extent="1" type="marker">
                <layer enabled="1" class="SimpleMarker" pass="0" locked="0">
                  <prop v="0" k="angle"/>
                  <prop v="114,155,111,255" k="color"/>
                  <prop v="1" k="horizontal_anchor_point"/>
                  <prop v="bevel" k="joinstyle"/>
                  <prop v="circle" k="name"/>
                  <prop v="0,0" k="offset"/>
                  <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
                  <prop v="MM" k="offset_unit"/>
                  <prop v="35,35,35,255" k="outline_color"/>
                  <prop v="solid" k="outline_style"/>
                  <prop v="0" k="outline_width"/>
                  <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
                  <prop v="MM" k="outline_width_unit"/>
                  <prop v="diameter" k="scale_method"/>
                  <prop v="2" k="size"/>
                  <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
                  <prop v="MM" k="size_unit"/>
                  <prop v="1" k="vertical_anchor_point"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option name="name" type="QString" value=""/>
                      <Option name="properties"/>
                      <Option name="type" type="QString" value="collection"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowOffsetAngle="135" shadowDraw="1" shadowRadius="1.5" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowUnder="0" shadowColor="0,0,0,255" shadowOffsetUnit="MM" shadowRadiusAlphaOnly="0" shadowScale="100" shadowOffsetDist="1.2" shadowOffsetGlobal="1" shadowRadiusUnit="MM" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowBlendMode="6"/>
            <dd_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format useMaxLineLengthForAutoWrap="1" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" plussign="0" rightDirectionSymbol=">" decimals="3" wrapChar="" addDirectionSymbol="0" autoWrapLength="0" multilineAlign="0" placeDirectionSymbol="0" formatNumbers="0"/>
          <placement centroidInside="1" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" overrunDistance="0" preserveRotation="1" dist="0" geometryGenerator="" maxCurvedCharAngleIn="25" repeatDistance="0" geometryGeneratorType="PointGeometry" offsetUnits="MM" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" xOffset="0" priority="5" geometryGeneratorEnabled="0" offsetType="0" maxCurvedCharAngleOut="-25" yOffset="0" repeatDistanceUnits="MM" overrunDistanceUnit="MM" quadOffset="4" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distMapUnitScale="3x:0,0,0,0,0,0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" placementFlags="10" distUnits="MM" fitInPolygonOnly="1" layerType="PolygonGeometry" rotationAngle="0" placement="0"/>
          <rendering obstacle="1" upsidedownLabels="0" limitNumLabels="0" obstacleType="1" displayAll="0" maxNumLabels="2000" drawLabels="1" fontMinPixelSize="3" fontMaxPixelSize="10000" obstacleFactor="1" mergeLines="0" scaleMin="0" scaleVisibility="0" labelPerPart="0" minFeatureSize="0" scaleMax="0" fontLimitPixelSize="0" zIndex="0"/>
          <dd_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option name="anchorPoint" type="QString" value="pole_of_inaccessibility"/>
              <Option name="ddProperties" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="drawToAllParts" type="bool" value="false"/>
              <Option name="enabled" type="QString" value="0"/>
              <Option name="lineSymbol" type="QString" value="&lt;symbol name=&quot;symbol&quot; alpha=&quot;1&quot; force_rhr=&quot;0&quot; clip_to_extent=&quot;1&quot; type=&quot;line&quot;>&lt;layer enabled=&quot;1&quot; class=&quot;SimpleLine&quot; pass=&quot;0&quot; locked=&quot;0&quot;>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option name=&quot;name&quot; type=&quot;QString&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option name=&quot;type&quot; type=&quot;QString&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
              <Option name="minLength" type="double" value="0"/>
              <Option name="minLengthMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="minLengthUnit" type="QString" value="MM"/>
              <Option name="offsetFromAnchor" type="double" value="0"/>
              <Option name="offsetFromAnchorMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromAnchorUnit" type="QString" value="MM"/>
              <Option name="offsetFromLabel" type="double" value="0"/>
              <Option name="offsetFromLabelMapUnitScale" type="QString" value="3x:0,0,0,0,0,0"/>
              <Option name="offsetFromLabelUnit" type="QString" value="MM"/>
            </Option>
          </callout>
        </settings>
      </labeling>
      <blendMode>0</blendMode>
      <featureBlendMode>0</featureBlendMode>
      <layerOpacity>1</layerOpacity>
      <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
        <DiagramCategory showAxis="1" sizeType="MM" lineSizeScale="3x:0,0,0,0,0,0" labelPlacementMethod="XHeight" penColor="#000000" spacing="5" width="15" rotationOffset="270" maxScaleDenominator="1e+08" scaleDependency="Area" penWidth="0" lineSizeType="MM" minimumSize="0" barWidth="5" backgroundAlpha="255" direction="0" sizeScale="3x:0,0,0,0,0,0" penAlpha="255" minScaleDenominator="0" backgroundColor="#ffffff" enabled="0" spacingUnit="MM" spacingUnitScale="3x:0,0,0,0,0,0" opacity="1" height="15" diagramOrientation="Up" scaleBasedVisibility="0">
          <fontProperties description=".SF NS Text,13,-1,5,50,0,0,0,0,0" style=""/>
          <axisSymbol>
            <symbol name="" alpha="1" force_rhr="0" clip_to_extent="1" type="line">
              <layer enabled="1" class="SimpleLine" pass="0" locked="0">
                <prop v="square" k="capstyle"/>
                <prop v="5;2" k="customdash"/>
                <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
                <prop v="MM" k="customdash_unit"/>
                <prop v="0" k="draw_inside_polygon"/>
                <prop v="bevel" k="joinstyle"/>
                <prop v="35,35,35,255" k="line_color"/>
                <prop v="solid" k="line_style"/>
                <prop v="0.26" k="line_width"/>
                <prop v="MM" k="line_width_unit"/>
                <prop v="0" k="offset"/>
                <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
                <prop v="MM" k="offset_unit"/>
                <prop v="0" k="ring_filter"/>
                <prop v="0" k="use_custom_dash"/>
                <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
                <data_defined_properties>
                  <Option type="Map">
                    <Option name="name" type="QString" value=""/>
                    <Option name="properties"/>
                    <Option name="type" type="QString" value="collection"/>
                  </Option>
                </data_defined_properties>
              </layer>
            </symbol>
          </axisSymbol>
        </DiagramCategory>
      </SingleCategoryDiagramRenderer>
      <blendMode>0</blendMode>
      <featureBlendMode>0</featureBlendMode>
      <layerOpacity>1</layerOpacity>
      <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
        <activeChecks type="StringList">
          <Option type="QString" value=""/>
        </activeChecks>
        <checkConfiguration/>
      </geometryOptions>
      <attributeactions>
        <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
      </attributeactions>
    </maplayer> """


class VisualDataLayer:
    def __init__(self, tile, uuid, public):
        self.tile = tile
        self.name = f"{self.tile.acq_id} Visual Image"
        self.uuid = uuid
        self.proj = Proj(tile.cell.proj)
        self.public = public
        self.pan = tile.properties["platform"] == "WV01"

    def as_treelayer(self):

        return f"""<layer-tree-layer checked="Qt::Checked" 
            id="{self.tile.acq_id}_visual_tif_{self.uuid}" 
            expanded="1" name="{self.name}" 
            legend_exp="" providerKey="gdal" 
            source="{vsify(self.tile, 'visual', self.public)}">
        <customproperties/>
        </layer-tree-layer>"""

    def as_maplayer(self):

        if self.pan:
            nodata = """<noData>
        <noDataList bandNo="1" useSrcNoData="0"/>
        <noDataList bandNo="2" useSrcNoData="0"/>
      </noData>"""

            renderer = """
           <rasterrenderer opacity="1" type="singlebandgray" grayBand="1" nodataColor="" alphaBand="-1" gradient="BlackToWhite">
          <rasterTransparency/>
          <minMaxOrigin>
            <limits>MinMax</limits>
            <extent>WholeRaster</extent>
            <statAccuracy>Estimated</statAccuracy>
            <cumulativeCutLower>0.02</cumulativeCutLower>
            <cumulativeCutUpper>0.98</cumulativeCutUpper>
            <stdDevFactor>2</stdDevFactor>
          </minMaxOrigin>
          <contrastEnhancement>
            <minValue>6</minValue>
            <maxValue>255</maxValue>
            <algorithm>StretchToMinimumMaximum</algorithm>
          </contrastEnhancement>
        </rasterrenderer> 
            
            """
        else:
            nodata = """<noData>
        <noDataList bandNo="1" useSrcNoData="0"/>
        <noDataList bandNo="2" useSrcNoData="0"/>
        <noDataList bandNo="3" useSrcNoData="0"/>
        <noDataList bandNo="4" useSrcNoData="0"/>
      </noData>"""

            renderer = """
            <rasterrenderer type="multibandcolor" alphaBand="4" opacity="1" redBand="1" blueBand="3" nodataColor="" greenBand="2">
          <rasterTransparency/>
          <minMaxOrigin>
            <limits>MinMax</limits>
            <extent>WholeRaster</extent>
            <statAccuracy>Estimated</statAccuracy>
            <cumulativeCutLower>0.02</cumulativeCutLower>
            <cumulativeCutUpper>0.98</cumulativeCutUpper>
            <stdDevFactor>2</stdDevFactor>
          </minMaxOrigin>
          <redContrastEnhancement>
            <minValue>0</minValue>
            <maxValue>255</maxValue>
            <algorithm>NoEnhancement</algorithm>
          </redContrastEnhancement>
          <greenContrastEnhancement>
            <minValue>0</minValue>
            <maxValue>255</maxValue>
            <algorithm>NoEnhancement</algorithm>
          </greenContrastEnhancement>
          <blueContrastEnhancement>
            <minValue>0</minValue>
            <maxValue>255</maxValue>
            <algorithm>NoEnhancement</algorithm>
          </blueContrastEnhancement>
        </rasterrenderer> 
            """

        return f"""
        <maplayer labelsEnabled="1" maxScale="0" autoRefreshTime="0" type="raster" hasScaleBasedVisibilityFlag="0" autoRefreshEnabled="0" styleCategories="AllStyleCategories" minScale="1e+08" refreshOnNotifyEnabled="0" refreshOnNotifyMessage="">
      <extent>
        <xmin>{self.tile.cell.bounds[0] - 0.30517578125 * 256} </xmin>
        <ymin>{self.tile.cell.bounds[1] - 0.30517578125 * 256}</ymin>
        <xmax>{self.tile.cell.bounds[2] + 0.30517578125 * 256}</xmax>
        <ymax>{self.tile.cell.bounds[3] + 0.30517578125 * 256 }</ymax>
      </extent>
      <id>{self.tile.acq_id}_visual_tif_{self.uuid}</id>
      <datasource>{vsify(self.tile, 'visual', self.public)}</datasource>
      <keywordList>
        <value></value>
      </keywordList>
      <layername>{self.name}</layername>
      <srs>
        <spatialrefsys>
          <wkt>{self.proj.crs.to_wkt()}</wkt>
          <proj4>{self.proj.srs}</proj4>
          <srsid>3094</srsid>
          <srid>{self.proj.crs.to_epsg()}</srid>
          <authid>{self.proj.crs.to_string()}</authid>
          <description>{self.proj.crs.name}</description>
          <projectionacronym>utm</projectionacronym>
          <ellipsoidacronym>WGS84</ellipsoidacronym>
          <geographicflag>false</geographicflag>
        </spatialrefsys>
      </srs>
      <resourceMetadata>
        <identifier></identifier>
        <parentidentifier></parentidentifier>
        <language></language>
        <type></type>
        <title></title>
        <abstract></abstract>
        <links/>
        <fees></fees>
        <encoding></encoding>
        <crs>
          <spatialrefsys>
            <wkt>{self.proj.crs.to_wkt()}</wkt>
            <proj4>{self.proj.srs}</proj4>
            <srsid>3094</srsid>
            <srid>{self.proj.crs.to_epsg()}</srid>
            <authid>{self.proj.crs.to_string()}</authid>
            <description>{self.proj.crs.name}</description>
            <projectionacronym>utm</projectionacronym>
            <ellipsoidacronym>WGS84</ellipsoidacronym>
            <geographicflag>false</geographicflag>
            </spatialrefsys>
        </crs>
        <extent/>
      </resourceMetadata>
      <provider>gdal</provider>
     {nodata} 
      <map-layer-style-manager current="default">
        <map-layer-style name="default"/>
      </map-layer-style-manager>
      <flags>
        <Identifiable>1</Identifiable>
        <Removable>1</Removable>
        <Searchable>1</Searchable>
      </flags>
      <customproperties>
        <property key="identify/format" value="Value"/>
      </customproperties>
      <pipe>
        {renderer} 
        <brightnesscontrast brightness="0" contrast="0"/>
        <huesaturation colorizeOn="0" colorizeGreen="128" saturation="0" grayscaleMode="0" colorizeRed="255" colorizeStrength="100" colorizeBlue="128"/>
        <rasterresampler maxOversampling="2"/>
      </pipe>
      <blendMode>0</blendMode>
    </maplayer>"""


##############


class EmptyMask(Exception):
    pass


class MaskDataLayer:
    def __init__(self, tile, asset, color, uuid, public):
        # asset = 'cloud-mask' i.e. asset key
        self.tile = tile
        self.asset = asset
        # color is r,g,b,a, clouds is 229,182,54,255
        self.color = color
        title = asset.replace("-", " ").title().replace("Ms ", "MS ")
        self.name = f"{self.tile.acq_id} {title}"
        self.uuid = uuid
        self.proj = Proj(tile.cell.proj)
        self.public = public
        asset = tile.asset_paths[asset]
        # cloud layer names got changed, have to look it up for now
        with fiona.open(f"{tile.gdal_prefix}{asset}") as layer:
            self.layername = layer.name
            features = list(layer)
            if len(features) == 0:
                raise EmptyMask
            if len(features) == 1:
                if len(features[0]["geometry"]["coordinates"]) == 0:
                    raise EmptyMask

    def as_treelayer(self):

        return f"""<layer-tree-layer checked="Qt::Checked" 
            id="{self.layername}_{self.uuid}" 
            expanded="1" name="{self.name}" 
            legend_exp="" providerKey="ogr" 
            source="{vsify(self.tile, self.asset, self.public)}|layername={self.layername}">
        <customproperties/>
        </layer-tree-layer>"""

    def as_maplayer(self):
        return f"""<maplayer refreshOnNotifyEnabled="0" simplifyAlgorithm="0" simplifyMaxScale="1" autoRefreshTime="0" minScale="100000000" wkbType="MultiPolygon" simplifyDrawingHints="1" readOnly="0" maxScale="0" refreshOnNotifyMessage="" styleCategories="AllStyleCategories" simplifyDrawingTol="1" labelsEnabled="0" type="vector" simplifyLocal="1" hasScaleBasedVisibilityFlag="0" autoRefreshEnabled="0" geometry="Polygon">
      <id>{self.layername}_{self.uuid}</id>
      <datasource>{vsify(self.tile, self.asset, self.public)}|layername={self.layername}</datasource>
      <layername>{self.name}</layername>
      <srs>
        <spatialrefsys>
          <wkt>{self.proj.crs.to_wkt()}</wkt>
          <proj4>{self.proj.srs}</proj4>
          <srsid>3094</srsid>
          <srid>{self.proj.crs.to_epsg()}</srid>
          <authid>{self.proj.crs.to_string()}</authid>
          <description>{self.proj.crs.name}</description>
          <projectionacronym>utm</projectionacronym>
          <ellipsoidacronym>WGS84</ellipsoidacronym>
          <geographicflag>false</geographicflag> 
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <legend type="default-vector"/>
      <map-layer-style-manager current="default">
        <map-layer-style name="default"/>
      </map-layer-style-manager>
      <flags>
        <Identifiable>1</Identifiable>
        <Removable>1</Removable>
        <Searchable>1</Searchable>
      </flags>
      <renderer-v2 type="singleSymbol" enableorderby="0" forceraster="0" symbollevels="0">
        <symbols>
          <symbol type="fill" alpha="1" clip_to_extent="1" force_rhr="0" name="0">
            <layer locked="0" enabled="1" pass="0" class="SimpleFill">
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="{self.color}"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </symbols>
      </renderer-v2>
      <blendMode>0</blendMode>
      <featureBlendMode>0</featureBlendMode>
      <layerOpacity>1</layerOpacity>
      <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
        <activeChecks type="StringList">
          <Option type="QString" value=""/>
        </activeChecks>
        <checkConfiguration/>
      </geometryOptions>
      <attributeactions>
        <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
      </attributeactions>
    </maplayer> """


class TreeLayer:
    def __init__(self, layers):
        self.layers = layers

    def as_text(self):

        layers = "\n".join(layer.as_treelayer() for layer in self.layers)
        return f"""
            <layer-tree-group checked="Qt::Checked" expanded="1" name="{self.layers[0].tile.cell.id}">
                {layers}
            </layer-tree-group> """


class MapLayer:
    def __init__(self, layers):
        self.layers = layers

    def as_text(self):
        return "\n".join(layer.as_maplayer() for layer in self.layers)


class QLayer:
    def __init__(self, collection, public=False):
        if not HAS_FIONA:
            raise MissingDependency("QLR export requires Fiona")
        self.treelayers = defaultdict(list)
        self.maplayers = []
        self.zone_ids = [(z, uuid4().hex) for z in collection.zones]
        for acq in collection.acquisitions:
            for tile in acq:
                uuid = uuid4().hex
                item = ItemLayer(tile, uuid, public)
                layers = [item]
                try:
                    layers.append(
                        MaskDataLayer(tile, "cloud-mask", "229,182,54,255", uuid, public)
                    )
                except EmptyMask:
                    pass

                # V3 ARD
                if "water-mask" in tile.asset_paths:
                    v3layers = (
                        ("cloud-shadow-mask", "220,67,0,255"),
                        ("water-mask", "0,204,204,128"),
                        ("terrain-shadow-mask", "255,51,51,255"),
                        ("ms-saturation-mask", "255,153,153,255"),
                    )
                    for asset, color in v3layers:
                        try:
                            layers.append(MaskDataLayer(tile, asset, color, uuid, public))
                        except EmptyMask:
                            pass

                visual = VisualDataLayer(tile, uuid, public)
                layers.append(visual)
                self.treelayers[acq].append(TreeLayer(layers))
                self.maplayers.append(MapLayer(layers))

    def render_tree(self):
        text = ""
        for acq, layers in sorted(
            self.treelayers.items(), key=lambda kv: kv[0].properties["datetime"], reverse=True
        ):
            text += f'<layer-tree-group checked="Qt::Unchecked" expanded="0" name="{acq.date}: {acq.acq_id}">'
            text += "<customproperties/>"
            text += "\n".join(t.as_text() for t in layers)
            text += " </layer-tree-group>"
        return text

    def render_layers(self):
        return "\n".join([l.as_text() for l in self.maplayers])

    def render_zones_tree(self):
        text = f'<layer-tree-group checked="Qt::Unchecked" expanded="0" name="ARD Grids">'
        text += "<customproperties/>"
        for zone, uuid in self.zone_ids:
            text += f"""
            <layer-tree-layer legend_exp="" source="/vsicurl/https://ard-docs.s3.amazonaws.com/main/canvas-grids/Z{zone}.gpkg|layername=Z{zone}" providerKey="ogr" expanded="1" name="ARD Grid Zone {zone}" checked="Qt::Unchecked" id="Z{zone}_{uuid}">
            <customproperties/>
            </layer-tree-layer>
            """
        text += " </layer-tree-group>"
        return text

    def render_zones_layers(self):
        text = ""
        for zone, uuid in self.zone_ids:
            proj = Proj(f"EPSG:326{zone:02}")
            text += f"""
            <maplayer simplifyDrawingHints="1" refreshOnNotifyMessage="" simplifyLocal="1" autoRefreshTime="0" simplifyDrawingTol="1" readOnly="0" type="vector" simplifyAlgorithm="0" styleCategories="AllStyleCategories" maxScale="0" minScale="100000000" simplifyMaxScale="1" labelsEnabled="1" wkbType="Polygon" geometry="Polygon" refreshOnNotifyEnabled="0" hasScaleBasedVisibilityFlag="0" autoRefreshEnabled="0">
      <extent>
        <xmin>165000</xmin>
        <ymin>-9330000</ymin>
        <xmax>835000</xmax>
        <ymax>9330000</ymax>
      </extent>
      <id>Z{zone}_{uuid}</id>
      <datasource>/vsicurl/https://ard-docs.s3.amazonaws.com/main/canvas-grids/Z{zone}.gpkg|layername=Z{zone}</datasource>
      <keywordList>
        <value></value>
      </keywordList>
      <layername>ARD Grid Zone {zone}</layername>
      <srs>
       <spatialrefsys>
          <wkt>{proj.crs.to_wkt()}</wkt>
          <proj4>{proj.srs}</proj4>
          <srsid>3094</srsid>
          <srid>{proj.crs.to_epsg()}</srid>
          <authid>{proj.crs.to_string()}</authid>
          <description>{proj.crs.name}</description>
          <projectionacronym>utm</projectionacronym>
          <ellipsoidacronym>WGS84</ellipsoidacronym>
          <geographicflag>false</geographicflag> 
        </spatialrefsys> 
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <legend type="default-vector"/>
      <map-layer-style-manager current="default">
        <map-layer-style name="default"/>
      </map-layer-style-manager>
      <flags>
        <Identifiable>1</Identifiable>
        <Removable>1</Removable>
        <Searchable>1</Searchable>
      </flags>
      <renderer-v2 type="singleSymbol" forceraster="0" symbollevels="0" enableorderby="0">
        <symbols>
          <symbol type="fill" force_rhr="0" alpha="1" name="0" clip_to_extent="1">
            <layer pass="0" class="SimpleFill" enabled="1" locked="0">
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="0,0,255,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="227,69,72,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.66"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="no"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" value="" name="name"/>
                  <Option name="properties"/>
                  <Option type="QString" value="collection" name="type"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </symbols>
        <rotation/>
        <sizescale/>
      </renderer-v2>
      <labeling type="simple">
        <settings calloutType="simple">
          <text-style fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontLetterSpacing="0" useSubstitutions="0" textOrientation="horizontal" fontCapitals="0" fontFamily=".SF NS Text" fontKerning="1" blendMode="0" fontStrikeout="0" previewBkgrdColor="255,255,255,255" fontSize="10" fontItalic="0" multilineHeight="1" fieldName="utmzone + '-' + quadkey" fontWeight="50" fontUnderline="0" textOpacity="1" namedStyle="Regular" isExpression="1" fontSizeUnit="Point" textColor="0,0,0,255" fontWordSpacing="0">
            <text-buffer bufferDraw="1" bufferNoFill="0" bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferBlendMode="0" bufferOpacity="1" bufferColor="255,255,255,255" bufferSize="1" bufferSizeUnits="MM"/>
            <text-mask maskOpacity="1" maskEnabled="0" maskJoinStyle="128" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSize="1.5" maskType="0" maskSizeUnits="MM" maskedSymbolLayers=""/>
            <background shapeDraw="0" shapeSizeX="0" shapeOpacity="1" shapeOffsetUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeOffsetY="0" shapeOffsetX="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeRadiiUnit="MM" shapeFillColor="255,255,255,255" shapeBorderWidth="0" shapeJoinStyle="64" shapeBlendMode="0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSizeType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderColor="128,128,128,255" shapeSVGFile="" shapeSizeUnit="MM" shapeRotation="0" shapeType="0" shapeSizeY="0" shapeRotationType="0" shapeBorderWidthUnit="MM" shapeRadiiY="0">
              <symbol type="marker" force_rhr="0" alpha="1" name="markerSymbol" clip_to_extent="1">
                <layer pass="0" class="SimpleMarker" enabled="1" locked="0">
                  <prop k="angle" v="0"/>
                  <prop k="color" v="196,60,57,255"/>
                  <prop k="horizontal_anchor_point" v="1"/>
                  <prop k="joinstyle" v="bevel"/>
                  <prop k="name" v="circle"/>
                  <prop k="offset" v="0,0"/>
                  <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="outline_color" v="35,35,35,255"/>
                  <prop k="outline_style" v="solid"/>
                  <prop k="outline_width" v="0"/>
                  <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="outline_width_unit" v="MM"/>
                  <prop k="scale_method" v="diameter"/>
                  <prop k="size" v="2"/>
                  <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="size_unit" v="MM"/>
                  <prop k="vertical_anchor_point" v="1"/>
                  <data_defined_properties>
                    <Option type="Map">
                      <Option type="QString" value="" name="name"/>
                      <Option name="properties"/>
                      <Option type="QString" value="collection" name="type"/>
                    </Option>
                  </data_defined_properties>
                </layer>
              </symbol>
            </background>
            <shadow shadowRadius="1.5" shadowUnder="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowColor="0,0,0,255" shadowDraw="0" shadowOffsetAngle="135" shadowOffsetDist="1" shadowScale="100" shadowBlendMode="6" shadowRadiusAlphaOnly="0" shadowOffsetGlobal="1" shadowRadiusUnit="MM" shadowOpacity="0.7" shadowOffsetUnit="MM" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0"/>
            <dd_properties>
              <Option type="Map">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </dd_properties>
            <substitutions/>
          </text-style>
          <text-format multilineAlign="0" addDirectionSymbol="0" reverseDirectionSymbol="0" autoWrapLength="0" formatNumbers="0" plussign="0" wrapChar="" rightDirectionSymbol=">" decimals="3" leftDirectionSymbol="&lt;" placeDirectionSymbol="0" useMaxLineLengthForAutoWrap="1"/>
          <placement fitInPolygonOnly="0" distMapUnitScale="3x:0,0,0,0,0,0" rotationAngle="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleIn="25" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" distUnits="MM" placement="0" placementFlags="10" geometryGeneratorEnabled="0" preserveRotation="1" geometryGenerator="" quadOffset="0" offsetUnits="MM" priority="5" geometryGeneratorType="PointGeometry" offsetType="0" centroidWhole="1" repeatDistance="0" dist="0" xOffset="0" yOffset="0" centroidInside="0" repeatDistanceUnits="MM" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" maxCurvedCharAngleOut="-25" layerType="PolygonGeometry" overrunDistance="0" overrunDistanceUnit="MM" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0"/>
          <rendering fontMinPixelSize="3" minFeatureSize="0" drawLabels="1" displayAll="0" scaleVisibility="1" maxNumLabels="2000" mergeLines="0" obstacleFactor="1" obstacleType="1" labelPerPart="0" scaleMin="0" upsidedownLabels="0" obstacle="1" zIndex="0" scaleMax="134345" fontMaxPixelSize="10000" fontLimitPixelSize="0" limitNumLabels="0"/>
          <dd_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </dd_properties>
          <callout type="simple">
            <Option type="Map">
              <Option type="QString" value="pole_of_inaccessibility" name="anchorPoint"/>
              <Option type="Map" name="ddProperties">
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
              <Option type="bool" value="false" name="drawToAllParts"/>
              <Option type="QString" value="0" name="enabled"/>
              <Option type="QString" value="&lt;symbol type=&quot;line&quot; force_rhr=&quot;0&quot; alpha=&quot;1&quot; name=&quot;symbol&quot; clip_to_extent=&quot;1&quot;>&lt;layer pass=&quot;0&quot; class=&quot;SimpleLine&quot; enabled=&quot;1&quot; locked=&quot;0&quot;>&lt;prop k=&quot;capstyle&quot; v=&quot;square&quot;/>&lt;prop k=&quot;customdash&quot; v=&quot;5;2&quot;/>&lt;prop k=&quot;customdash_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;customdash_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;draw_inside_polygon&quot; v=&quot;0&quot;/>&lt;prop k=&quot;joinstyle&quot; v=&quot;bevel&quot;/>&lt;prop k=&quot;line_color&quot; v=&quot;60,60,60,255&quot;/>&lt;prop k=&quot;line_style&quot; v=&quot;solid&quot;/>&lt;prop k=&quot;line_width&quot; v=&quot;0.3&quot;/>&lt;prop k=&quot;line_width_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;ring_filter&quot; v=&quot;0&quot;/>&lt;prop k=&quot;use_custom_dash&quot; v=&quot;0&quot;/>&lt;prop k=&quot;width_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; value=&quot;&quot; name=&quot;name&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; value=&quot;collection&quot; name=&quot;type&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol"/>
              <Option type="double" value="0" name="minLength"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale"/>
              <Option type="QString" value="MM" name="minLengthUnit"/>
              <Option type="double" value="0" name="offsetFromAnchor"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale"/>
              <Option type="QString" value="MM" name="offsetFromAnchorUnit"/>
              <Option type="double" value="0" name="offsetFromLabel"/>
              <Option type="QString" value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale"/>
              <Option type="QString" value="MM" name="offsetFromLabelUnit"/>
            </Option>
          </callout>
        </settings>
      </labeling>
      <customproperties>
        <property value="0" key="embeddedWidgets/count"/>
        <property key="variableNames"/>
        <property key="variableValues"/>
      </customproperties>
      <blendMode>0</blendMode>
      <featureBlendMode>0</featureBlendMode>
      <layerOpacity>1</layerOpacity>
      <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
        <DiagramCategory sizeType="MM" backgroundAlpha="255" penColor="#000000" sizeScale="3x:0,0,0,0,0,0" penWidth="0" spacingUnit="MM" showAxis="1" width="15" rotationOffset="270" spacingUnitScale="3x:0,0,0,0,0,0" enabled="0" opacity="1" diagramOrientation="Up" barWidth="5" maxScaleDenominator="1e+08" labelPlacementMethod="XHeight" lineSizeType="MM" minimumSize="0" spacing="5" scaleBasedVisibility="0" direction="0" minScaleDenominator="0" penAlpha="255" lineSizeScale="3x:0,0,0,0,0,0" scaleDependency="Area" backgroundColor="#ffffff" height="15">
          <fontProperties description=".SF NS Text,13,-1,5,50,0,0,0,0,0" style=""/>
          <axisSymbol>
            <symbol type="line" force_rhr="0" alpha="1" name="" clip_to_extent="1">
              <layer pass="0" class="SimpleLine" enabled="1" locked="0">
                <prop k="capstyle" v="square"/>
                <prop k="customdash" v="5;2"/>
                <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                <prop k="customdash_unit" v="MM"/>
                <prop k="draw_inside_polygon" v="0"/>
                <prop k="joinstyle" v="bevel"/>
                <prop k="line_color" v="35,35,35,255"/>
                <prop k="line_style" v="solid"/>
                <prop k="line_width" v="0.26"/>
                <prop k="line_width_unit" v="MM"/>
                <prop k="offset" v="0"/>
                <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                <prop k="offset_unit" v="MM"/>
                <prop k="ring_filter" v="0"/>
                <prop k="use_custom_dash" v="0"/>
                <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
                <data_defined_properties>
                  <Option type="Map">
                    <Option type="QString" value="" name="name"/>
                    <Option name="properties"/>
                    <Option type="QString" value="collection" name="type"/>
                  </Option>
                </data_defined_properties>
              </layer>
            </symbol>
          </axisSymbol>
        </DiagramCategory>
      </SingleCategoryDiagramRenderer>
      <DiagramLayerSettings linePlacementFlags="18" zIndex="0" dist="0" placement="1" priority="0" showAll="1" obstacle="0">
        <properties>
          <Option type="Map">
            <Option type="QString" value="" name="name"/>
            <Option name="properties"/>
            <Option type="QString" value="collection" name="type"/>
          </Option>
        </properties>
      </DiagramLayerSettings>
      <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
        <activeChecks/>
        <checkConfiguration type="Map">
          <Option type="Map" name="QgsGeometryGapCheck">
            <Option type="double" value="0" name="allowedGapsBuffer"/>
            <Option type="bool" value="false" name="allowedGapsEnabled"/>
            <Option type="QString" value="" name="allowedGapsLayer"/>
          </Option>
        </checkConfiguration>
      </geometryOptions>
     
      <attributeactions>
        <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
      </attributeactions>
    </maplayer>"""

        return text

    def as_text(self):
        return f"""<!DOCTYPE qgis-layer-definition>
        <qlr>
           <layer-tree-group checked="Qt::Checked" expanded="1" name="">
            <customproperties/>
            {self.render_zones_tree()}
            {self.render_tree()}
            </layer-tree-group> 
            <maplayers>
            {self.render_zones_layers()}
            {self.render_layers()}
            </maplayers>
        </qlr> """
