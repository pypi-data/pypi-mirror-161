//
// Created by C S on 8/1/22.
//



#include <pcl/memory.h>
#include <pcl/pcl_macros.h>
#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <pcl/pcl_config.h>
#include <pcl/common/distances.h>
#include <concepts>

template <typename T>
concept XYZPt = requires(T p) { p.x; };

namespace pcl
{
  namespace filters
  {
     /** Pyramid constructs a multi-scale representation of an organised point cloud.
       * It is an iterative smoothing subsampling algorithm.
       * The subsampling is fixed to 2. Two smoothing kernels may be used:
       * - [1/16 1/4 3/8 1/4 1/16] slower but produces finer result;
       * - [1/4 1/2 1/2] the more conventional binomial kernel which is faster.
       * We use a memory efficient algorithm so the convolving and subsampling are combined in a
       * single step.
       *
       * \author Nizar Sallem
       */
     template <XYZPt PointT>
     class Pyramid
     {
     public:
         using PointCloudPtr = typename PointCloud<PointT>::Ptr;
         using PointCloudConstPtr = typename PointCloud<PointT>::ConstPtr;
         using Ptr = shared_ptr< Pyramid<PointT> >;
         using ConstPtr = shared_ptr< const Pyramid<PointT> >;

         Pyramid (int levels = 4)
                 : levels_ (levels)
                 , large_ (false)
                 , threshold_ (0.01)
                 , threads_ (0)
         {
             name_ = "Pyramid";
         }

         /** \brief Provide a pointer to the input dataset
           * \param cloud the const boost shared pointer to a PointCloud message
           */
         inline void
         setInputCloud (const PointCloudConstPtr &cloud) { input_ = cloud; }

         /** \brief Get a pointer to the input point cloud dataset. */
         inline PointCloudConstPtr const
         getInputCloud () { return (input_); }

         /** \brief Set the number of pyramid levels
           * \param levels desired number of pyramid levels
           */
         inline void
         setNumberOfLevels (int levels) { levels_ = levels; }

         /// \brief \return the number of pyramid levels
         inline int
         getNumberOfLevels () const { return (levels_); }

         /** \brief Initialize the scheduler and set the number of threads to use.
           * \param nr_threads the number of hardware threads to use (0 sets the value back to automatic).
           */
         inline void
         setNumberOfThreads (unsigned int nr_threads = 0) { threads_ = nr_threads; }

         /** \brief Choose a larger smoothing kernel for enhanced smoothing.
           * \param large if true large smoothng kernel will be used.
           */
         inline void
         setLargeSmoothingKernel (bool large) { large_ = large; }

         /** Only points such us distance (center,point) < threshold are accounted for to prevent
           * ghost points.
           * Default value is 0.01, to disable set to std::numeric<float>::infinity ().
           * \param[in] threshold maximum allowed distance between center and neighbor.
           */
         inline void
         setDistanceThreshold (float threshold) { threshold_ = threshold; }

         /// \return the distance threshold
         inline float
         getDistanceThreshold () const { return (threshold_); }

         /** \brief compute the pyramid levels.
           * \param[out] output the constructed pyramid. It is resized to the number of levels.
           * \remark input_ is copied to output[0] for consistency reasons.
           */
         void
         compute (std::vector<PointCloudPtr>& output);

         inline const std::string&
         getClassName () const { return (name_); }

     private:

         /// \brief init computation
         bool
         initCompute ();

         /** \brief nullify a point
           * \param[in][out] p point to nullify
           */
         inline void nullify (pcl::RGB& p)
         {
             p.r = 0; p.g = 0; p.b = 0;
         }

         inline void
         nullify (pcl::PointXYZ& p) const
         {
                p.x = p.y = p.z = std::numeric_limits<float>::quiet_NaN ();
         }

         inline void
         nullify (pcl::PointXYZRGB& p) const
         {
             p.x = p.y = p.z = std::numeric_limits<float>::quiet_NaN ();
         }

         inline void
         nullify (pcl::PointXYZRGBA& p) const
         {
             p.x = p.y = p.z = std::numeric_limits<float>::quiet_NaN ();
         }

         /// \brief The input point cloud dataset.
         PointCloudConstPtr input_;
         /// \brief number of pyramid levels
         int levels_;
         /// \brief use large smoothing kernel
         bool large_;
         /// \brief filter name
         std::string name_;
         /// \brief smoothing kernel
         Eigen::MatrixXf kernel_;
         /// Threshold distance between adjacent points
         float threshold_;
         /// \brief number of threads
         unsigned int threads_;

     public:
         PCL_MAKE_ALIGNED_OPERATOR_NEW
     };
  }
}









  namespace pcl
  {

      namespace filters
      {

         template <XYZPt PointT> bool
         Pyramid<PointT>::initCompute ()
         {
             if (!input_->isOrganized ())
             {
                 PCL_ERROR ("[pcl::fileters::%s::initCompute] Number of levels should be at least 2!\n", getClassName ().c_str ());
                 return (false);
             }

             if (levels_ < 2)
             {
                 PCL_ERROR ("[pcl::fileters::%s::initCompute] Number of levels should be at least 2!\n", getClassName ().c_str ());
                 return (false);
             }

             // std::size_t ratio (std::pow (2, levels_));
             // std::size_t last_width = input_->width / ratio;
             // std::size_t last_height = input_->height / ratio;

             if (levels_ > 4)
             {
                 PCL_ERROR ("[pcl::fileters::%s::initCompute] Number of levels should not exceed 4!\n", getClassName ().c_str ());
                 return (false);
             }

             if (large_)
             {
                 Eigen::VectorXf k (5);
                 k << 1.f/16.f, 1.f/4.f, 3.f/8.f, 1.f/4.f, 1.f/16.f;
                 kernel_ = k * k.transpose ();
                 if (threshold_ != std::numeric_limits<float>::infinity ())
                     threshold_ *= 2 * threshold_;

             }
             else
             {
                 Eigen::VectorXf k (3);
                 k << 1.f/4.f, 1.f/2.f, 1.f/4.f;
                 kernel_ = k * k.transpose ();
                 if (threshold_ != std::numeric_limits<float>::infinity ())
                     threshold_ *= threshold_;
             }

             return (true);
         }

         template <XYZPt PointT> void
         Pyramid<PointT>::compute (std::vector<PointCloudPtr>& output)
         {
             std::cout << "compute" << std::endl;
             if (!initCompute ())
             {
                 PCL_ERROR ("[pcl::%s::compute] initCompute failed!\n", getClassName ().c_str ());
                 return;
             }

             int kernel_rows = static_cast<int> (kernel_.rows ());
             int kernel_cols = static_cast<int> (kernel_.cols ());
             int kernel_center_x = kernel_cols / 2;
             int kernel_center_y = kernel_rows / 2;

             output.resize (levels_ + 1);
             output[0].reset (new pcl::PointCloud<PointT>);
             *(output[0]) = *input_;

             if (input_->is_dense)
             {
                 for (int l = 1; l <= levels_; ++l)
                 {
                     output[l].reset (new pcl::PointCloud<PointT> (output[l-1]->width/2, output[l-1]->height/2));
                     const PointCloud<PointT> &previous = *output[l-1];
                     PointCloud<PointT> &next = *output[l];
  #pragma omp parallel for \
    default(none)          \
    shared(next)           \
    num_threads(threads_)
                     for(int i=0; i < next.height; ++i)
                     {
                         for(int j=0; j < next.width; ++j)
                         {
                             for(int m=0; m < kernel_rows; ++m)
                             {
                                 int mm = kernel_rows - 1 - m;
                                 for(int n=0; n < kernel_cols; ++n)
                                 {
                                     int nn = kernel_cols - 1 - n;

                                     int ii = 2*i + (m - kernel_center_y);
                                     int jj = 2*j + (n - kernel_center_x);

                                     if (ii < 0) ii = 0;
                                     if (ii >= previous.height) ii = previous.height - 1;
                                     if (jj < 0) jj = 0;
                                     if (jj >= previous.width) jj = previous.width - 1;
                                     next.at (j).data[i] += previous.at (jj).data[ii] * kernel_ (mm,nn);
                                 }
                             }
                         }
                     }
                 }
             }
             else
             {
                 for (int l = 1; l <= levels_; ++l)
                 {
                     output[l].reset (new pcl::PointCloud<PointT> (output[l-1]->width/2, output[l-1]->height/2));
                     const PointCloud<PointT> &previous = *output[l-1];
                     PointCloud<PointT> &next = *output[l];
  #pragma omp parallel for \
    default(none)          \
    shared(next)           \
    num_threads(threads_)
                     for(int i=0; i < next.height; ++i)
                     {
                         for(int j=0; j < next.width; ++j)
                         {
                             float weight = 0;
                             for(int m=0; m < kernel_rows; ++m)
                             {
                                 int mm = kernel_rows - 1 - m;
                                 for(int n=0; n < kernel_cols; ++n)
                                 {
                                     int nn = kernel_cols - 1 - n;
                                     int ii = 2*i + (m - kernel_center_y);
                                     int jj = 2*j + (n - kernel_center_x);
                                     if (ii < 0) ii = 0;
                                     if (ii >= previous.height) ii = previous.height - 1;
                                     if (jj < 0) jj = 0;
                                     if (jj >= previous.width) jj = previous.width - 1;
                                     if (!isFinite (previous.at (jj,ii)))
                                         continue;
                                     if (pcl::squaredEuclideanDistance (previous.at (2*j,2*i), previous.at (jj,ii)) < threshold_)
                                     {
                                         next.at (j).data[i] += previous.at (jj).data[ii] * kernel_ (mm,nn);
                                         weight+= kernel_ (mm,nn);
                                     }
                                 }
                             }
                             if (weight == 0)
                                 nullify (next.at (j,i));
                             else
                             {
                                 weight = 1.f/weight;
                                 next.at (j).data[i]*= weight;
                             }
                         }
                     }
                 }
             }
         }


         template <> void
         Pyramid<pcl::PointXYZRGB>::compute (std::vector<Pyramid<pcl::PointXYZRGB>::PointCloudPtr> &output)
         {
             std::cout << "PointXYZRGB" << std::endl;
             if (!initCompute ())
             {
                 PCL_ERROR ("[pcl::%s::compute] initCompute failed!\n", getClassName ().c_str ());
                 return;
             }

             int kernel_rows = static_cast<int> (kernel_.rows ());
             int kernel_cols = static_cast<int> (kernel_.cols ());
             int kernel_center_x = kernel_cols / 2;
             int kernel_center_y = kernel_rows / 2;

             output.resize (levels_ + 1);
             output[0].reset (new pcl::PointCloud<pcl::PointXYZRGB>);
             *(output[0]) = *input_;

             if (input_->is_dense)
             {
                 for (int l = 1; l <= levels_; ++l)
                 {
                     output[l].reset (new pcl::PointCloud<pcl::PointXYZRGB> (output[l-1]->width/2, output[l-1]->height/2));
                     const PointCloud<pcl::PointXYZRGB> &previous = *output[l-1];
                     PointCloud<pcl::PointXYZRGB> &next = *output[l];
  #pragma omp parallel for \
    default(none)          \
    shared(next)           \
    num_threads(threads_)
                     for(int i=0; i < next.height; ++i)              // rows
                     {
                         for(int j=0; j < next.width; ++j)          // columns
                         {
                             float r = 0, g = 0, b = 0;
                             for(int m=0; m < kernel_rows; ++m)     // kernel rows
                             {
                                 int mm = kernel_rows - 1 - m;      // row index of flipped kernel
                                 for(int n=0; n < kernel_cols; ++n) // kernel columns
                                 {
                                     int nn = kernel_cols - 1 - n;  // column index of flipped kernel
                                     // index of input signal, used for checking boundary
                                     int ii = 2*i + (m - kernel_center_y);
                                     int jj = 2*j + (n - kernel_center_x);

                                     // ignore input samples which are out of bound
                                     if (ii < 0) ii = 0;
                                     if (ii >= previous.height) ii = previous.height - 1;
                                     if (jj < 0) jj = 0;
                                     if (jj >= previous.width) jj = previous.width - 1;
                                     next.at (j,i).x += previous.at (jj,ii).x * kernel_ (mm,nn);
                                     next.at (j,i).y += previous.at (jj,ii).y * kernel_ (mm,nn);
                                     next.at (j,i).z += previous.at (jj,ii).z * kernel_ (mm,nn);
                                     b += previous.at (jj,ii).b * kernel_ (mm,nn);
                                     g += previous.at (jj,ii).g * kernel_ (mm,nn);
                                     r += previous.at (jj,ii).r * kernel_ (mm,nn);
                                 }
                             }
                             next.at (j,i).b = static_cast<std::uint8_t> (b);
                             next.at (j,i).g = static_cast<std::uint8_t> (g);
                             next.at (j,i).r = static_cast<std::uint8_t> (r);
                         }
                     }
                 }
             }
             else
             {
                 for (int l = 1; l <= levels_; ++l)
                 {
                     output[l].reset (new pcl::PointCloud<pcl::PointXYZRGB> (output[l-1]->width/2, output[l-1]->height/2));
                     const PointCloud<pcl::PointXYZRGB> &previous = *output[l-1];
                     PointCloud<pcl::PointXYZRGB> &next = *output[l];
  #pragma omp parallel for \
    default(none)          \
    shared(next)           \
    num_threads(threads_)
                     for(int i=0; i < next.height; ++i)
                     {
                         for(int j=0; j < next.width; ++j)
                         {
                             float weight = 0;
                             float r = 0, g = 0, b = 0;
                             for(int m=0; m < kernel_rows; ++m)
                             {
                                 int mm = kernel_rows - 1 - m;
                                 for(int n=0; n < kernel_cols; ++n)
                                 {
                                     int nn = kernel_cols - 1 - n;
                                     int ii = 2*i + (m - kernel_center_y);
                                     int jj = 2*j + (n - kernel_center_x);
                                     if (ii < 0) ii = 0;
                                     if (ii >= previous.height) ii = previous.height - 1;
                                     if (jj < 0) jj = 0;
                                     if (jj >= previous.width) jj = previous.width - 1;
                                     if (!isFinite (previous.at (jj,ii)))
                                         continue;
                                     if (pcl::squaredEuclideanDistance (previous.at (2*j,2*i), previous.at (jj,ii)) < threshold_)
                                     {
                                         next.at (j,i).x += previous.at (jj,ii).x * kernel_ (mm,nn);
                                         next.at (j,i).y += previous.at (jj,ii).y * kernel_ (mm,nn);
                                         next.at (j,i).z += previous.at (jj,ii).z * kernel_ (mm,nn);
                                         b += previous.at (jj,ii).b * kernel_ (mm,nn);
                                         g += previous.at (jj,ii).g * kernel_ (mm,nn);
                                         r += previous.at (jj,ii).r * kernel_ (mm,nn);
                                         weight+= kernel_ (mm,nn);
                                     }
                                 }
                             }
                             if (weight == 0)
                                 nullify (next.at (j,i));
                             else
                             {
                                 weight = 1.f/weight;
                                 r*= weight; g*= weight; b*= weight;
                                 next.at (j,i).x*= weight; next.at (j,i).y*= weight; next.at (j,i).z*= weight;
                                 next.at (j,i).b = static_cast<std::uint8_t> (b);
                                 next.at (j,i).g = static_cast<std::uint8_t> (g);
                                 next.at (j,i).r = static_cast<std::uint8_t> (r);
                             }
                         }
                     }
                 }
             }
         }

         template <> void
         Pyramid<pcl::PointXYZRGBA>::compute (std::vector<Pyramid<pcl::PointXYZRGBA>::PointCloudPtr> &output)
         {
             std::cout << "PointXYZRGBA" << std::endl;
             if (!initCompute ())
             {
                 PCL_ERROR ("[pcl::%s::compute] initCompute failed!\n", getClassName ().c_str ());
                 return;
             }

             int kernel_rows = static_cast<int> (kernel_.rows ());
             int kernel_cols = static_cast<int> (kernel_.cols ());
             int kernel_center_x = kernel_cols / 2;
             int kernel_center_y = kernel_rows / 2;

             output.resize (levels_ + 1);
             output[0].reset (new pcl::PointCloud<pcl::PointXYZRGBA>);
             *(output[0]) = *input_;

             if (input_->is_dense)
             {
                 for (int l = 1; l <= levels_; ++l)
                 {
                     output[l].reset (new pcl::PointCloud<pcl::PointXYZRGBA> (output[l-1]->width/2, output[l-1]->height/2));
                     const PointCloud<pcl::PointXYZRGBA> &previous = *output[l-1];
                     PointCloud<pcl::PointXYZRGBA> &next = *output[l];
  #pragma omp parallel for \
    default(none)          \
    shared(next)           \
    num_threads(threads_)
                     for(int i=0; i < next.height; ++i)              // rows
                     {
                         for(int j=0; j < next.width; ++j)          // columns
                         {
                             float r = 0, g = 0, b = 0, a = 0;
                             for(int m=0; m < kernel_rows; ++m)     // kernel rows
                             {
                                 int mm = kernel_rows - 1 - m;      // row index of flipped kernel
                                 for(int n=0; n < kernel_cols; ++n) // kernel columns
                                 {
                                     int nn = kernel_cols - 1 - n;  // column index of flipped kernel
                                     // index of input signal, used for checking boundary
                                     int ii = 2*i + (m - kernel_center_y);
                                     int jj = 2*j + (n - kernel_center_x);

                                     // ignore input samples which are out of bound
                                     if (ii < 0) ii = 0;
                                     if (ii >= previous.height) ii = previous.height - 1;
                                     if (jj < 0) jj = 0;
                                     if (jj >= previous.width) jj = previous.width - 1;
                                     next.at (j,i).x += previous.at (jj,ii).x * kernel_ (mm,nn);
                                     next.at (j,i).y += previous.at (jj,ii).y * kernel_ (mm,nn);
                                     next.at (j,i).z += previous.at (jj,ii).z * kernel_ (mm,nn);
                                     b += previous.at (jj,ii).b * kernel_ (mm,nn);
                                     g += previous.at (jj,ii).g * kernel_ (mm,nn);
                                     r += previous.at (jj,ii).r * kernel_ (mm,nn);
                                     a += previous.at (jj,ii).a * kernel_ (mm,nn);
                                 }
                             }
                             next.at (j,i).b = static_cast<std::uint8_t> (b);
                             next.at (j,i).g = static_cast<std::uint8_t> (g);
                             next.at (j,i).r = static_cast<std::uint8_t> (r);
                             next.at (j,i).a = static_cast<std::uint8_t> (a);
                         }
                     }
                 }
             }
             else
             {
                 for (int l = 1; l <= levels_; ++l)
                 {
                     output[l].reset (new pcl::PointCloud<pcl::PointXYZRGBA> (output[l-1]->width/2, output[l-1]->height/2));
                     const PointCloud<pcl::PointXYZRGBA> &previous = *output[l-1];
                     PointCloud<pcl::PointXYZRGBA> &next = *output[l];
  #pragma omp parallel for \
    default(none)          \
    shared(next)           \
    num_threads(threads_)
                     for(int i=0; i < next.height; ++i)
                     {
                         for(int j=0; j < next.width; ++j)
                         {
                             float weight = 0;
                             float r = 0, g = 0, b = 0, a = 0;
                             for(int m=0; m < kernel_rows; ++m)
                             {
                                 int mm = kernel_rows - 1 - m;
                                 for(int n=0; n < kernel_cols; ++n)
                                 {
                                     int nn = kernel_cols - 1 - n;
                                     int ii = 2*i + (m - kernel_center_y);
                                     int jj = 2*j + (n - kernel_center_x);
                                     if (ii < 0) ii = 0;
                                     if (ii >= previous.height) ii = previous.height - 1;
                                     if (jj < 0) jj = 0;
                                     if (jj >= previous.width) jj = previous.width - 1;
                                     if (!isFinite (previous.at (jj,ii)))
                                         continue;
                                     if (pcl::squaredEuclideanDistance (previous.at (2*j,2*i), previous.at (jj,ii)) < threshold_)
                                     {
                                         next.at (j,i).x += previous.at (jj,ii).x * kernel_ (mm,nn);
                                         next.at (j,i).y += previous.at (jj,ii).y * kernel_ (mm,nn);
                                         next.at (j,i).z += previous.at (jj,ii).z * kernel_ (mm,nn);
                                         b += previous.at (jj,ii).b * kernel_ (mm,nn);
                                         g += previous.at (jj,ii).g * kernel_ (mm,nn);
                                         r += previous.at (jj,ii).r * kernel_ (mm,nn);
                                         a += previous.at (jj,ii).a * kernel_ (mm,nn);
                                         weight+= kernel_ (mm,nn);
                                     }
                                 }
                             }
                             if (weight == 0)
                                 nullify (next.at (j,i));
                             else
                             {
                                 weight = 1.f/weight;
                                 r*= weight; g*= weight; b*= weight; a*= weight;
                                 next.at (j,i).x*= weight; next.at (j,i).y*= weight; next.at (j,i).z*= weight;
                                 next.at (j,i).b = static_cast<std::uint8_t> (b);
                                 next.at (j,i).g = static_cast<std::uint8_t> (g);
                                 next.at (j,i).r = static_cast<std::uint8_t> (r);
                                 next.at (j,i).a = static_cast<std::uint8_t> (a);
                             }
                         }
                     }
                 }
             }
         }

//          template <> void
//          Pyramid<pcl::RGB>::compute (std::vector<Pyramid<pcl::RGB>::PointCloudPtr> &output)
//          {
//              std::cout << "RGB" << std::endl;
//              if (!initCompute ())
//              {
//                  PCL_ERROR ("[pcl::%s::compute] initCompute failed!\n", getClassName ().c_str ());
//                  return;
//              }

//              int kernel_rows = static_cast<int> (kernel_.rows ());
//              int kernel_cols = static_cast<int> (kernel_.cols ());
//              int kernel_center_x = kernel_cols / 2;
//              int kernel_center_y = kernel_rows / 2;

//              output.resize (levels_ + 1);
//              output[0].reset (new pcl::PointCloud<pcl::RGB>);
//              *(output[0]) = *input_;

//              if (input_->is_dense)
//              {
//                  for (int l = 1; l <= levels_; ++l)
//                  {
//                      output[l].reset (new pcl::PointCloud<pcl::RGB> (output[l-1]->width/2, output[l-1]->height/2));
//                      const PointCloud<pcl::RGB> &previous = *output[l-1];
//                      PointCloud<pcl::RGB> &next = *output[l];
//   #pragma omp parallel for \
//     default(none)          \
//     shared(next)           \
//     num_threads(threads_)
//                      for(int i=0; i < next.height; ++i)
//                      {
//                          for(int j=0; j < next.width; ++j)
//                          {
//                              float r = 0, g = 0, b = 0;
//                              for(int m=0; m < kernel_rows; ++m)
//                              {
//                                  int mm = kernel_rows - 1 - m;
//                                  for(int n=0; n < kernel_cols; ++n)
//                                  {
//                                      int nn = kernel_cols - 1 - n;
//                                      int ii = 2*i + (m - kernel_center_y);
//                                      int jj = 2*j + (n - kernel_center_x);
//                                      if (ii < 0) ii = 0;
//                                      if (ii >= previous.height) ii = previous.height - 1;
//                                      if (jj < 0) jj = 0;
//                                      if (jj >= previous.width) jj = previous.width - 1;
//                                      b += previous.at (jj,ii).b * kernel_ (mm,nn);
//                                      g += previous.at (jj,ii).g * kernel_ (mm,nn);
//                                      r += previous.at (jj,ii).r * kernel_ (mm,nn);
//                                  }
//                              }
//                              next.at (j,i).b = static_cast<std::uint8_t> (b);
//                              next.at (j,i).g = static_cast<std::uint8_t> (g);
//                              next.at (j,i).r = static_cast<std::uint8_t> (r);
//                          }
//                      }
//                  }
//              }
//              else
//              {
//                  for (int l = 1; l <= levels_; ++l)
//                  {
//                      output[l].reset (new pcl::PointCloud<pcl::RGB> (output[l-1]->width/2, output[l-1]->height/2));
//                      const PointCloud<pcl::RGB> &previous = *output[l-1];
//                      PointCloud<pcl::RGB> &next = *output[l];
//   #pragma omp parallel for \
//     default(none)          \
//     shared(next)           \
//     num_threads(threads_)
//                      for(int i=0; i < next.height; ++i)
//                      {
//                          for(int j=0; j < next.width; ++j)
//                          {
//                              float weight = 0;
//                              float r = 0, g = 0, b = 0;
//                              for(int m=0; m < kernel_rows; ++m)
//                              {
//                                  int mm = kernel_rows - 1 - m;
//                                  for(int n=0; n < kernel_cols; ++n)
//                                  {
//                                      int nn = kernel_cols - 1 - n;
//                                      int ii = 2*i + (m - kernel_center_y);
//                                      int jj = 2*j + (n - kernel_center_x);
//                                      if (ii < 0) ii = 0;
//                                      if (ii >= previous.height) ii = previous.height - 1;
//                                      if (jj < 0) jj = 0;
//                                      if (jj >= previous.width) jj = previous.width - 1;
//                                      if (!isFinite (previous.at (jj,ii)))
//                                          continue;
//                                      if (pcl::squaredEuclideanDistance (previous.at (2*j,2*i), previous.at (jj,ii)) < threshold_)
//                                      {
//                                          b += previous.at (jj,ii).b * kernel_ (mm,nn);
//                                          g += previous.at (jj,ii).g * kernel_ (mm,nn);
//                                          r += previous.at (jj,ii).r * kernel_ (mm,nn);
//                                          weight+= kernel_ (mm,nn);
//                                      }
//                                  }
//                              }
//                              if (weight == 0)
//                                  nullify (next.at (j,i));
//                              else
//                              {
//                                  weight = 1.f/weight;
//                                  r*= weight; g*= weight; b*= weight;
//                                  next.at (j,i).b = static_cast<std::uint8_t> (b);
//                                  next.at (j,i).g = static_cast<std::uint8_t> (g);
//                                  next.at (j,i).r = static_cast<std::uint8_t> (r);
//                              }
//                          }
//                      }
//                  }
//              }
//          }

     } // namespace filters
 } // namespace pcl
