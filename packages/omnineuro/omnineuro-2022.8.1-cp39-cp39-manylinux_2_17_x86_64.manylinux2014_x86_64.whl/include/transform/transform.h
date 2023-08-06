/*
    Header for transform class
*/

#ifndef TRANSFORM_H_
#define TRANSFORM_H_

#include <algorithm>
#include <armadillo>
#include <omnitable.h>
#include <resample.h>

class Transformer {
  public:
    using shared_ptr_img = OmniTable::shared_ptr_img;
    Transformer(shared_ptr_img,shared_ptr_img,shared_ptr_img,shared_ptr_img,shared_ptr_img,arma::mat&,int = 12);
    void calc_residual(arma::mat, bool = false);
    void calc_gradient(arma::vec*, arma::mat, shared_ptr_img, int = 0);
    std::shared_ptr<arma::vec> params;
    std::function<arma::mat(arma::vec)> params_to_affine;
    std::function<void(OmniTable::shared_ptr_img, arma::mat, arma::mat&)> params_gradient;
    shared_ptr_img gradient_x;
    shared_ptr_img gradient_y;
    shared_ptr_img gradient_z;
    shared_ptr_img residual;
    std::shared_ptr<Resampler> resample;
    arma::mat affine_grad;
    double target_size;
    unsigned int num_params;
  private:
    shared_ptr_img target;
    shared_ptr_img source;
    shared_ptr_img output;
    shared_ptr_img target_mask;
    static void image_gradient(shared_ptr_img, shared_ptr_img, shared_ptr_img, shared_ptr_img);
    static void param_12_gradient(shared_ptr_img, arma::mat, arma::mat&);
    static void param_9_gradient(shared_ptr_img, arma::mat, arma::mat&);
    static void param_6_gradient(shared_ptr_img, arma::mat, arma::mat&);
    static void param_3_gradient(shared_ptr_img, arma::mat, arma::mat&);
    static arma::mat param_12_affine(arma::vec);
    static arma::mat param_9_affine(arma::vec);
    static arma::mat param_6_affine(arma::vec);
    static arma::mat param_3_affine(arma::vec);
};

#endif
