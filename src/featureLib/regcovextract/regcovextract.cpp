/* Region Covariance feature extraction on a pyramid.
 */

#include <vector>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <string>
#include <algorithm>

#include <vigra/stdimage.hxx>
#include <vigra/copyimage.hxx>
#include <boost/program_options.hpp>

#include <assert.h>
#include <stdlib.h>
#include <math.h>

#include "DenseFeature.h"
#include "RegionCovariance.h"
#include "LBP.h"
#include "utility.h"
#include "ColorHistogram.h"
#include "EdgeHistogram.h"

namespace po = boost::program_options;

static int generate_features(const vigra::FVector3Image& image,
	unsigned int pyramid_levels, unsigned int pyramid_split,
	Features::DenseFeature* feat, std::vector<std::vector<double> >& X) {
	// Precompute
	feat->InitializeImage(image);

	// Extract pyramid, assume constant size descriptor
	unsigned int desc_len = feat->DescriptorSizeFromPixels(1, 1);
	for (unsigned int plevel = 0; plevel < pyramid_levels; ++plevel) {
		unsigned int win_div = pow(static_cast<double>(pyramid_split),
			static_cast<double>(plevel));
		unsigned int win_width = static_cast<unsigned int>(
			static_cast<double>(image.width()) / win_div);
		unsigned int win_height = static_cast<unsigned int>(
			static_cast<double>(image.height()) / win_div);

		// Must be an invariant-size feature
		assert(desc_len == static_cast<unsigned int>(
			feat->DescriptorSizeFromPixels(win_width, win_height)));
		for (unsigned int yi = 0; yi < win_div; ++yi) {
			for (unsigned int xi = 0; xi < win_div; ++xi) {
				std::vector<double> desc(desc_len);
				std::fill(desc.begin(), desc.end(), 0.0);
#if 0
				std::cout << "idx " << X.size() << std::endl;
				std::cout << "  (" << xi*win_width << "," << yi*win_height
					<< "), width " << win_width << ", height " << win_height
					<< std::endl;
#endif
				feat->ExtractDescriptor(image, xi * win_width, yi * win_height,
					win_width, win_height, desc);
				X.push_back(desc);
			}
		}
	}
	return (X.size());
}

int main(int argc, char **argv) {
	unsigned int pyramid_levels;
	unsigned int pyramid_split;
	std::string image_filename;
	std::string output_filename;
	std::string featuretype;

	po::options_description generic("Generic Options");
	generic.add_options()
		("help", "Produce help message")
		("verbose", "Verbose output")
		;

	po::options_description input_options("Input/Output Options");
	input_options.add_options()
		("image", po::value<std::string>
			(&image_filename)->default_value("input.png"),
			"The input image, PNG/JPEG/TIFF format.")
		("output", po::value<std::string>
			(&output_filename)->default_value("output.txt"),
			"The name of the file to store the generated features in")
		;

	po::options_description gen_options("Feature Options");
	gen_options.add_options()
		("type", po::value<std::string>(&featuretype)->default_value("regcov"),
			"Feature type to extract.  "
			"One of \"regcov\", \"regcov_image\" and \"lbp\".  "
			"\"regcov\" is the region covariance feature with per-subwindow "
			"normalization, \"regcov_image\" is the region covariance feature "
			"with per-image normalization and \"lbp\" is the local binary "
			"pattern feature.")
		("pyramid_levels", po::value<unsigned int>
			(&pyramid_levels)->default_value(3),
			"Number of pyramid levels.")
		("pyramid_split", po::value<unsigned int>
			(&pyramid_split)->default_value(2),
			"Splitting number for each pyramid level.")
		;

	// Parse options
	po::options_description all_options;
	all_options.add(generic).add(input_options).add(gen_options);
	po::variables_map vm;
	po::store(po::command_line_parser(argc, argv).options(all_options).run(), vm);
	po::notify(vm);

	if (vm.count("help")) {
		std::cerr << "regcovextract $Id: $" << std::endl;
		std::cerr << "===================================================="
			<< "===========================" << std::endl;
		std::cerr << "Copyright (C) 2008 -- "
			<< "Sebastian Nowozin <sebastian.nowozin@tuebingen.mpg.de>"
			<< std::endl;
		std::cerr << std::endl;
		std::cerr << "Usage: regcov [options]" << std::endl;
		std::cerr << std::endl;
		std::cerr << all_options << std::endl;

		exit(EXIT_SUCCESS);
	}

	// Load image
	vigra::FVector3Image image;
	bool success = Features::ImageLoader::LoadImage(image_filename, image, true);
	if (success == false) {
		std::cerr << "Failed to load image \"" << image_filename << "\"."
			<< std::endl;
		exit(EXIT_FAILURE);
	}

	// Produce pyramid and create features
	std::vector<std::vector<double> > X;
	Features::DenseFeature* feat = 0;
	if (featuretype == "regcov") {
		feat = new Features::RegionCovariance(false);
	} else if (featuretype == "regcov_image") {
		feat = new Features::RegionCovariance(true);
	} else if (featuretype == "lbp") {
		feat = new Features::LocalBinaryPattern;
	} else if (featuretype == "color") {
	  feat = new Features::ColorHistogram("rgb");
	} else if (featuretype == "edge") {
	  feat = new Features::EdgeHistogram;
	} else {
		std::cout << "Unsupported feature type \"" << featuretype << "\"." << std::endl;
		exit(EXIT_FAILURE);
	}
	unsigned int count = generate_features(image, pyramid_levels, pyramid_split,
		feat, X);
	std::cout << "Extracted " << count << " descriptors." << std::endl;
	delete feat;

	// Output features to file
	std::ofstream data_out(output_filename.c_str());
	if (data_out.fail()) {
		std::cerr << "Failed to open output file \"" << output_filename << "\"."
			<< std::endl;
		exit(EXIT_FAILURE);
	}
	data_out << std::setprecision(12);
	for (unsigned int n = 0; n < X.size(); ++n) {
		if (n > 0)
			data_out << std::endl;
		for (unsigned int ei = 0; ei < X[n].size(); ++ei) {
			if (ei > 0)
				data_out << " ";
			data_out << X[n][ei];
		}
	}
	data_out.close();
}



