#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <memory>

namespace py = pybind11;
using namespace py::literals;

using namespace pcl;


template<typename T>
pcl::shared_ptr<PointCloud<T>> fromPtsArray(py::array_t<float> &points);

template<>
pcl::shared_ptr<PointCloud<PointXYZ>> fromPtsArray<PointXYZ>(py::array_t<float> &points)
{
    auto cloud{std::make_shared<PointCloud<PointXYZ>>()};
    cloud->resize(points.shape(0));
    auto r{points.unchecked<2>()};
    PointXYZ* pt;
    for (ssize_t i = 0; i < r.shape(0); ++i)
    {
        pt = &cloud->at(i);
        pt->x = r(i, 0);
        pt->y = r(i, 1);
        pt->z = r(i, 2);
    }
    return cloud;
}


template<>
pcl::shared_ptr<PointCloud<PointXYZI>> fromPtsArray<PointXYZI>(py::array_t<float> &points)
{
    auto cloud{std::make_shared<PointCloud<PointXYZI>>()};
    cloud->resize(points.shape(0));
    auto r{points.unchecked<2>()};
    PointXYZI* pt;
    for (ssize_t i = 0; i < r.shape(0); ++i)
    {
        pt = &cloud->at(i);
        pt->x = r(i, 0);
        pt->y = r(i, 1);
        pt->z = r(i, 2);
        pt->intensity = r(i, 3);
    }
    return cloud;
}


template<typename T>
pcl::shared_ptr<PointCloud<T>> fromDimsArray(py::array_t<float>& array);

template<>
pcl::shared_ptr<PointCloud<PointXYZ>> fromDimsArray<PointXYZ>(py::array_t<float>& array)
{
    auto cloud{std::make_shared<PointCloud<PointXYZ>>()};
    cloud->resize(array.shape(1));

    auto r{array.unchecked<2>()};
    PointXYZ* pt;
    for (ssize_t i = 0; i < r.shape(1); ++i)
    {
        pt = &cloud->at(i);
        pt->x = r(0, i);
        pt->y = r(1, i);
        pt->z = r(2, i);
    }
    return cloud;
}


template<>
pcl::shared_ptr<PointCloud<PointXYZI>> fromDimsArray<PointXYZI>(py::array_t<float>& array)
{
    auto cloud{std::make_shared<PointCloud<PointXYZI>>()};
    cloud->resize(array.shape(1));

    auto r{array.unchecked<2>()};
    PointXYZI* pt;
    for (ssize_t i = 0; i < r.shape(0); ++i)
    {
        pt = &cloud->at(i);
        pt->x = r(0, i);
        pt->y = r(1, i);
        pt->z = r(2, i);
        pt->intensity = r(3, i);
    }
    return cloud;
}