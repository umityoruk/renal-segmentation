#include <iostream>
#include <string>
#include <opencv.hpp>
#include "umt.hpp"
#include "gcgraph.hpp"

void grabCut3d( std::vector<cv::Mat> &_img3d, std::vector<cv::Mat> &_mask3d, 
                  cv::InputOutputArray _bgdModel, cv::InputOutputArray _fgdModel,
                  int iterCount, int mode );

int main(int argc, char* argv[]) {
	if (argc != 4) {
		std::cout << "usage: run_grabcut3d input.umt mask.umt output.umt" << std::endl;
		return -1;
	}

	std::string inputFilename = std::string(argv[1]);
	std::string maskFilename = std::string(argv[2]);
	std::string outputFilename = std::string(argv[3]);

	// Read .umt files
	Umt* inputUmt = new Umt(inputFilename);
	Umt* maskUmt = new Umt(maskFilename);

	// Convert input to vector of cv::Mat
	uint8_t* dataIn = inputUmt->getData();
	std::vector<int> shapeIn = inputUmt->getShape();
	std::vector<cv::Mat> imgVec;
	for (int xx=0; xx<shapeIn[0]; xx++) {
		int loc = xx*shapeIn[1]*shapeIn[2]*3;  // 3Channels
		cv::Mat slice = cv::Mat(2, &shapeIn[1], CV_8UC3, (void*)(&dataIn[loc])); // 3Channels
		imgVec.push_back(slice);
	}

	// Convert mask to vector of cv::Mat
	uint8_t* dataMask = maskUmt->getData();
	std::vector<int> shapeMask = maskUmt->getShape();
	std::vector<cv::Mat> maskVec;
	for (int xx=0; xx<shapeMask[0]; xx++) {
		int loc = xx*shapeMask[1]*shapeMask[2]*1;  // 1Channel
		cv::Mat slice = cv::Mat(2, &shapeMask[1], CV_8UC1, (void*)(&dataMask[loc])); // 1Channel
		maskVec.push_back(slice);
	}
	
	// cv::Mat subImage = image(cv::Range(0, 100), cv::Range::all());
	// cv::Mat subImage = imgVec[28];

	// cv::namedWindow("Input Image", cv::WINDOW_AUTOSIZE);
	// cv::imshow("Input Image", subImage);

	// cv::waitKey(0);

	cv::Mat bgdModel, fgdModel;
	grabCut3d( imgVec, maskVec, bgdModel, fgdModel, 3, cv::GC_INIT_WITH_MASK);

	maskUmt->save(outputFilename);

	delete inputUmt;
	delete maskUmt;

	std::cout << "Success" << std::endl;
	return 0;
}