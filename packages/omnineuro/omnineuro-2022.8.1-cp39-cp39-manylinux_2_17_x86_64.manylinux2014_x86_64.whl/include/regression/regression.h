/*
  Header for regression routines
*/

#ifndef REGRESSION_H_
#define REGRESSION_H_

#include <omnitable.h>
#include <resample.h>

#include <armadillo>
#include <string>
#include <vector>

class Regressor {
   public:
    using shared_ptr_img = OmniTable::shared_ptr_img;
    using string = std::string;
    using shared_ptr_mat = std::shared_ptr<arma::mat>;
    Regressor(std::vector<shared_ptr_img>, shared_ptr_img, shared_ptr_img, shared_ptr_img, string, shared_ptr_img,
              shared_ptr_img, shared_ptr_img, bool, bool = false, arma::cube = arma::cube(1, 1, 1, arma::fill::zeros));
    void calc_output();
    void calc_blurred_output();
    void calc_gradient(arma::vec *, arma::mat &, int index = 12);
    void calc_params(arma::mat &);
    std::vector<shared_ptr_img> sources;
    shared_ptr_img output;
    shared_ptr_img blurred_output;
    shared_ptr_img aligned_target;
    std::shared_ptr<Resampler> resample;
    shared_ptr_img regress_mask;
    std::shared_ptr<arma::vec> params;
    shared_ptr_mat interaction_mat;
    shared_ptr_mat blurred_interaction_mat;

   private:
    void create_interaction_mat(string, bool);
    string modelspec;
    bool use_kernel;
    arma::cube blur_kernel;
};

// string parser
void parse_string(std::vector<std::string> &, std::string, std::string);

#endif
