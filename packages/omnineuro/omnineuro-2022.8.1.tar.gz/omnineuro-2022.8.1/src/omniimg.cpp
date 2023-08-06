/*
  Implementation details for Generic Image class
*/
#include <omniimg.h>
#include <armadillo>

using namespace omniimg;

// Constructor
Image::Image(const double* ptr, size_vec shape, size_vec stride, const double* affine_ptr) :
  ptr(ptr), shape(shape), stride(stride), affine_ptr(affine_ptr)  {

  // create cube object from data
  this->data = std::make_shared<arma::cube>(ptr, this->shape[0], this->shape[1], this->shape[2]);

  // create mat for affine matrix
  this->affine = std::make_shared<arma::mat::fixed<4,4>>(this->affine_ptr);

  // initialize position vectors
  this->x = std::make_shared<Image::double_vec>(this->shape[0]);
  std::vector<double>::iterator x_it = this->x->begin();
  this->y = std::make_shared<Image::double_vec>(this->shape[1]);
  std::vector<double>::iterator y_it = this->y->begin();
  this->z = std::make_shared<Image::double_vec>(this->shape[2]);
  std::vector<double>::iterator z_it = this->z->begin();

  /*
    This operates under the assumption that the affine matrix in the
    nifti header is always a rigid body transform. If shears are involved
    the following grid creation will probably fail, since the grid is not
    equaldistant anymore. However, this is very unlikely to occur I think...
    TODO: check that the affine is rigid
  */
  
  /*
    Since the interpolator only works on a increasing grid
    we should reflect any axis that is decreasing. This can be done
    by detecting the diagonal and flipping the signs of any negatives
  */
  this->grid_mat = std::make_shared<arma::mat>(4,4,arma::fill::eye);
  if (this->affine->at(0,0) < 0)
    this->grid_mat->at(0,0) = -1;
  if (this->affine->at(1,1) < 0)
    this->grid_mat->at(1,1) = -1;
  if (this->affine->at(2,2) < 0)
    this->grid_mat->at(2,2) = -1;

  // combine the grid mat and the affine mat
  arma::mat::fixed<4,4> combined_mat = (*(this->grid_mat))*(*(this->affine));

  // constuct position vectors by applying affine to indices
  for (auto i=0; i<this->shape[0]; i++) {
    *x_it = combined_mat(0,0)*i + combined_mat(0,3);
    ++x_it;
  }
  for (auto j=0; j<this->shape[1]; j++) {
    *y_it = combined_mat(1,1)*j + combined_mat(1,3);
    ++y_it;
  }
  for (auto k=0; k<this->shape[2]; k++) {
    *z_it = combined_mat(2,2)*k + combined_mat(2,3);
    ++z_it;
  }
}

// Changes the spacing for the image (This will clear the current reference
// to the data of the current image)
// This is intended to be run with a resample of another image
void Image::regrid(shared_ptr_double x, shared_ptr_double y, shared_ptr_double z) {
  // reassign the grid pointers to the new grid
  this->x = x;
  this->y = y;
  this->z = z;

  // Update the size
  this->shape[0] = x->size();
  this->shape[1] = y->size();
  this->shape[2] = z->size();

  // Update the stride (first stride is always 8 since a double)
  this->stride[0] = sizeof(double);
  this->stride[1] = (x->size())*sizeof(double);
  this->stride[2] = (x->size())*(y->size())*sizeof(double);

  // Update the affine of the image (calculate spacing and then assign)
  this->affine->at(0,0) = ((*x)[1] - (*x)[0])*this->grid_mat->at(0,0);
  this->affine->at(1,1) = ((*y)[1] - (*y)[0])*this->grid_mat->at(1,1);
  this->affine->at(2,2) = ((*z)[1] - (*z)[0])*this->grid_mat->at(2,2);

  // Delete the memory pointed to by the current pointer
  this->free_mem();

  // Change the raw pointer to a new chunk of memory of the new size
  this->ptr = new double[(x->size())*(y->size())*(z->size())]{};

  // Now create a new cube for the data from the pointer
  this->data = std::make_shared<arma::cube>(this->ptr, this->shape[0], this->shape[1], this->shape[2]);
}

// returns a copy of the affine
arma::mat Image::get_affine() {
  return *(this->affine);
}

// returns a copy of the data
arma::cube Image::get_data() {
  return *(this->data);
}

// returns a copy of the vectorized version of the data
arma::vec Image::get_data_vec() {
  return arma::vectorise(*(this->data));
}

// get size of vectoriszed data
long int Image::get_data_vec_size() {
  return this->shape[0]*this->shape[1]*this->shape[2];
}

// Deletes allocated memory held by Image
void Image::free_mem() {
  delete[] this->ptr;
}
