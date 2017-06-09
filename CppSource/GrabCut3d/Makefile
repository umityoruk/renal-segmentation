opencv_lib_path = /data3/umit-data/opencv/lib

all:
	g++ `pkg-config --cflags --libs $(opencv_lib_path)/pkgconfig/opencv.pc` -Wl,-rpath,$(opencv_lib_path) -std=c++0x run_grabcut3d.cpp grabcut3d.cpp umt.cpp -o run_grabcut3d
