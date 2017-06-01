all:
	g++ `pkg-config --cflags --libs opencv` -std=c++11 run_grabcut3d.cpp grabcut3d.cpp umt.cpp -o run_grabcut3d
no_opencv:
	g++ `pkg-config --cflags --libs opencv` -std=c++11 run_grabcut3d.cpp grabcut3d_no_opencv.cpp umt.cpp -o run_grabcut3d
