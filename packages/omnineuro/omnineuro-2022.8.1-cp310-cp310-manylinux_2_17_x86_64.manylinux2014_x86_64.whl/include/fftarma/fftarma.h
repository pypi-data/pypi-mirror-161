/*
  Header for fft functions
*/
#ifndef FFTARMA_H_
#define FFTARMA_H_

#include <armadillo>

/*****************************
  3D.
*****************************/
arma::cx_cube fft(const arma::cube &X);
arma::cube ifftr(const arma::cx_cube &X);
arma::cx_cube fft(const arma::cx_cube &X);
arma::cx_cube ifft(const arma::cx_cube &X);
// Return center of cube (for convolutions)
// Assumes ref is smaller in dim compared to X
arma::cube centered(const arma::cube &X, const arma::cube &ref);
// Does convolution on X with kernel
// Output is centered (similar to MATLAB conv "same" argument)
arma::cube conv(arma::cube &X, arma::cube kernel);
arma::cube conv_fast(arma::cube &X, arma::cube kernel);
#endif
