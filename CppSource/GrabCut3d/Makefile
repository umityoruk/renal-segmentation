opencv_lib_path = /opt/opencv/lib

all:
	g++ `pkg-config --cflags $(opencv_lib_path)/pkgconfig/opencv.pc` -std=c++11 run_grabcut3d.cpp grabcut3d.cpp umt.cpp `pkg-config --libs $(opencv_lib_path)/pkgconfig/opencv.pc` -Wl,-rpath,$(opencv_lib_path) -o run_grabcut3d
