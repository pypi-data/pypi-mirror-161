/*
    Implementation for transform class
*/

#include <transform.h>
#include <memory>
#include <armadillo>
#include <omnitable.h>

// Constructor for transformer class
Transformer::Transformer(shared_ptr_img target,
                         shared_ptr_img source,
                         shared_ptr_img output,
                         shared_ptr_img target_mask,
                         shared_ptr_img source_mask,
                         arma::mat& affine_mat,
                         int transcode) :
                         gradient_x(OmniTable::make_img(target)), // allocate memory for gradient images
                         gradient_y(OmniTable::make_img(target)),
                         gradient_z(OmniTable::make_img(target)),
                         residual(OmniTable::make_img(target)), // allocate memory for residual image
                         resample(std::make_shared<Resampler>(target, source, output, nullptr, nullptr, 3)), // initialize a resampler object
                         affine_grad(target->shape[0]*target->shape[1]*target->shape[2], 4, arma::fill::zeros), // allocate memory for affine gradient
                         target_size(arma::sum(target_mask->get_data_vec() > 0 )), // calculate target size 
                         target(target), // store image inputs
                         source(source),
                         output(output),
                         target_mask(target_mask)
{
  // select the transformation type
  switch (transcode) {
    case 3: // Just the three translation values
      params_to_affine = param_3_affine;
      params_gradient = param_3_gradient;
      params = std::make_shared<arma::vec>(
        std::initializer_list<double>{0,0,0});
      num_params = 3;
      break;
    case 6: // This uses quaternions so it's actually 7 instead of 6
      params_to_affine = param_6_affine;
      params_gradient = param_6_gradient;
      params = std::make_shared<arma::vec>(
        std::initializer_list<double>{0,0,0,1,0,0,0});
      num_params = 7;      
      break;
    case 9: // This uses quaternions so it's actually 10 instead of 9
      params_to_affine = param_9_affine;
      params_gradient = param_9_gradient;
      params = std::make_shared<arma::vec>(
        std::initializer_list<double>{0,0,0,1,0,0,0,1,1,1});
      num_params = 10;      
      break;
    case 12: // This just uses a flattened affine matrix minus last row
      params_to_affine = param_12_affine;
      params_gradient = param_12_gradient;
      params = std::make_shared<arma::vec>(
        arma::vectorise(affine_mat.submat(0,0,2,3),1).t());
      num_params = 12;
      break;
    default:
      throw std::runtime_error("Invalid parameter number selection");
      break;
    }
}

// Calculates the derivative of the MSE objective function wrt to the transformed image
// TODO: Implement for other objective functions
void Transformer::calc_residual(arma::mat affine, bool reinitialize) {
  // Get proposed output image with current affine
  // This uses the resampler object that the Transformer object creates
  // to apply the affine to the output image. Since all images are pointers,
  // changes are propagated as long as you have a reference to the image
  // i.e. the pointer to the output image.
  if (reinitialize)
    resample->initialize(); // Reset the interpolator with the updated source image
  resample->apply_transform(affine);
  
  // Save data in residual (difference and images with mask applied)
  *(residual->data) = (output->get_data() - target->get_data()) % target_mask->get_data();
}

// Returns the gradient to the gradient pointer for optimlib optimizers
// The index parameter sets the first index of the grad_out vector where the gradient
// terms should be written out to
// TODO: This only works with 12 param affine. Make compatible with other number of affine parameters
void Transformer::calc_gradient(arma::vec* grad_out, arma::mat affine, shared_ptr_img residual, int index) {
  // Calculate the affine gradient
  params_gradient(target,affine, affine_grad);

  // get image gradients
  Transformer::image_gradient(output, gradient_x, gradient_y, gradient_z);  
  
  // Combine gradients
  for (auto i=0; i<4; i++) {
    grad_out->at(index+i) = arma::dot(residual->get_data_vec(), gradient_x->get_data_vec() % affine_grad.col(i))/target_size;
    grad_out->at(index+i+4) = arma::dot(residual->get_data_vec(), gradient_y->get_data_vec() % affine_grad.col(i))/target_size;
    grad_out->at(index+i+8) = arma::dot(residual->get_data_vec(), gradient_z->get_data_vec() % affine_grad.col(i))/target_size;
  }
}

// Calculate the image gradient
void Transformer::image_gradient(shared_ptr_img img,
                                 shared_ptr_img gradient_x,
                                 shared_ptr_img gradient_y,
                                 shared_ptr_img gradient_z) {
  // Get image dims
  const auto& max_k = img->shape[2];
  const auto& max_j = img->shape[1];
  const auto& max_i = img->shape[0];

  // Calculate finite difference of gradient for each direction (non-boundary)
  for (auto k = 1; k<max_k-1; k++) {
    for (auto j = 1; j<max_j-1; j++) {
      for (auto i = 1; i<max_i-1; i++) {
        // gradient x
        gradient_x->data->at(i,j,k) = 
          (img->data->at(i+1,j,k) - img->data->at(i-1,j,k))/(2*(img->affine->at(0,0)));
        // gradient y
        gradient_y->data->at(i,j,k) = 
          (img->data->at(i,j+1,k) - img->data->at(i,j-1,k))/(2*(img->affine->at(1,1)));
        // gradient z
        gradient_z->data->at(i,j,k) = 
          (img->data->at(i,j,k+1) - img->data->at(i,j,k-1))/(2*(img->affine->at(2,2)));
      }
    }
  }
  /* Calculate gradient at the boundary using the Neumann Boundary Condition.
    This specifies that any voxel outside the image should have a gradient equal to 0.
    Another way of looking at this condition is to assume that any outlier voxel assumes the 
    value of the closest voxel on the edge of the volume. For example:

      * * * * * *
      * * * * * *
      * 1 2 3 4 5  (where * denotes voxels that lie
      * 3 3 5 5 6          outside of the image boundary)
      * 4 4 6 7 8

      will be:

      1 1 1 2 3 4 5
      1 1 1 2 3 4 5
      1 1 1 2 3 4 5
      3 3 3 3 5 5 6   (note the corner values)
      4 4 4 4 6 7 8

  */
  // TODO: Come up with cleaner implementation?
  // x boundary
  int i_i, i_f, j_i, j_f, k_i, k_f;
  for (auto k = 0; k<max_k; k++) {
    for (auto j = 0; j<max_j; j++) {
      gradient_x->data->at(0,j,k) = (img->data->at(1,j,k) - img->data->at(0,j,k))/(2*(img->affine->at(0,0)));
      gradient_x->data->at(max_i-1,j,k) = (img->data->at(max_i-1,j,k) - img->data->at(max_i-2,j,k))/(2*(img->affine->at(0,0)));
      if (j==0) {
        j_f = j+1;
        j_i = j; 
      }
      else if (j==max_j-1) {
        j_f = j;
        j_i = j-1;
      }
      else {
        j_f = j+1;
        j_i = j-1;
      }
      if (k==0) {
        k_f = k+1;
        k_i = k;
      } 
      else if (k==max_k-1) {
        k_f = k;
        k_i = k-1;
      }
      else {
        k_f = k+1;
        k_i = k-1;
      }
      gradient_y->data->at(0,j,k) = (img->data->at(0,j_f,k) - img->data->at(0,j_i,k))/(2*(img->affine->at(1,1)));
      gradient_y->data->at(max_i-1,j,k) = (img->data->at(max_i-1,j_f,k) - img->data->at(max_i-1,j_i,k))/(2*(img->affine->at(1,1)));
      gradient_z->data->at(0,j,k) = (img->data->at(0,j,k_f) - img->data->at(0,j,k_i))/(2*(img->affine->at(2,2)));
      gradient_z->data->at(max_i-1,j,k) = (img->data->at(max_i-1,j,k_f) - img->data->at(max_i-1,j,k_i))/(2*(img->affine->at(2,2)));
    }
  }
  // y boundary
  for (auto k = 0; k<max_k; k++) {
    for (auto i = 0; i<max_i; i++) {
      gradient_y->data->at(i,0,k) = (img->data->at(i,1,k) - img->data->at(i,0,k))/(2*(img->affine->at(1,1)));
      gradient_y->data->at(i,max_j-1,k) = (img->data->at(i,max_j-1,k) - img->data->at(i,max_j-2,k))/(2*(img->affine->at(1,1)));
      if (i==0) {
        i_f = i+1;
        i_i = i;
      }
      else if (i==max_i-1) {
        i_f = i;
        i_i = i-1;
      }
      else {
        i_f = i+1;
        i_i = i-1;
      }
      if (k==0) {
        k_f = k+1;
        k_i = k;
      } 
      else if (k==max_k-1) {
        k_f = k;
        k_i = k-1;
      }
      else {
        k_f = k+1;
        k_i = k-1;
      }
      gradient_x->data->at(i,0,k) = (img->data->at(i_f,0,k) - img->data->at(i_i,0,k))/(2*(img->affine->at(0,0)));
      gradient_x->data->at(i,max_j-1,k) = (img->data->at(i_f,max_j-1,k) - img->data->at(i_i,max_j-1,k))/(2*(img->affine->at(0,0)));
      gradient_z->data->at(i,0,k) = (img->data->at(i,0,k_f) - img->data->at(i,0,k_i))/(2*(img->affine->at(2,2)));
      gradient_z->data->at(i,max_j-1,k) = (img->data->at(i,max_j-1,k_f) - img->data->at(i,max_j-1,k_i))/(2*(img->affine->at(2,2)));
    }
  }
  // z boundary
  for (auto j = 0; j<max_j; j++) {
    for (auto i = 0; i<max_i; i++) {
      gradient_z->data->at(i,j,0) = (img->data->at(i,j,1) - img->data->at(i,j,0))/(2*(img->affine->at(2,2)));
      gradient_z->data->at(i,j,max_k-1) = (img->data->at(i,j,max_k-1) - img->data->at(i,j,max_k-2))/(2*(img->affine->at(2,2)));
      if (i==0) {
        i_f = i+1;
        i_i = i;
      }
      else if (i==max_i-1) {
        i_f = i;
        i_i = i-1;
      }
      else {
        i_f = i+1;
        i_i = i-1;
      }
      if (j==0) {
        j_f = j+1;
        j_i = j; 
      }
      else if (j==max_j-1) {
        j_f = j;
        j_i = j-1;
      }
      else {
        j_f = j+1;
        j_i = j-1;
      }
      gradient_x->data->at(i,j,0) = (img->data->at(i_f,j,0) - img->data->at(i_i,j,0))/(2*(img->affine->at(0,0)));
      gradient_x->data->at(i,j,max_k-1) = (img->data->at(i_f,j,max_k-1) - img->data->at(i_i,j,max_k-1))/(2*(img->affine->at(0,0)));
      gradient_y->data->at(i,j,0) = (img->data->at(i,j_f,0) - img->data->at(i,j_i,0))/(2*(img->affine->at(1,1)));
      gradient_y->data->at(i,j,max_k-1) = (img->data->at(i,j_f,max_k-1) - img->data->at(i,j_i,max_k-1))/(2*(img->affine->at(1,1)));
    }
  }
}

// 12 parameter gradient
void Transformer::param_12_gradient(shared_ptr_img target, arma::mat affine, arma::mat& affine_grad) {
  // NOTE: affine here is the inverse affine (in other words, from target --> source grid)
  
  // Create iterators
  int v = 0;
  std::vector<double>::iterator x_it;
  std::vector<double>::iterator y_it;
  std::vector<double>::iterator z_it;

  // Get the grid mat to "unpositify" the grid
  const auto& gm = target->grid_mat;

  // For each position in the target, get the position in the source image using the affine transform
  for (z_it = target->z->begin(); z_it != target->z->end(); ++z_it) {
    for (y_it = target->y->begin(); y_it != target->y->end(); ++y_it) {
      for (x_it = target->x->begin(); x_it != target->x->end(); ++x_it) {
        affine_grad.at(v,0) = (*(x_it))*gm->at(0,0)*affine.at(0,0) + (*(y_it))*gm->at(1,1)*affine.at(0,1) + (*(z_it))*gm->at(2,2)*affine.at(0,2) + affine.at(0,3);
        affine_grad.at(v,1) = (*(x_it))*gm->at(0,0)*affine.at(1,0) + (*(y_it))*gm->at(1,1)*affine.at(1,1) + (*(z_it))*gm->at(2,2)*affine.at(1,2) + affine.at(1,3);
        affine_grad.at(v,2) = (*(x_it))*gm->at(0,0)*affine.at(2,0) + (*(y_it))*gm->at(1,1)*affine.at(2,1) + (*(z_it))*gm->at(2,2)*affine.at(2,2) + affine.at(2,3);
        v++; // increment the row
      }
    }
  }

  // Fill the last column with ones (the translation part of affine transform)
  affine_grad.col(3).fill(1);
}

// TODO
// 9 parameter gradient
void Transformer::param_9_gradient(shared_ptr_img target, arma::mat affine, arma::mat& affine_grad) {}

// TODO
// 6 parameter gradient
void Transformer::param_6_gradient(shared_ptr_img target, arma::mat affine, arma::mat& affine_grad) {}

// 3 parameter gradient
void Transformer::param_3_gradient(shared_ptr_img target, arma::mat affine, arma::mat& affine_grad) {
  // Since affine is the same but only translations we can just use the 12 parameter gradient call
  param_12_gradient(target, affine, affine_grad);
}

// 12 parameter affine transform
arma::mat Transformer::param_12_affine(arma::vec affine_vec) {
  // convert 12 parameter transform to matrix
  arma::mat affine;
  affine.insert_cols(0,affine_vec);
  affine.reshape(4,4);
  arma::inplace_trans(affine);
  affine.at(3,3) = 1; // add corner
  return affine;
}

// 9 parameter transform
// TODO
arma::mat Transformer::param_9_affine(arma::vec affine_vec) {
  return arma::mat();
}

// 6 parameter rigid body transform
// TODO
arma::mat Transformer::param_6_affine(arma::vec affine_vec) {
  return arma::mat();
}

// 3 parameter translation transform
arma::mat Transformer::param_3_affine(arma::vec affine_vec) {
  // convert 3 parameter transform to matrix
  arma::mat affine(4,4,arma::fill::eye);
  // insert translations
  affine.submat(0,3,2,3) = affine_vec;
  arma::cout << affine << arma::endl;
  return affine;
}
