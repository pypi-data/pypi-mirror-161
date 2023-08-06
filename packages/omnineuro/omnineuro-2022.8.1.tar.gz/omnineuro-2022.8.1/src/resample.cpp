/*
  Implementation for resampler class
*/
#include <resample.h>
#include <bsplineinterface.h>
#include <armadillo>
#include <vector>

template<typename T>
void print_vec(const std::vector<T>& v) {
  for (auto& i: v) {
    arma::cout << i << " ";
  }
  arma::cout << arma::endl;
}

// Constructor
Resampler::Resampler(shared_ptr_img target, shared_ptr_img source, shared_ptr_img output,
  shared_ptr_img target_mask, shared_ptr_img source_mask, int order) :
  output(output), target(target), source(source), source_mask(source_mask),
  interp(std::make_shared<Interpolator>(source, source_mask, order)) {
    // check if target mask defined
    // if (target_mask)
    //   this->target_mask = target_mask->get_data();
    // else
    // Force target mask off
    this->target_mask.ones(arma::size(target->get_data()));
  }

// Resets output image and reinitialize the interpolator
void Resampler::initialize(int order) {
  output->data->fill(0); // reset the output image
  interp->initialize(order); // reinitialize the interpolator
}

// apply transformation
void Resampler::apply_transform(arma::mat& amat, int idx, int idy, int idz) {
  interp->interpolate(target, source, output, target_mask, amat, idx, idy, idz);
}

// Interpolator Constructor
Interpolator::Interpolator(shared_ptr_img source, shared_ptr_img source_mask, int order) : 
  order(order), source(source), source_mask(source_mask) {
  // initialize interpolator using image at source
  initialize(order);
}

// initialize the interpolator
void Interpolator::initialize(int order) {
  // initialize various things for spline interp
  kx = order; ky = kx; kz = ky;
  iknot = 0;
  tx = std::make_shared<double_vec>(source->shape[0]+kx);
  ty = std::make_shared<double_vec>(source->shape[1]+ky);
  tz = std::make_shared<double_vec>(source->shape[2]+kz);
  bcoef = std::make_shared<double_vec>(source->shape[0]*source->shape[1]*source->shape[2]);
  
  // initialize the iflag
  iflag = -1;

  // apply mask to data (if exists)
  // if (source_mask)
  //   fcn = source->get_data() % (source_mask->get_data() > 0);
  // else
  // Get data
  fcn = source->get_data();

  // setup bspline interpolator
  FC_bspline_sub_module_db3ink(
    source->x->data(), // x
    &source->shape[0], // nx
    source->y->data(), // y
    &source->shape[1], // ny
    source->z->data(), // z
    &source->shape[2], // nz
    fcn.memptr(), // fcn
    &kx, // kx
    &ky, // ky
    &kz, // kz
    &iknot, // iknot
    tx->data(), // tx
    ty->data(), // ty
    tz->data(), // tz
    bcoef->data(), // bcoef
    &iflag // iflag
  );
}

// interpolate
void Interpolator::interpolate(shared_ptr_img target, shared_ptr_img source, shared_ptr_img output,
  arma::cube& target_mask, arma::mat& amat, int idx, int idy, int idz) {
  // set initial iflag value // TODO: reorganize code so error codes work in openmp environment
  iflag = -1;

  // do interp
  FC_db3interp(
    target->x->data(), // x
    target->y->data(), // y
    target->z->data(), // z
    &idx, // idx
    &idy, // idy
    &idz, // idz
    tx->data(), // tx
    ty->data(), // ty
    tz->data(), // tz
    &target->shape[0], // ntx
    &target->shape[1], // nty
    &target->shape[2], // ntz
    &source->shape[0], // nx
    &source->shape[1], // ny
    &source->shape[2], // nz
    &kx, // kx
    &ky, // ky
    &kz, // kz
    bcoef->data(), // bcoef
    output->data->memptr(), // f
    &iflag, // iflag
    &inbvx, // inbvx
    &inbvy, // inbvy
    &inbvz, // inbvz
    &iloy, // iloy
    &iloz, // iloz
    &extrap, // extrap
    amat.memptr(), // affine
    source->grid_mat->memptr(), // grid_mat_source
    target->grid_mat->memptr(), // grid_mat_target
    target_mask.memptr() // target mask
  );
}