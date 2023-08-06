/*
  Header for Image object hash table
  Used for storing and operating on images
*/
#ifndef OMNITABLE_H_
#define OMNITABLE_H_

#include <omniimg.h>

#include <memory>
#include <string>
#include <unordered_map>

class OmniTable {
   public:
    using Image = omniimg::Image;
    using shared_ptr_img = std::shared_ptr<Image>;
    using size_vec = omniimg::Image::size_vec;
    using shared_ptr_double = omniimg::Image::shared_ptr_double;
    using string = std::string;
    void save_img_at(string, shared_ptr_img);
    shared_ptr_img return_img(string);
    static shared_ptr_img make_img(shared_ptr_img, bool = false);

   private:
    std::unordered_map<string, shared_ptr_img> working_imgs;
};

#endif
