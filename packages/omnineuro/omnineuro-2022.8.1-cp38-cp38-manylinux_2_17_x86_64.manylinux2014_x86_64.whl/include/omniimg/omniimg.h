/*
  Header for Generic Image class
*/
#ifndef OMNIIMG_H_
#define OMNIIMG_H_

#include <armadillo>
#include <memory>
#include <vector>

namespace omniimg {
// Define a Generic Image class
class Image {
   public:
    using size_vec = std::vector<long int>;
    using double_vec = std::vector<double>;
    using shared_ptr_double = std::shared_ptr<double_vec>;
    Image(const double *ptr, size_vec shape, size_vec stride, const double *affine_ptr);
    std::shared_ptr<arma::cube> data;
    const double *ptr;
    size_vec shape;
    size_vec stride;
    const double *affine_ptr;  // DO NOT RELY ON THIS, NIBABEL SEEMS TO CHANGE THE POINTER WHENEVER IT FEELS LIKE...
                               // (use the affine parameter or get_affine method instead)
    shared_ptr_double x;
    shared_ptr_double y;
    shared_ptr_double z;
    std::shared_ptr<arma::mat> grid_mat;
    std::shared_ptr<arma::mat> affine;
    void regrid(shared_ptr_double, shared_ptr_double, shared_ptr_double);
    arma::mat get_affine();
    arma::cube get_data();
    arma::vec get_data_vec();
    long int get_data_vec_size();
    void free_mem();
};
}  // namespace omniimg
#endif
