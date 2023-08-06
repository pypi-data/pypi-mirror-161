/*
  Header for optimization routines
*/
#ifndef OPTIMIZE_H_
#define OPTIMIZE_H_

#include <omnitable.h>
#include <resample.h>

#include <armadillo>
#include <functional>
#include <optim.hpp>
#include <string>

class Optimizer {
   public:
    using shared_ptr_img = OmniTable::shared_ptr_img;
    using shared_ptr_params = std::shared_ptr<arma::vec>;
    using unique_ptr_settings = std::unique_ptr<optim::algo_settings_t>;
    using objfx = std::function<double(const arma::vec &, arma::vec *, void *)>;
    Optimizer(std::string, double, double, int, objfx);
    bool run(shared_ptr_params);
    shared_ptr_img output;
    unique_ptr_settings settings = std::make_unique<optim::algo_settings_t>();

   private:
    shared_ptr_img target;
    shared_ptr_img source;
    objfx opt_objfn;
    std::string obj_fx_type;
};

#endif
