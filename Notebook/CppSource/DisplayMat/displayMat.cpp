#include <iostream>
#include <string>
#include <opencv.hpp>
#include "umt.hpp"


int main(int argc, char* argv[]) {
	if (argc != 3) {
		std::cout << "usage: displayMat input.umt output.umt" << std::endl;
		return -1;
	}

	std::string inputFilename = std::string(argv[1]);
	std::string outputFilename = std::string(argv[2]);

	// Read .umt file
	Umt* inputUmt = new Umt(inputFilename);
	uint8_t* dataIn = inputUmt->getData();
	std::vector<int> shapeIn = inputUmt->getShape();
	int ndims = shapeIn.size(); // vectorAxis + 2D + 3Channels = 4

	std::vector<cv::Mat> imgVec;

	for (int xx=0; xx<shapeIn[0]; xx++) {
		int loc = xx*shapeIn[1]*shapeIn[2]*3;
		cv::Mat img = cv::Mat(ndims-2, &shapeIn[1], CV_8UC3, (void*)(&dataIn[loc]));
		imgVec.push_back(img);
	}
	

	// cv::Mat subImage = image(cv::Range(0, 100), cv::Range::all());
	cv::Mat subImage = imgVec[25];

	cv::namedWindow("Display Image", cv::WINDOW_AUTOSIZE);
	cv::imshow("Display Image", subImage);

	cv::waitKey(0);

	delete inputUmt;

	Umt* outputUmt = new Umt();
	std::vector<int> shape;
	shape.push_back(5);
	shape.push_back(5);
	uint8_t* data = outputUmt->newData(shape);
	for (int ii=0; ii<25; ii++) {
		data[ii] = ii*2;
	}
	outputUmt->save(outputFilename);
	delete outputUmt;

	std::cout << "Success" << std::endl;
	return 0;
}
