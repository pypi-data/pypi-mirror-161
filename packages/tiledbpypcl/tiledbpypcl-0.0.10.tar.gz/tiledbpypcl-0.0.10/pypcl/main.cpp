#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <pcl/range_image/range_image.h>
#include <pcl/keypoints/narf_keypoint.h>
#include <pcl/features/range_image_border_extractor.h>
#include <pcl/features/narf_descriptor.h>
#include <pcl/registration/pyramid_feature_matching.h>
#include <memory>

// #include "vector_classes.hpp"   // inludes make_opaque which needs to be included at least once!
#include "point_cloud_buffers.hpp"
#include "point_types.hpp"
#include "point_cloud_from_array.hpp"
#include "make_opaque_vectors.hpp"
#include "pyramid_port.hpp"


#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)


// not sure if necessary
//PYBIND11_DECLARE_HOLDER_TYPE(T, pcl::shared_ptr<T>);



namespace py = pybind11;
//using namespace pcl;



class CloudFuncs
{
private:
    pcl::PointXYZ* pt;
    pcl::PointCloud<pcl::PointXYZ>* cloud;
public:
    CloudFuncs(float a, float b, float c, int d);

    float add_all_pts();

    bool add_array(std::vector<float> nums);

    int loadXYZCloud(std::vector<float> xs, std::vector<float> ys, std::vector<float> zs);
};

CloudFuncs::CloudFuncs(float a, float b, float c, int d)
{
    cloud = new pcl::PointCloud<pcl::PointXYZ>();
    for (int i = 0; i < d; ++i)
        cloud->push_back({a, b, c});
}

float CloudFuncs::add_all_pts()
{
    float total{0.f};
    for (const auto& pt: *cloud)
        total += (pt.x + pt.y + pt.z);
    return total;
}

bool CloudFuncs::add_array(std::vector<float> nums)
{
    if (nums.size() == 0) return false;
    for (const auto& num: nums)
        if (num != 2.0) return false;
    return true;
}


int CloudFuncs::loadXYZCloud(std::vector<float> xs, std::vector<float> ys, std::vector<float> zs)
{
    if (xs.size() != ys.size() || xs.size() != zs.size())
        return 1;
    size_t size{xs.size()};

    cloud->erase(cloud->begin(), cloud->end());
    for (size_t i = 0; i < size; ++i)
        cloud->push_back({xs[i], ys[i], zs[i]});

    pcl::PointCloud<pcl::PointWithViewpoint> far_ranges;
    Eigen::Affine3f scene_sensor_pose (Eigen::Affine3f::Identity());

    float angular_res{0.5f};
    float support_size{0.2f};
    pcl::RangeImage::CoordinateFrame coordinate_frame = pcl::RangeImage::CAMERA_FRAME;
    bool setUnseenToMaxRange{true};
    float noise_level{0.0f};
    float min_range{0.0f};
    int border_size{1};
    pcl::RangeImage::Ptr range_image_ptr(new pcl::RangeImage);
    const pcl::RangeImage* range_image_raw(range_image_ptr.get());
    pcl::RangeImage& range_image = *range_image_ptr;
    range_image.createFromPointCloud(*cloud, angular_res,
                                     pcl::deg2rad(360.0f), pcl::deg2rad(180.0f),
                                     scene_sensor_pose, coordinate_frame,
                                     noise_level, min_range, border_size);
    range_image.integrateFarRanges(far_ranges);
    if (setUnseenToMaxRange)
        range_image.setUnseenToMaxRange();

    pcl::RangeImageBorderExtractor range_image_border_extractor(range_image_raw);
    pcl::NarfKeypoint narf_Keypoint_detector(&range_image_border_extractor);
    narf_Keypoint_detector.setRangeImage(&range_image);
    narf_Keypoint_detector.getParameters().support_size = support_size;

    pcl::PointCloud<int> keypoint_indices;
    narf_Keypoint_detector.compute(keypoint_indices);

    return keypoint_indices.size();
//    return 0;
}

int add(int i, int j) {
    pcl::PointCloud<pcl::PointXYZ> cloud;
    cloud.push_back({float(i), float(j), float(j)});
    pcl::RangeImage::Ptr range_image_ptr(new pcl::RangeImage);
    return cloud[0].x + cloud[0].y + cloud[0].z;
}












template <typename T>
void definePointCloudClassFloatPts(py::module& m, char* suffix)
{
    using PointCloudT = pcl::PointCloud<T>;
    auto pc = py::class_<PointCloudT, pcl::shared_ptr<PointCloudT>>(m, suffix);
    pc.def(py::init([](py::array_t<float>& points, bool pts_array) { return fromPtsArray<T>(points); }), "points"_a, "pts_array"_a);
    pc.def(py::init([](py::array_t<float>& array) { return fromDimsArray<T>(array); }), "array"_a);
    pc.def(py::init([](){ return PointCloudT{}; }));
    pc.def("push_back", &PointCloudT::push_back, "pt"_a);
    pc.def_static("from_pts_array", &fromPtsArray<T>, "array"_a);
    pc.def_static("from_array", &fromDimsArray<T>, "array"_a);
    defineBuffers<T>(pc);
}

//template <typename T>
//void definePointCloudClassRGB(py::module& m, char* suffix)
//{
//    using PointCloudT = PointCloud<T>;
//    using Type = py::class_<PointCloudT, pcl::shared_ptr<PointCloudT>>;
//    auto pc = static_cast<Type>(m.attr(suffix));
//    pc.def(py::init([](py::array_t<float>& points, bool pts_array) { return fromPtsArray<T>(points); }), "points"_a, "pts_array"_a);
//    pc.def(py::init([](py::array_t<float>& array) { return fromDimsArray<T>(array); }), "array"_a);
//    pc.def(py::init<>());
//    pc.def_static("from_pts_array", &fromPtsArray<T>, "array"_a);
//    pc.def_static("from_array", &fromDimsArray<T>, "array"_a);
//    defineBuffers<T>(pc);
//}

//using namespace pcl;





template <typename PointT>
void defineRangeImage(py::module& m, char* suffix)
{
    using CloudT = pcl::PointCloud<PointT>;
//    typedef RangeImage::createFromPointCloud<CloudXYZ>;
    auto ri = py::class_<RangeImage, pcl::shared_ptr<RangeImage>>(m, (std::string("RangeImage") + suffix).c_str());
    ri.def(py::init([](){ return RangeImage{}; }));
    ri.def("createFromPointCloud", (void (RangeImage::*)(const CloudT&, float, float, float, const Eigen::Affine3f&, RangeImage::CoordinateFrame, float, float, int))&RangeImage::createFromPointCloud<CloudT>);
    ri.def("createFromPointCloud", (void (RangeImage::*)(const CloudT&, float, float, float, float, const Eigen::Affine3f&, RangeImage::CoordinateFrame, float, float, int))&RangeImage::createFromPointCloud<CloudT>);
}



//void defineIndices(py::module& m)
//{
//    auto idcs = py::class_<pcl::Indices>
//}


class NarfDescriptorPy : public pcl::NarfDescriptor
{
public:
    using NarfDescriptor::NarfDescriptor;
    using NarfDescriptor::computeFeature;
};

template <typename T>
void defineVector(py::module& m, std::string prefix)
{
    using vec = std::vector<T, std::allocator<T>>;
    auto vi = py::class_<vec>(m, std::string(prefix + "Vector").c_str());
    vi.def(py::init([](){ return std::vector<T, std::allocator<T>>{}; }));
    vi.def("push_back", (void (vec::*)(const T&))&vec::push_back);
    vi.def("push_back", (void (vec::*)(T&&))&vec::push_back);
    vi.def("at", (T& (vec::*)(size_t))&vec::at);
    vi.def("size", &vec::size);
}

//PYBIND11_MAKE_OPAQUE(std::vector<std::shared_ptr<pcl::PointCloud<pcl::PointXYZ>>>);

template <typename T>
void definePCVector(py::module& m, std::string prefix)
{
    using PC = pcl::PointCloud<pcl::PointXYZ>;
//    using PCPtr = std::shared_ptr<PC>;
    using vec = std::vector<PC, std::allocator<PC>>;
    auto vi = py::class_<vec>(m, ("Pc" + prefix + "Vector").c_str());
    vi.def(py::init([](){ return std::vector<PC, std::allocator<PC>>{}; }));
    vi.def(py::init([](PC cloud1, PC cloud2) { std::vector<PC> result; result.push_back(cloud1); result.push_back(cloud2); return result; }));
    vi.def("push_back", (void (vec::*)(const PC&))&vec::push_back);
//    vi.def("push_back", (void (vec::*)(PC&&))&vec::push_back);
    vi.def("at", (PC& (vec::*)(size_t))&vec::at);
    vi.def("size", &vec::size);
}



void defineNarfDescriptor(py::module& m)
{
    auto nd = py::class_<pcl::NarfDescriptor, NarfDescriptorPy, pcl::shared_ptr<NarfDescriptor>>(m, "NarfDescriptor");
    nd.def(py::init([](const pcl::RangeImage* range_image=nullptr, const pcl::Indices* indices=nullptr){ return NarfDescriptor{range_image, indices}; }));
    nd.def("setRangeImage", &NarfDescriptor::setRangeImage);
    nd.def("compute", &NarfDescriptor::compute);
//    nd.def("getParameters", &NarfDescriptor::getParameters);

}

template <typename PointT>
void definePyramid(py::module& m, std::string suffix)
{
    using PyramidT = pcl::filters::Pyramid<PointT>;
    using PointCloudPtr = std::shared_ptr<pcl::PointCloud<PointT>>;
    using PointCloudConstPtr = std::shared_ptr<const pcl::PointCloud<PointT>>;
    auto pmd = py::class_<PyramidT, pcl::shared_ptr<PyramidT>>(m, ("Pyramid" + suffix).c_str());
    pmd.def(py::init([](){ return pcl::filters::Pyramid<PointT>{}; }));
    pmd.def(py::init([](int levels) { return pcl::filters::Pyramid<PointT>{levels}; }));
    pmd.def("setInputCloud", &PyramidT::setInputCloud);
    pmd.def("getInputCloud", &PyramidT::getInputCloud);
    pmd.def("setNumberOfLevels", &PyramidT::setNumberOfLevels);
    pmd.def("getNumberOfLevels", &PyramidT::getNumberOfLevels);
    pmd.def("setNumberOfThreads", (void (PyramidT::*)())&PyramidT::setNumberOfThreads);
    pmd.def("setNumberOfThreads", (void (PyramidT::*)(unsigned int))&PyramidT::setNumberOfThreads);
    pmd.def("setLargeSmoothingKernel", (void (PyramidT::*)(bool))&PyramidT::setLargeSmoothingKernel);
    pmd.def("setDistanceThreshold", (void (PyramidT::*)(float))&PyramidT::setDistanceThreshold);
    pmd.def("getDistanceThreshold", &PyramidT::getDistanceThreshold);
    pmd.def("compute", (void (PyramidT::*)(std::vector<PointCloudPtr>&))&PyramidT::compute);
    pmd.def("getClassName", &PyramidT::getClassName);
}







//using PointCloudXYZ = pcl::PointCloud<pcl::PointXYZ>;
//using XYZIter = std::__wrap_iter<std::vector<pcl::PointXYZ, Eigen::aligned_allocator<pcl::PointXYZ>>::pointer>;

//py::call_guard<py::scoped_ostream_redirect, py::scoped_estream_redirect>()

PYBIND11_MODULE(tiledbpypcl, m) {
    m.doc() = R"pbdoc(
        TileDB: Pybind11 with PCL
        -----------------------

        .. currentmodule:: cmake_example

        .. autosummary::
           :toctree: _generate

            Cloud Funcs
            add
            point types
            PointCloudXYZ

    )pbdoc";

    // py::module m_vector = m.def_submodule("vectors", "vector types submodule");
    // defineVectorClasses(m_vector);

    py::module m_pts = m.def_submodule("point_types", "Point Types Submodule");
    definePointTypes(m_pts);

    py::module pc = m.def_submodule("PointCloud");
    definePointCloudClassFloatPts<PointXYZ>(pc, "PointXYZ");
    definePointCloudClassFloatPts<PointXYZI>(pc, "PointXYZI");
    py::module ri = m.def_submodule("RangeImage");
    defineRangeImage<PointXYZ>(ri, "XYZ");
    defineVector<int>(m, "Int");
    defineVector<float>(m, "Float");
    definePCVector<pcl::PointXYZ>(m, "XYZ");
    defineNarfDescriptor(m);
    definePyramid<pcl::PointXYZ>(m, "XYZ");
    m.def("add", &add);

//    py::class_<CloudFuncs>(m, "CloudFuncs")
//        .def(py::init<float, float, float, int>())
//        .def("add_all_pts", &CloudFuncs::add_all_pts)
//        .def("add_array", &CloudFuncs::add_array)
//        .def("loadXYZCloud", &CloudFuncs::loadXYZCloud);

//    py::class_<PointCloudXYZ>(m, "PointCloudXYZ")
//        .def(py::init<>())
//        .def("push_back", &PointCloudXYZ::push_back)
//        .def("size", &PointCloudXYZ::size)
////        .def("begin", static_cast<std::vector<pcl::PointXYZ>::iterator (PointCloudXYZ::*)(size_t)>(&PointCloudXYZ::begin));
////        .def("end", &PointCloudXYZ::end)
//        .def("at", static_cast<pcl::PointXYZ& (PointCloudXYZ::*)(size_t)>(&PointCloudXYZ::at))
//        .def_readonly("points", static_cast<std::vector<pcl::PointXYZ, Eigen::aligned_allocator<pcl::PointXYZ>> (PointCloudXYZ::*)>(&PointCloudXYZ::points));

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
