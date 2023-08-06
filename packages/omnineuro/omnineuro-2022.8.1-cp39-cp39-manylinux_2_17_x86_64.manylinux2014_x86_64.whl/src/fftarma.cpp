#include <fftw3.h>
#include <armadillo>
#include <fftarma.h>
#include <memory>
#include <omp.h>


/***************************** 
  3D. 
*****************************/
arma::cx_cube fft(const arma::cube &X) {
  arma::cx_cube out(X.n_rows / 2 + 1, X.n_cols, X.n_slices);
  fftw_plan plan = fftw_plan_dft_r2c_3d(X.n_slices, X.n_cols, X.n_rows, (double *)X.memptr(), (fftw_complex *)out.memptr(), FFTW_ESTIMATE);
  fftw_execute(plan);
  fftw_destroy_plan(plan);
  out.resize(X.n_rows, X.n_cols, X.n_slices);
  // fill X redundant data.
  for(size_t i = X.n_rows / 2 + 1; i < X.n_rows; i++) {
    out(i,0,0) = std::conj(out(X.n_rows-i, 0, 0));
    for(size_t j = 1; j < X.n_cols; j++)
      out(i,j,0) = std::conj(out(X.n_rows-i, X.n_cols-j, 0));
    for(size_t k = 1; k < X.n_slices; k++)
      out(i,0,k) = std::conj(out(X.n_rows-i, 0, X.n_slices-k));
    for(size_t j = 1; j < X.n_cols; j++)
      for(size_t k = 1; k < X.n_slices; k++)
        out(i,j,k) = std::conj(out(X.n_rows-i, X.n_cols-j, X.n_slices-k));
  }
  return out;
}
arma::cube ifftr(const arma::cx_cube &X) {
  arma::cx_cube in = X(arma::span(0, X.n_rows / 2), arma::span(), arma::span());
  arma::cube ifft_data(X.n_rows, X.n_cols, X.n_slices);
  fftw_plan plan = fftw_plan_dft_c2r_3d(X.n_slices, X.n_cols, X.n_rows, (fftw_complex *)in.memptr(), ifft_data.memptr(), FFTW_ESTIMATE);
  fftw_execute(plan);
  fftw_destroy_plan(plan);
  return ifft_data/(X.n_rows * X.n_cols * X.n_slices);
}
arma::cx_cube fft(const arma::cx_cube &X) {
  arma::cx_cube fft_data(X.n_rows, X.n_cols, X.n_slices);
  fftw_plan plan = fftw_plan_dft_3d(X.n_slices, X.n_cols, X.n_rows, (fftw_complex *)X.memptr(), (fftw_complex *)fft_data.memptr(), FFTW_FORWARD, FFTW_ESTIMATE);
  fftw_execute(plan);
  fftw_destroy_plan(plan);
  return fft_data;
}
arma::cx_cube ifft(const arma::cx_cube &X) {
  arma::cx_cube ifft_data(X.n_rows, X.n_cols, X.n_slices);
  fftw_plan plan = fftw_plan_dft_3d(X.n_slices, X.n_cols, X.n_rows, (fftw_complex *)X.memptr(), (fftw_complex *)ifft_data.memptr(), FFTW_BACKWARD, FFTW_ESTIMATE);
  fftw_execute(plan);
  fftw_destroy_plan(plan);
  return ifft_data/(X.n_rows * X.n_cols * X.n_slices);
}

// Return center of cube (for convolutions)
// Assumes ref is smaller in dim compared to X
arma::cube centered(const arma::cube &X, const arma::cube &ref) {
  // we round up to match MATLAB's "same" argument
  int row = 0, col = 0, slice = 0;
  if ((X.n_rows - ref.n_rows) % 2 > 0)
    row = 1;
  if ((X.n_cols - ref.n_cols) % 2 > 0)
    col = 1;
  if ((X.n_slices - ref.n_slices) % 2 > 0)
    slice = 1;
  return X.subcube(
    (X.n_rows - ref.n_rows)/2 + row,
    (X.n_cols - ref.n_cols)/2 + col, 
    (X.n_slices - ref.n_slices)/2 + slice,
    (X.n_rows - ref.n_rows)/2 + row + ref.n_rows - 1,
    (X.n_cols - ref.n_cols)/2 + col + ref.n_cols - 1,
    (X.n_slices - ref.n_slices)/2 + slice + ref.n_slices - 1
  );
}

// Does convolution on X with kernel
// Output is centered (similar to MATLAB conv "same" argument)
arma::cube conv(arma::cube &X, arma::cube kernel) {
  // Setup threads
  fftw_init_threads();
  fftw_plan_with_nthreads(omp_get_max_threads());

  // Get padding size
  int padrow = X.n_rows + kernel.n_rows - 1;
  int padcol = X.n_cols + kernel.n_cols - 1;
  int padslice = X.n_slices + kernel.n_slices - 1;

  // Create a reference cube to go back to size of X after convolution
  arma::cube ref(X.n_rows, X.n_cols, X.n_slices); 

  // Create a copy of the cube to manipulate
  arma::cube mutX = arma::cube(X);

  // reshape each cube to padding size
  mutX.resize(padrow, padcol, padslice);
  kernel.resize(padrow, padcol, padslice);

  // apply fft, element wise multiply, ifft back, and center
  arma::cx_cube f = fft(mutX) % fft(kernel);
  return centered(ifftr(f), ref);
}

arma::cube conv_fast(arma::cube &X, arma::cube kernel) {
  // Setup threads
  fftw_init_threads();
  fftw_plan_with_nthreads(omp_get_max_threads());

  // reshape each cube to padding size
  kernel.resize(X.n_rows, X.n_cols, X.n_slices);

  // apply fft, element wise multiply, ifft back, and center
  arma::cx_cube f = fft(X) % arma::abs(fft(kernel));
  return ifftr(f);
}
