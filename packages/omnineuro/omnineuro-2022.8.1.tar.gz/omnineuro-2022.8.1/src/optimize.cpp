/*
  Implementation file for optimizers
*/

#include <optimize.h>
#include <optim.hpp>
#include <armadillo>
#include <cmath>
#include <string>

// Constructor for Optimizer class
Optimizer::Optimizer(std::string obj_fx_type, double step_size, double err_tol, int iterations, objfx opt_objfn)
  : opt_objfn(opt_objfn), obj_fx_type(obj_fx_type) {
  // Set optimizer settings
  settings->gd_settings.method = 7;
  settings->gd_settings.par_step_size = step_size;
  settings->grad_err_tol = err_tol;
  settings->iter_max = iterations;
  settings->conv_failure_switch = 0;
  settings->vals_bound = true;
  settings->upper_bounds = {1.5,1.5,1.5,100,
                            1.5,1.5,1.5,100,
                            1.5,1.5,1.5,100};
  settings->lower_bounds = {0.5,-1.5,-1.5,-100,
                            -1.5,0.5,-1.5,-100,
                            -1.5,-1.5,0.5,-100};
}

// Implementation for run method of Optimizer class
bool Optimizer::run(shared_ptr_params init) {
  bool fakedata = false; // make empty reference for data since we pass by lambda capture instead
  arma::cout << "Using Optimizer: " << obj_fx_type << arma::endl;
  arma::cout << "Running optimization..." << arma::endl;
  if (obj_fx_type.compare("gd") == 0) {
    return optim::gd(*init, opt_objfn, &fakedata, *(settings));
  }
  else if (obj_fx_type.compare("bfgs") == 0) {
    return optim::bfgs(*init, opt_objfn, &fakedata, *(settings));
  }
  else
    throw std::runtime_error("Unknown optimizer type.");
}
