#include <string>
#include <vector>

class Umt {
private:
	uint8_t* data;
	std::vector<int> shape;
	void freeData();
	long long int getDataSize();
public:
	Umt();
	Umt(const std::string &filename);
	~Umt();
	void load(const std::string &filename);
	void save(const std::string &filename);
	uint8_t* getData();
	std::vector<int> getShape();
	uint8_t* newData(std::vector<int> shape);
};