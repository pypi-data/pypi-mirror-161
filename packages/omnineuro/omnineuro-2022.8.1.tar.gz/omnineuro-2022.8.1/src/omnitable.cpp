/*
  Implementation of omnitable
*/
#include <omnitable.h>

// return image in table at name
OmniTable::shared_ptr_img OmniTable::return_img(string name) {
  // check if key exists (if it doesn't throw an exception)
  if (this->working_imgs.find(name) == this->working_imgs.end())
    throw std::runtime_error("Image does not exist in table");
  return this->working_imgs[name];
}

// save image into table at name
void OmniTable::save_img_at(string name, shared_ptr_img img) {
  // save the img at the specified name
  this->working_imgs[name] = img;
}

// Creates a blank image of the same size as the reference
// If manage is false (default), memory will not be managed by C++
// so user (or python) will need to delete the memory.
// When manage is true, a shared_ptr will be made to manage the
// image memory
OmniTable::shared_ptr_img OmniTable::make_img(shared_ptr_img reference, bool manage) {
  // define const double pointer
  const double* ptr; 
  
  // allocate memory for image
  if (manage) { // if true, C++ should manage the memory chunck on it's own with a shared_ptr
    // TODO: Figure out a way to automatically manage this transparently...
  }
  else { 
    ptr = new double[reference->shape[0]*reference->shape[1]*reference->shape[2]]();
  }

  // return Image
  // We use the affine attribute instead of the affine_ptr (which can apparently change arbitrarily)
  return std::make_shared<OmniTable::Image>(ptr,reference->shape,reference->stride,reference->affine->memptr());
}