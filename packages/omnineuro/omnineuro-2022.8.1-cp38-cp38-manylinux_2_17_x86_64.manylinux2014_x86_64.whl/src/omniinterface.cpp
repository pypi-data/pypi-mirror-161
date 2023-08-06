/***
    Python/C++ interface for omnireg
***/
#include <cmath>
#include <chrono>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <omnitable.h>
#include <resample.h>
#include <optimize.h>
#include <regression.h>
#include <transform.h>
#include <stdexcept>

// use pybind shorthand
namespace py = pybind11;

// Interface class to call all other code
// Default arguments should be specified on the pybind interface, as pybind doesn't
// pass them by default from the C++ class
class Interface {
  public:
    Interface();
    Interface(const OmniTable::string&, py::array_t<double,py::array::f_style>&,
      py::array_t<double,py::array::f_style>&);
    void set_img(const OmniTable::string&, py::array_t<double,py::array::f_style>&,
      py::array_t<double,py::array::f_style>&);
    void resample(const OmniTable::string&, const OmniTable::string&, const OmniTable::string&,
      py::array_t<double,py::array::f_style>&);
    py::tuple registrate(const OmniTable::string&, std::vector<OmniTable::string>,
      const OmniTable::string&, const OmniTable::string&, const OmniTable::string&, const OmniTable::string&,
      py::array_t<double,py::array::f_style>&, py::array_t<double,py::array::f_style>&,
      const OmniTable::string&, int, const OmniTable::string&, const OmniTable::string&,
      const OmniTable::string&, double, double, int, bool, bool, bool, py::array_t<double,py::array::f_style>&);
    py::array_t<double> return_array(const OmniTable::string&);
  private:
    std::unique_ptr<OmniTable> archive;
    OmniTable::shared_ptr_img np_to_img(py::array_t<double,py::array::f_style>&,
      py::array_t<double,py::array::f_style>&);
};

// PYBIND INTERFACE
PYBIND11_MODULE(omni,m) {
  py::class_<Interface>(m,"Interface")
    .def(py::init<>())
    .def(py::init<const OmniTable::string&,
      py::array_t<double,py::array::f_style>&,
      py::array_t<double,py::array::f_style>&>())
    .def("set_img", &Interface::set_img)
    .def("resample", &Interface::resample)
    .def("registrate", &Interface::registrate,
      py::arg(), py::arg(), py::arg(), py::arg(), py::arg(), py::arg(), py::arg(), py::arg(), py::arg("optimizer") = "gd", py::arg("transcode") = 12,
      py::arg("target_mask") = "_NO_MASK_", py::arg("source_mask") = "_NO_MASK_", py::arg("regress_mask") = "_NO_MASK_",
      py::arg("step_size") = 1e-2, py::arg("err_tol") = 1e2, py::arg("iterations") = 200, py::arg("no_register") = false, py::arg("output_intmat") = false,
      py::arg("use_kernel") = false, py::arg("blur_kernel") = py::none())
    .def("return_array", &Interface::return_array);
}

// Interface constructor (initialize the omnitable)
Interface::Interface() : archive(std::make_unique<OmniTable>()) {}

// Interface constructor 2 (set the image on object contruction)
Interface::Interface(const OmniTable::string& name, py::array_t<double,py::array::f_style>& input,
  py::array_t<double,py::array::f_style>& affine) : Interface() {
    this->set_img(name, input, affine);
}

// set image at name
void Interface::set_img(const OmniTable::string& name, py::array_t<double,py::array::f_style>& input,
  py::array_t<double,py::array::f_style>& affine) {
    this->archive->save_img_at(name, this->np_to_img(input,affine));
}

// resample image
void Interface::resample(const OmniTable::string& target, const OmniTable::string& source,
  const OmniTable::string& output, py::array_t<double,py::array::f_style>& affine) {
    // grab image pointers
    OmniTable::shared_ptr_img target_img = this->archive->return_img(target);
    OmniTable::shared_ptr_img source_img = this->archive->return_img(source);

    // grab the affine transform and store in mat
    arma::mat::fixed<4,4> affine_mat(reinterpret_cast<double*>(affine.request().ptr));

    // allocate memory for output img
    OmniTable::shared_ptr_img output_img = OmniTable::make_img(target_img);

    // Construct resampler
    std::shared_ptr<Resampler> r = std::make_shared<Resampler>(target_img, source_img, output_img);

    // apply affine matrix
    r->apply_transform(affine_mat);

    // get the output and store in table
    archive->save_img_at(output, r->output);
}

py::tuple Interface::registrate(const OmniTable::string& target,
                                std::vector<OmniTable::string> sources,
                                const OmniTable::string& regressed,
                                const OmniTable::string& blurred_regressed,
                                const OmniTable::string& aligned,
                                const OmniTable::string& modelspec,
                                py::array_t<double,py::array::f_style>& affine,
                                py::array_t<double,py::array::f_style>& fixed_regress,
                                const OmniTable::string& optimizer_type,
                                int transcode,
                                const OmniTable::string& target_mask,
                                const OmniTable::string& source_mask,
                                const OmniTable::string& regress_mask,
                                double step_size,
                                double err_tol,
                                int iterations,
                                bool no_register,
                                bool output_intmat,
                                bool use_kernel,
                                py::array_t<double,py::array::f_style>& blur_kernel) {
    // grab image pointers
    OmniTable::shared_ptr_img target_img = archive->return_img(target);
    // grab all the source images
    std::vector<OmniTable::shared_ptr_img> source_imgs;
    std::transform(sources.begin(), sources.end(), std::back_inserter(source_imgs),
      [this](OmniTable::string s) -> OmniTable::shared_ptr_img { return this->archive->return_img(s); });
    
    // if not mask just create an image of ones the size of the target
    OmniTable::shared_ptr_img target_mask_img;
    if (target_mask.compare("_NO_MASK_") == 0) {
      target_mask_img = OmniTable::make_img(target_img);
      target_mask_img->data->fill(1);
    }
    else
      target_mask_img = archive->return_img(target_mask);

    // if not mask just create an image of ones the size of the source
    OmniTable::shared_ptr_img source_mask_img;
    if (source_mask.compare("_NO_MASK_") == 0) {
      source_mask_img = OmniTable::make_img(source_imgs[0]);
      source_mask_img->data->fill(1);
    }
    else
      source_mask_img = archive->return_img(source_mask);

    // if not mask just create an image of ones the size of the target
    OmniTable::shared_ptr_img regress_mask_img;
    if (regress_mask.compare("_NO_MASK_") == 0) {
      regress_mask_img = OmniTable::make_img(source_imgs[0]);
      regress_mask_img->data->fill(1);
    }
    else
      regress_mask_img = archive->return_img(regress_mask);

    // allocate memory for output img and regressed img
    OmniTable::shared_ptr_img aligned_img = OmniTable::make_img(target_img);
    OmniTable::shared_ptr_img regressed_img = OmniTable::make_img(source_imgs[0]);
    OmniTable::shared_ptr_img blurred_regressed_img = OmniTable::make_img(source_imgs[0]);

    // grab the initial affine transform and store in mat
    arma::mat::fixed<4,4> affine_mat(reinterpret_cast<double*>(affine.request().ptr));

    // check if fixed regress params set
    bool use_fixed_params = false;
    arma::vec fixed_regress_params(reinterpret_cast<double*>(fixed_regress.request().ptr), fixed_regress.request().shape[0]);
    if ( fixed_regress_params.n_rows > 1 ) {
      arma::cout << "Using fixed params..." << arma::endl;
      use_fixed_params = true;
    }

    // Create a Regressor and Transform object depending on if kernel is used
    std::shared_ptr<Regressor> regress;
    std::shared_ptr<Transformer> transform;
    if (use_kernel) {
      arma::cube kernel_cube(
        reinterpret_cast<double*>(blur_kernel.request().ptr),
        blur_kernel.request().shape[0],
        blur_kernel.request().shape[1],
        blur_kernel.request().shape[2]
      );
      regress = std::make_shared<Regressor>(
        source_imgs, regressed_img, blurred_regressed_img, target_img, modelspec, target_mask_img, source_mask_img, regress_mask_img, output_intmat, use_kernel, kernel_cube);
      transform =std::make_shared<Transformer>(target_img, blurred_regressed_img, aligned_img, target_mask_img, source_mask_img, affine_mat, transcode);
    }
    else {
      regress = std::make_shared<Regressor>(
        source_imgs, regressed_img, blurred_regressed_img, target_img, modelspec, target_mask_img, source_mask_img, regress_mask_img, output_intmat);
      transform =std::make_shared<Transformer>(target_img, regressed_img, aligned_img, target_mask_img, source_mask_img, affine_mat, transcode);
    }

    // Create optimizer (pass in the objective function as a lambda)
    auto optimizer = std::make_unique<Optimizer>(
      optimizer_type,
      step_size,
      err_tol,
      iterations,
      [
            &transform,
            &regress,
            &no_register,
            &use_fixed_params,
            &fixed_regress_params,
            &use_kernel
      ](
        const arma::vec& params,
        arma::vec* grad_out,
        void* unused
      ) -> double {
        // Time function call
        auto t1 = std::chrono::high_resolution_clock::now();

        // Convert the affine vec to a matrix
        arma::mat affine = transform->params_to_affine(params);

        // save gradient norm
        double grad_norm = -1;

        // Recalculate regression parameters and image if needed
        if (grad_out) {
          if (use_fixed_params) { // use user specified parameters
            *(regress->params) = fixed_regress_params;
          }
          else { // calculate the parameters
            // Get the regression parameters
            regress->calc_params(affine);
          }

          // calculate regressed image
          if (use_kernel)
            regress->calc_blurred_output();
          else
            regress->calc_output();
        }

        // calculate the residual term
        transform->calc_residual(affine, true);

        // only when algorithm needs gradient
        if (grad_out) {
          // if no_register set to true, we force the gradient to be 0 to skip registration
          if (no_register) {
            grad_out->zeros();
            grad_norm = 0;
          }
          else { // calculate affine gradient          
            // Calculate the registration gradient
            transform->calc_gradient(grad_out, affine, transform->residual);
            
            arma::cout << "Gradient: " << arma::endl;
            arma::cout << grad_out->as_row() << arma::endl;

            // get the gradient norm
            grad_norm = arma::norm(*grad_out, 2);
          }
        }

        // return objective function value
        double error = pow(arma::norm(transform->residual->get_data_vec()),2)/(2*transform->target_size);
        auto t2 = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
        arma::cout << "Iteration Duration (ms): " << duration << ", Error: " << error << ", Gradient Norm: " << grad_norm << arma::endl;
        arma::cout << "Affine Parameters: " << arma::endl;
        arma::cout << affine << arma::endl;
        arma::cout << "Regression Parameters: " << arma::endl;
        arma::cout << regress->params->as_row() << arma::endl;
        return error;
    });

    // Run optimizer on transform parameters
    auto t1 = std::chrono::high_resolution_clock::now(); // time optimization
    bool success = optimizer->run(transform->params);
    auto t2 = std::chrono::high_resolution_clock::now(); // end time
    std::chrono::duration<double> duration = t2 - t1; // duration
    arma::cout << "Total Duration: " << duration.count() << " seconds" << arma::endl; 
    arma::cout << "Converged: " << (success ? "true" : "false") << arma::endl;

    // Do a final update of regression (if kernel on)
    if (use_kernel)
      regress->calc_output();

    // Convert the affine vec to a matrix
    arma::mat new_affine = transform->params_to_affine(*(transform->params));
    arma::cout << new_affine << arma::endl;
    arma::cout << regress->params->as_row() << arma::endl;

    // save output
    archive->save_img_at(regressed, regressed_img);
    archive->save_img_at(blurred_regressed, blurred_regressed_img);
    archive->save_img_at(aligned, aligned_img);

    // free memory held by temp images
    // TODO: Make this automatic
    transform->gradient_x->free_mem();
    transform->gradient_y->free_mem();
    transform->gradient_z->free_mem();
    transform->residual->free_mem();
    regress->aligned_target->free_mem();

    // make numpy arrays of affine and regression parameters
    py::array_t<double> np_affine = py::array_t<double>(
      {4,4},
      {sizeof(double),sizeof(double)*4},
      new_affine.memptr(),
      py::object()
    );
    py::array_t<double> np_params = py::array_t<double>(
      {regress->params->n_elem},
      {sizeof(double)},
      regress->params->memptr(),
      py::object()
    );

    // return tuple
    return py::make_tuple(np_affine, np_params);
}

// return working image
py::array_t<double> Interface::return_array(const OmniTable::string& name) {
  // return the array of the working image
  return py::array_t<double>(
    archive->return_img(name)->shape,
    archive->return_img(name)->stride,
    archive->return_img(name)->data->memptr(),
    py::object()
  );
}

// convert numpy to img ptr
OmniTable::shared_ptr_img Interface::np_to_img(py::array_t<double,py::array::f_style>& input,
  py::array_t<double,py::array::f_style>& affine) {
    return std::make_shared<OmniTable::Image>(
      reinterpret_cast<const double*>(input.request().ptr),
      input.request().shape,
      input.request().strides,
      reinterpret_cast<const double*>(affine.request().ptr));
}
