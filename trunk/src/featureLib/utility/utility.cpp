/* Utility code
 *
 * Copyright (C) 2007 -- Sebastian Nowozin <nowozin@gmail.com>
 */

#include <iostream>

#include "utility.h"

namespace Features {

bool ImageLoader::LoadImage(const std::string& filename,
	vigra::FVector3Image& image, bool verbose) {
	vigra::ImageImportInfo info(filename.c_str());
	vigra::Size2D isize = info.size();
	if (verbose) {
		std::cerr << info.getFileType() << " image "
			<< isize.width() << "x" << isize.height()
			<< " " << (info.isGrayscale() ? "gray" : "")
			<< (info.isColor() ? "color" : "")
			<< ", " << info.numBands() << "(+"
			<< info.numExtraBands() << ") bands, pixeltype \""
			<< info.getPixelType() << "\"" << std::endl;
	}

	image.resize(info.width(), info.height());
	vigra::FVector4Image image4;
	vigra::FImage image1;
	if (info.isGrayscale()) {
		// Duplicate gray plane to RGB
		image1.resize(isize.width(), isize.height());
		vigra::importImage(info, vigra::destImage(image1));
		vigra::FImage::Iterator sy = image1.upperLeft();
		vigra::FImage::Iterator sy_end = image1.lowerRight();
		vigra::FVector3Image::Iterator dy = image.upperLeft();
		vigra::FVector3Image::Iterator dy_end = image.lowerRight();
		for ( ; sy.y != sy_end.y; ++sy.y, ++dy.y) {
			vigra::FImage::Iterator sx = sy;
			vigra::FVector3Image::Iterator dx = dy;
			for ( ; sx.x != sy_end.x; ++sx.x, ++dx.x)
				for (int i = 0; i < 3; ++i)
					(*dx)[i] = (*sx);
		}
	} else {
		switch (info.numBands()) {
		case (4):
			{
				image4.resize(isize.width(), isize.height());
				vigra::importImage(info, vigra::destImage(image4));
				vigra::FVector4Image::Iterator sy = image4.upperLeft();
				vigra::FVector4Image::Iterator sy_end = image4.lowerRight();
				vigra::FVector3Image::Iterator dy = image.upperLeft();
				vigra::FVector3Image::Iterator dy_end = image.lowerRight();
				for ( ; sy.y != sy_end.y; ++sy.y, ++dy.y) {
					vigra::FVector4Image::Iterator sx = sy;
					vigra::FVector3Image::Iterator dx = dy;
					for ( ; sx.x != sy_end.x; ++sx.x, ++dx.x) {
						for (int i = 0; i < 3; ++i)
							(*dx)[i] = (*sx)[i];
					}
				}
			}
			break;
		case (3):
			vigra::importImage(info, vigra::destImage(image));
			break;
		default:
			return (false);
		}
	}
	return (true);
}

}

