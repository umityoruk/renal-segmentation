#include "umt.hpp"
#include <iostream>
#include <fstream>
#include <sstream>

Umt::Umt() {
	this->data = NULL;
}

Umt::Umt(const std::string &filename) {
	this->data = NULL;
	this->load(filename);
}

Umt::~Umt() {
	freeData();
}

void Umt::freeData() {
	if (this->data) {
		delete[] this->data;
		this->data = NULL;
	}
}

void Umt::load(const std::string &filename) {
	std::ifstream f;
	f.open(filename, std::ios::in | std::ios::binary);
	if (f.is_open()) {
		int ndim;
		f >> ndim;

		for (int ii=0; ii<ndim; ii++) {
			int num;
			f >> num;
			this->shape.push_back(num);
		}

		// Consume the rest of the line
		std::string line;
		std::getline(f, line);

		long long int dataSize = getDataSize();

		this->data = new uint8_t[dataSize];

		f.read((char*)this->data, dataSize);

		// for (int ii=0; ii<dataSize; ii++) {
		// 	std::cout << int(this->data[ii]) << " ";
		// }
		// std::cout << std::endl;

		f.close();
	}
	else {
		std::cout << "Unable to open file" << filename << std::endl;
	}
}

void Umt::save(const std::string &filename) {
	std::ofstream f;
	f.open(filename, std::ios::out | std::ios::binary);
	if (f.is_open()) {
		f << this->shape.size() << "\n";
		for (int ii=0; ii<this->shape.size(); ii++) {
			f << this->shape[ii] << " ";
		}
		f << "\n";

		long long int dataSize = getDataSize();
		f.write((char*)this->data, dataSize);
		f.close();
	}
	else {
		std::cout << "Unable to open file " << filename << std::endl;
	}
}

uint8_t* Umt::getData() {
	return this->data;
}

std::vector<int> Umt::getShape() {
	return this->shape;
}

uint8_t* Umt::newData(std::vector<int> shape) {
	freeData();

	this->shape = shape;
	long long int dataSize = getDataSize();
	this->data = new uint8_t[dataSize];
	
	return this->data;
}

long long int Umt::getDataSize() {
	long long int dataSize = 1;
	for (int ii=0; ii<this->shape.size(); ii++) {
		dataSize *= this->shape[ii];
	}
	return dataSize;
}