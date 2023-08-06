/*
  Implementation file for regression model
*/

#include <armadillo>
#include <cmath>
#include <vector>
#include <tuple>
#include <regression.h>
#include <assert.h>
#include <resample.h>
#include <omnitable.h>
#include <fftarma.h>

// Constructor
Regressor::Regressor(std::vector<shared_ptr_img> sources,
                     shared_ptr_img output,
                     shared_ptr_img blurred_output,
                     shared_ptr_img target,
                     string model,
                     shared_ptr_img target_mask,
                     shared_ptr_img source_mask,
                     shared_ptr_img regress_mask,
                     bool output_intmat,
                     bool use_kernel,
                     arma::cube blur_kernel):
                     sources(sources),
                     output(output),
                     blurred_output(blurred_output),
                     aligned_target(OmniTable::make_img(sources[0])),
                     resample(std::make_shared<Resampler>(sources[0], target, aligned_target, nullptr, nullptr, 3)),
                     regress_mask(regress_mask),
                     params(std::make_shared<arma::vec>()),
                     modelspec(model),
                     use_kernel(use_kernel),
                     blur_kernel(blur_kernel) {
    create_interaction_mat(modelspec, output_intmat);
}

template<typename T>
void print_vec(const std::vector<T>& v) {
  for (auto& i: v) {
    arma::cout << i << " ";
  }
  arma::cout << arma::endl;
}

// cut string 1
std::string cut_string(const std::string& to_parse, const std::string& end) {
  // get end string indices
  auto end_idx = to_parse.find(end);
  // return the cut string
  return to_parse.substr(0, end_idx);
}

// cut string 2
std::string cut_string2(const std::string& to_parse, const std::string& start, const std::string& end) {
  // get start/end string indices
  auto start_idx = to_parse.find(start);
  auto end_idx = to_parse.find(end);
  // return the cut string
  return to_parse.substr(start_idx+1,end_idx-1-start_idx);
}

// parse the string (specs are returned in reverse order)
std::vector<std::string> parse_string_reverse(const std::string& to_parse, const std::string& delimiter) {
  // get the spec
  std::string spec = cut_string(to_parse, delimiter);
  // create spec vector
  std::vector<std::string> spec_vec;
  if (to_parse.find(delimiter) != std::string::npos) // recursive call if not end of string
    spec_vec = parse_string_reverse(to_parse.substr(to_parse.find(delimiter)+1), delimiter); // get the next spec
  spec_vec.push_back(spec); // push the current spec to the vector
  return spec_vec;
}

// parse string function with forward order
std::vector<std::string> parse_string(const std::string& to_parse, const std::string& delimiter) {
  std::vector<std::string> spec_vec = parse_string_reverse(to_parse, delimiter); // get the reverse list
  std::reverse(spec_vec.begin(), spec_vec.end()); // reverse order
  return spec_vec; // return the spec vector
}

// given model, parse the kernel strings
std::vector<std::string> get_kernels(const std::string& model) {
  return parse_string(model, "+");
}

// given kernel string, parse pairwise interactions
std::vector<std::string> get_pairwise_interactions(const std::string& kernel) {
  return parse_string(kernel, "*");
}

// get kernel type
std::string get_kernel_type(const std::string& spec_term) {
  return cut_string(spec_term, "(");
}
// get kernel input
std::string get_kernel_input(const std::string& spec_term) {
  return cut_string2(spec_term, "(", ";");
}

// get the index of the source image input
int get_source_index(const std::string& spec_term) {
  return std::stoi(get_kernel_input(spec_term));
}

// get kernel parameters
std::string get_kernel_parameters(const std::string& spec_term) {
  return cut_string2(spec_term, ";", ")");
}

// get number of columns
int get_num_columns(const std::string& spec_term) {
  return std::stoi(get_kernel_parameters(spec_term));
}

// initialize interaction matrix
Regressor::shared_ptr_mat initialize_interaction_matrix(
  const std::vector<std::string>& kernels,
  Regressor::shared_ptr_img regress_mask, 
  const std::vector<arma::vec>& source_vecs,
  int& current_col) {
  // keep track of intercepts to check for duplicates
  std::vector<arma::uvec> intercepts;
  // initialize number of columns
  int number_of_columns = 0;
  int number_of_intercepts = 0;
  for (auto& kernel : kernels) {
    // get pairwise interactions for kernel
    std::vector<std::string> pairwise_interactions = get_pairwise_interactions(kernel);
    // for each pairwise interaction term for the kernel, get the number of columns
    int pairwise_cols = 1;
    for (auto& term : pairwise_interactions) {
      // get the kernel type for the term
      auto kernel_type = get_kernel_type(term);
      if (kernel_type.compare("rbf") == 0)
        pairwise_cols *= get_num_columns(term); // calc columns
      else if (kernel_type.compare("none") == 0)
        pairwise_cols *= 1; // just use 1 column
      else
        throw std::runtime_error("Unknown Kernel Type.");
      if (pairwise_interactions.size() == 1) { // if only one pairwise interaction get the intercept
        int source_index = get_source_index(term); // get the source index
        intercepts.push_back(source_vecs[source_index] > 0); // get intercept
        number_of_intercepts++;
      }
    }
    number_of_columns += pairwise_cols; // add to total columns
  }

  // check intercepts for duplicates
  std::vector<int> duplicates;
  for (int n = 0; n < number_of_intercepts; n++)
    for (int m = n+1; m < number_of_intercepts; m++)
      if (arma::sum(intercepts[n] - intercepts[m]) == 0)
        duplicates.push_back(m); // add duplicate index

  // remove duplicates from vector
  std::reverse(duplicates.begin(), duplicates.end());
  for (auto& d : duplicates)
    intercepts.erase(intercepts.begin() + d);
  
  // we need to model intercept of voxels in regress mask,
  // but not in either current intercepts
  arma::vec leftovers(arma::conv_to<arma::vec>::from(regress_mask->get_data_vec() > 0));
  for (auto& intercept : intercepts)
    leftovers -= arma::conv_to<arma::vec>::from(intercept);
  if (arma::sum(leftovers > 0) != 0) // add to intercepts if not all zeros
    intercepts.push_back((leftovers > 0));

  // add number of intercepts to columns
  number_of_columns += intercepts.size();

  // initialize matrix
  Regressor::shared_ptr_mat intmat(std::make_shared<arma::mat>(regress_mask->get_data_vec_size(), number_of_columns, arma::fill::ones));

  // initialize first few intercept columns
  for (auto& intercept : intercepts) {
    std::cout << "\rColumn: " << current_col+1 << "/" << number_of_columns << std::flush;
    intmat->col(current_col) = arma::conv_to<arma::vec>::from(intercept);
    current_col++; // go to next column
  }

  // return number of columns
  return intmat;
}

// slice array
template<typename T>
std::vector<T> slice(std::vector<T>& v)
{
    auto first = v.begin() + 1;
    auto last = v.end();
    std::vector<T> vec(first, last);
    return vec;
}

// rbf kernel function
arma::vec rbf_kernel(arma::vec& base, double center, double step) {
  return arma::exp(4*log(0.5)*arma::pow(base-center, 2)/pow(step, 2));
}

// calculate pairwise interactions
void calc_pairwise_interactions(
  Regressor::shared_ptr_mat interaction_mat,
  std::vector<arma::uvec>& intercept_masks,
  std::vector<arma::vec>& temp_vecs,
  std::vector<std::string> kernel_types,
  std::vector<arma::vec>& kernel_centers,
  std::vector<double>& kernel_steps,
  int& current_col, int& total_cols) {
    // get current values
    arma::uvec intercept_mask = intercept_masks.front();
    arma::vec temp_vec = temp_vecs.front();
    arma::vec centers = kernel_centers.front();
    std::string kernel_type = kernel_types.front();
    double step = kernel_steps.front();
    if (temp_vecs.size() == 1) { // base case
      // get the accumulated column
      arma::vec acol(interaction_mat->col(current_col));
      for (auto& center : centers) { // for each center
        std::cout << "\rColumn: " << current_col+1 << "/" << total_cols << std::flush;
        // multiply kernel by accumulated column + mask
        if (kernel_type.compare("rbf") == 0)
          interaction_mat->col(current_col) = (rbf_kernel(temp_vec, center, step) % acol) % intercept_mask;
        else if (kernel_type.compare("none") == 0)
          interaction_mat->col(current_col) = (temp_vec % acol) % intercept_mask;
        interaction_mat->col(current_col) /= interaction_mat->col(current_col).max(); // normalize to 1
        current_col++; // go to next column
      }
    }
    else { // general case
      for (auto& center : centers) { // for each center
        // element-wise multiply rbf kernel into matrix + mask
        if (kernel_type.compare("rbf") == 0)
          interaction_mat->col(current_col) %= rbf_kernel(temp_vec, center, step) % intercept_mask;
        else if (kernel_type.compare("none") == 0)
          interaction_mat->col(current_col) %= temp_vec % intercept_mask;
        // slice vectors for recursive call
        auto new_intercept_masks = slice(intercept_masks);
        auto new_temp_vecs = slice(temp_vecs);
        auto new_kernel_types = slice(kernel_types);
        auto new_kernel_centers = slice(kernel_centers);
        auto new_kernel_steps = slice(kernel_steps);
        // call pairwise interactions again
        calc_pairwise_interactions(interaction_mat, new_intercept_masks, new_temp_vecs, new_kernel_types,
          new_kernel_centers, new_kernel_steps, current_col, total_cols);
      }
    }
}

// .Create interation matrix from model spec
void Regressor::create_interaction_mat(string model, bool output_intmat) {
  arma::cout << "Building Interaction Matrix..." << arma::endl;
  // parse model
  std::vector<std::string> kernels = get_kernels(model);

  // Convert source images to arma vectors
  auto source_size = regress_mask->get_data_vec_size();
  std::vector<arma::vec> source_vecs;
  for (auto &s : sources) {
    assert(s->get_data_vec_size() == source_size); // assert regress mask and source images are same size
    source_vecs.push_back(arma::vec(s->ptr, s->get_data_vec_size()));
  }

  // Allocate interaction matrix
  int current_col = 0; // keep track of current column
  interaction_mat = initialize_interaction_matrix(kernels, regress_mask, source_vecs, current_col);
  int number_of_columns = interaction_mat->n_cols; // get total number of columns for interaction mat

  // if kernel enabled, create a blurred version
  blurred_interaction_mat = std::make_shared<arma::mat>(arma::size(*interaction_mat), arma::fill::zeros);

  // Now loop through the kernels vector and add each to the matrix
  for (auto& kernel : kernels) {
    std::vector<arma::uvec> intercept_masks; // vector for storing intercept masks
    std::vector<arma::vec> kernel_centers; // vector for storing arma vec of kernel centers
    std::vector<double> kernel_steps; // vector for storing arma vec of kernel centers
    std::vector<std::string> kernel_types; // vector for storing kernel types
    std::vector<arma::vec> temp_vecs; // create vector for storing temp vecs for pairwise interactions
    arma::vec temp_vec(regress_mask->get_data_vec_size(), arma::fill::ones); // temp vector for storing base column

    // Within each set of kernel terms, check for pairwise interactions
    auto pairwise_interactions = get_pairwise_interactions(kernel);

    // loop over each term in pairwise interactions
    for (auto& term : pairwise_interactions) {
      // Get the kernel type for the pairwise term
      auto kernel_type = get_kernel_type(term);
      kernel_types.push_back(kernel_type);

      // Get the source image index
      int source_index = get_source_index(term);

      // build temp vec
      temp_vec %= source_vecs[source_index];

      // generate intercept mask
      arma::uvec intercept_mask(temp_vec > 0);

      // store the intercept mask
      intercept_masks.push_back(intercept_mask);

      // store temp vec into vector
      temp_vecs.push_back(temp_vec);

      if (kernel_type.compare("rbf") == 0) { // rbf kernel type
        // Get the number of columns
        int num_kcolumns = get_num_columns(term);
        assert(num_kcolumns >= 2);

        // calculate kernel setup parameters from temp vector
        kernel_centers.push_back(arma::linspace(
          temp_vec.elem(arma::find(intercept_mask)).min(),
          temp_vec.elem(arma::find(intercept_mask)).max(),
          num_kcolumns)); // calculate centers
        kernel_steps.push_back(kernel_centers.back().at(1) - kernel_centers.back().at(0)); // calculate kernel step
      }
      else if (kernel_type.compare("none") == 0) { // none kernel type
        // just create a dummy kernel centers vector
        kernel_centers.push_back(arma::vec({0})); // Create a place holder kernel center vector
        kernel_steps.push_back(0); // calculate kernel step
      }
    }
    // calculate pairwise interactions for this term
    calc_pairwise_interactions(interaction_mat, intercept_masks, temp_vecs, kernel_types,
      kernel_centers, kernel_steps, current_col, number_of_columns);
  }
  std::cout << "\rColumn: " << current_col << "/" << number_of_columns << std::flush;
  arma::cout << arma::endl;
  arma::cout << "Finished Interaction Matrix Construction." << arma::endl;

  // if blur is enabled, apply blur to each column of the matrix
  if (use_kernel) {
    arma::cout << "Building Blurred Interaction Matrix..." << arma::endl;
    for (int c = 0; c < number_of_columns; c++) {
      std::cout << "\rColumn: " << c + 1 << "/" << number_of_columns << std::flush;
      arma::vec mat_col(interaction_mat->col(c));
      arma::cube col_img(
        mat_col.memptr(),
        output->get_data().n_rows,
        output->get_data().n_cols,
        output->get_data().n_slices
      );
      blurred_interaction_mat->col(c) = arma::vectorise(conv_fast(col_img, blur_kernel));
    }
    arma::cout << arma::endl;
    arma::cout << "Finished Blurred Interaction Matrix Construction." << arma::endl;
  }

  // output intmat if true
  if (output_intmat) {
    interaction_mat->save(arma::hdf5_name("intmat.h5", "intmat"));
    blurred_interaction_mat->save(arma::hdf5_name("blurred_intmat.h5", "blurred_intmat"));
  } 
}

// applies currently stored regression parameters to the interaction matrix
void Regressor::calc_output() {
  // apply regression parameters to interaction matrix 
  arma::vec array(*interaction_mat * *params);
  
  // convert to cube
  std::shared_ptr<arma::cube> data = std::make_shared<arma::cube>(
    array.memptr(), output->shape[0], output->shape[1], output->shape[2]);

  // store into output mask with regress mask and store in output
  output->data = data;
}

// applies currently stored regression parameters to the blurred interaction matrix
void Regressor::calc_blurred_output() {
  // apply regression parameters to interaction matrix 
  arma::vec array(*blurred_interaction_mat * *params);
  
  // convert to cube
  std::shared_ptr<arma::cube> data = std::make_shared<arma::cube>(
    array.memptr(), output->shape[0], output->shape[1], output->shape[2]);

  // store into output mask with regress mask and store in output
  blurred_output->data = data;
}

// calculate the regression parameters
void Regressor::calc_params(arma::mat& affine) {
  // invert the affine
  arma::mat inv_affine = arma::inv(affine);

  // Apply inverse transform to target and mask
  resample->apply_transform(inv_affine);
  
  // select the relevant voxels (only those greater than 0)
  arma::mat masked_interaction_mat;
  if (use_kernel)
    masked_interaction_mat = blurred_interaction_mat->rows(arma::find(regress_mask->get_data_vec() > 0));
  else
    masked_interaction_mat = interaction_mat->rows(arma::find(regress_mask->get_data_vec() > 0));
  arma::vec masked_target(aligned_target->get_data_vec().rows(arma::find(regress_mask->get_data_vec() > 0)));
  
  // get weights
  arma::vec weights = regress_mask->get_data_vec().rows(arma::find(regress_mask->get_data_vec() > 0));

  // solve for new parameters
  *params = arma::solve(arma::sqrt(weights) % masked_interaction_mat.each_col(), arma::sqrt(weights) % masked_target);
}