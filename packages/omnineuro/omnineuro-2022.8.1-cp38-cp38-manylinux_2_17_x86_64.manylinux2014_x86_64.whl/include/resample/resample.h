/*
  Header for resampler
*/
#ifndef RESAMPLER_H_
#define RESAMPLER_H_

#include <omnitable.h>

#include <armadillo>

class Interpolator {
   public:
    using shared_ptr_img = OmniTable::shared_ptr_img;
    using double_vec = std::vector<double>;
    using shared_ptr_double = std::shared_ptr<double_vec>;
    using affine_mat = arma::mat::fixed<4, 4>;
    Interpolator(shared_ptr_img, shared_ptr_img, int = 3);
    void initialize(int = 3);
    void interpolate(shared_ptr_img, shared_ptr_img, shared_ptr_img, arma::cube &, arma::mat &, int = 0, int = 0,
                     int = 0);
    int order;

   private:
    shared_ptr_img source;
    shared_ptr_img source_mask;
    int kx;
    int ky;
    int kz;
    int iknot;
    int iflag;
    shared_ptr_double tx;
    shared_ptr_double ty;
    shared_ptr_double tz;
    shared_ptr_double bcoef;
    int inbvx = 1;
    int inbvy = 1;
    int inbvz = 1;
    int iloy = 1;
    int iloz = 1;
    int extrap = 0;
    arma::cube fcn;
};

class Resampler {
   public:
    using shared_ptr_img = OmniTable::shared_ptr_img;
    using shared_ptr_interp = std::shared_ptr<Interpolator>;
    Resampler(shared_ptr_img, shared_ptr_img, shared_ptr_img, shared_ptr_img = nullptr, shared_ptr_img = nullptr,
              int = 3);
    void apply_transform(arma::mat &, int = 0, int = 0, int = 0);
    void initialize(int order = 3);
    shared_ptr_img output;
    shared_ptr_img target;
    shared_ptr_img source;
    shared_ptr_img source_mask;
    shared_ptr_interp interp;
    arma::cube target_mask;
};

#endif
