#include <types.hpp>
#include <python_geo_query.hpp>

namespace boost_geo_query
{

    PythonGeoQuery::PythonGeoQuery(const LocationArray &xy, const IndexArray &rowPtr, const std::string &type)
    {
        if (type == accepted_input_types::point)
        {
            _query = std::make_unique<BoostGeoQueryWrapper<Point>>(xy, rowPtr);
        }
        else if (type == accepted_input_types::linestring)
        {
            _query = std::make_unique<BoostGeoQueryWrapper<LineString>>(xy, rowPtr);
        }
        else if (type == accepted_input_types::openPolygon)
        {
            _query = std::make_unique<BoostGeoQueryWrapper<OpenPolygon>>(xy, rowPtr);
        }
        else if (type == accepted_input_types::closedPolygon)
        {
            _query = std::make_unique<BoostGeoQueryWrapper<ClosedPolygon>>(xy, rowPtr);
        }
        else
        {
            throw std::invalid_argument("Input type: " + type + " unknown. Choose from " + accepted_input_types::point + ", " + accepted_input_types::linestring + ", " + accepted_input_types::openPolygon + " and " + accepted_input_types::closedPolygon + ".");
        }
    }

}