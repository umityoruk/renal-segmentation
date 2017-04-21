#include <iostream>
#include "ucv_saturate.hpp"

using namespace std;

namespace ucv {
	template<typename _Tp, int m, int n> class Matx
	{
	public:
		enum { rows = m,
			   cols = n,
			   channels = rows*cols
		};
		_Tp data[m*n];

		// Default constructor
		Matx();

		// Constructor using existing array
		explicit Matx(const _Tp* vals);

		// Convenience methods
		static Matx all(_Tp val);
		static Matx zeros();
		static Matx ones();

		// Dot-product operations
		_Tp dot(const Matx<_Tp, m, n>& v) const;
		double ddot(const Matx<_Tp, m, n>& v) const;

		// Element-wise operations
		Matx<_Tp, m, n> operator+(const Matx<_Tp, m, n>& v) const;
		Matx<_Tp, m, n> operator-(const Matx<_Tp, m, n>& v) const;

		// Conversion to another data type
		template<typename T2> operator Matx<T2, m, n>() const;

		// Element access
		const _Tp& operator ()(int i, int j) const;
		_Tp& operator ()(int i, int j);

		// 1D Element access
		const _Tp& operator ()(int i) const;
		_Tp& operator ()(int i);

	};

	// Matx implementations
	template<typename _Tp, int m, int n> inline 
	Matx<_Tp, m, n>::Matx() {
		for(int i=0; i<channels; i++) data[i] = _Tp(0);
	}

	template<typename _Tp, int m, int n> inline 
	Matx<_Tp, m, n>::Matx(const _Tp* vals) {
		for(int i=0; i<channels; i++) data[i] = vals(i);
	}

	template<typename _Tp, int m, int n> inline 
	Matx<_Tp, m, n> Matx<_Tp, m, n>::all(_Tp val) {
		Matx<_Tp, m, n> M;
		for(int i=0; i<channels; i++) M.data[i] = val;
		return M;
	}

	template<typename _Tp, int m, int n> inline 
	Matx<_Tp, m, n> Matx<_Tp, m, n>::zeros() {
		return all(0);
	}

	template<typename _Tp, int m, int n> inline 
	Matx<_Tp, m, n> Matx<_Tp, m, n>::ones() {
		return all(1);
	}

	template<typename _Tp, int m, int n> inline 
	_Tp Matx<_Tp, m, n>::dot(const Matx<_Tp, m, n>& v) const {
		_Tp s = 0;
		for(int i=0; i<channels; i++) s += data[i]*v.data[i];
		return s;
	}

	template<typename _Tp, int m, int n> inline 
	double Matx<_Tp, m, n>::ddot(const Matx<_Tp, m, n>& v) const {
		double s = 0;
		for(int i=0; i<channels; i++) s += (double)data[i]*v.data[i];
		return s;
	}

	template<typename _Tp, int m, int n> inline 
	Matx<_Tp, m, n> Matx<_Tp, m, n>::operator+(const Matx<_Tp, m, n>& v) const {
		Matx<_Tp, m, n> M;
		for(int i=0; i<channels; i++) M.data[i] = saturate_cast<_Tp>(data[i] + v.data[i]);
		return M;
	}
	
	template<typename _Tp, int m, int n> inline 
	Matx<_Tp, m, n> Matx<_Tp, m, n>::operator-(const Matx<_Tp, m, n>& v) const {
		Matx<_Tp, m, n> M;
		for(int i=0; i<channels; i++) M.data[i] = saturate_cast<_Tp>(data[i] - v.data[i]);
		return M;
	}

	template<typename _Tp, int m, int n> template<typename T2> inline
	Matx<_Tp, m, n>::operator Matx<T2, m, n>() const
	{
		Matx<T2, m, n> M;
		for(int i=0; i<channels; i++) M.data[i] = saturate_cast<T2>(data[i]);
		return M;
	}

	template<typename _Tp, int m, int n> inline
	const _Tp& Matx<_Tp, m, n>::operator()(int i, int j) const {
		return this->data[i*n + j];
	}

	template<typename _Tp, int m, int n> inline
	_Tp& Matx<_Tp, m, n>::operator()(int i, int j) {
		return data[i*n + j];
	}

	template<typename _Tp, int m, int n> inline
	const _Tp& Matx<_Tp, m, n>::operator ()(int i) const {
		// CV_StaticAssert(m == 1 || n == 1, "Single index indexation requires matrix to be a column or a row");
		return data[i];
	}

	template<typename _Tp, int m, int n> inline
	_Tp& Matx<_Tp, m, n>::operator ()(int i) {
		// CV_StaticAssert(m == 1 || n == 1, "Single index indexation requires matrix to be a column or a row");
		return data[i];
	}
}


int main() {
	cout << "Hello World!" << endl;

	// Vec3d color;
	// for (int ii=0; ii<3; ii++) {
	// 	color[ii] = ii*ii;
	// }

	// for (int ii=0; ii<3; ii++) {
	// 	cout << color[ii] << " ";
	// }
	// cout << endl;

	return 0;
}