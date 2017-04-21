/*
Copied from OpenCV implementation of Grabcut.
Extended for 3D 3-channel inputs.
*/

/*M///////////////////////////////////////////////////////////////////////////////////////
//
//  IMPORTANT: READ BEFORE DOWNLOADING, COPYING, INSTALLING OR USING.
//
//  By downloading, copying, installing or using the software you agree to this license.
//  If you do not agree to this license, do not download, install,
//  copy or use the software.
//
//
//                        Intel License Agreement
//                For Open Source Computer Vision Library
//
// Copyright (C) 2000, Intel Corporation, all rights reserved.
// Third party copyrights are property of their respective owners.
//
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//
//   * Redistribution's of source code must retain the above copyright notice,
//     this list of conditions and the following disclaimer.
//
//   * Redistribution's in binary form must reproduce the above copyright notice,
//     this list of conditions and the following disclaimer in the documentation
//     and/or other materials provided with the distribution.
//
//   * The name of Intel Corporation may not be used to endorse or promote products
//     derived from this software without specific prior written permission.
//
// This software is provided by the copyright holders and contributors "as is" and
// any express or implied warranties, including, but not limited to, the implied
// warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the Intel Corporation or contributors be liable for any direct,
// indirect, incidental, special, exemplary, or consequential damages
// (including, but not limited to, procurement of substitute goods or services;
// loss of use, data, or profits; or business interruption) however caused
// and on any theory of liability, whether in contract, strict liability,
// or tort (including negligence or otherwise) arising in any way out of
// the use of this software, even if advised of the possibility of such damage.
//
//M*/

#include <opencv.hpp>
#include "gcgraph.hpp"
#include <limits>
#include <vector>
#include <iostream>

using namespace cv;

/*
This is implementation of image segmentation algorithm GrabCut described in
"GrabCut — Interactive Foreground Extraction using Iterated Graph Cuts".
Carsten Rother, Vladimir Kolmogorov, Andrew Blake.
 */

/*
 GMM - Gaussian Mixture Model
*/
class GMM
{
public:
    static const int componentsCount = 5;

    GMM( Mat& _model );
    double operator()( const Vec3d color ) const;
    double operator()( int ci, const Vec3d color ) const;
    int whichComponent( const Vec3d color ) const;

    void initLearning();
    void addSample( int ci, const Vec3d color );
    void endLearning();

private:
    void calcInverseCovAndDeterm( int ci );
    Mat model;
    double* coefs;
    double* mean;
    double* cov;

    double inverseCovs[componentsCount][3][3];
    double covDeterms[componentsCount];

    double sums[componentsCount][3];
    double prods[componentsCount][3][3];
    int sampleCounts[componentsCount];
    int totalSampleCount;
};

GMM::GMM( Mat& _model )
{
    const int modelSize = 3/*mean*/ + 9/*covariance*/ + 1/*component weight*/;
    if( _model.empty() )
    {
        _model.create( 1, modelSize*componentsCount, CV_64FC1 );
        _model.setTo(Scalar(0));
    }
    else if( (_model.type() != CV_64FC1) || (_model.rows != 1) || (_model.cols != modelSize*componentsCount) )
        CV_Error( CV_StsBadArg, "_model must have CV_64FC1 type, rows == 1 and cols == 13*componentsCount" );

    model = _model;

    coefs = model.ptr<double>(0);
    mean = coefs + componentsCount;
    cov = mean + 3*componentsCount;

    for( int ci = 0; ci < componentsCount; ci++ )
        if( coefs[ci] > 0 )
             calcInverseCovAndDeterm( ci );
}

double GMM::operator()( const Vec3d color ) const
{
    double res = 0;
    for( int ci = 0; ci < componentsCount; ci++ )
        res += coefs[ci] * (*this)(ci, color );
    return res;
}

double GMM::operator()( int ci, const Vec3d color ) const
{
    double res = 0;
    if( coefs[ci] > 0 )
    {
        CV_Assert( covDeterms[ci] > std::numeric_limits<double>::epsilon() );
        Vec3d diff = color;
        double* m = mean + 3*ci;
        diff[0] -= m[0]; diff[1] -= m[1]; diff[2] -= m[2];
        double mult = diff[0]*(diff[0]*inverseCovs[ci][0][0] + diff[1]*inverseCovs[ci][1][0] + diff[2]*inverseCovs[ci][2][0])
                   + diff[1]*(diff[0]*inverseCovs[ci][0][1] + diff[1]*inverseCovs[ci][1][1] + diff[2]*inverseCovs[ci][2][1])
                   + diff[2]*(diff[0]*inverseCovs[ci][0][2] + diff[1]*inverseCovs[ci][1][2] + diff[2]*inverseCovs[ci][2][2]);
        res = 1.0f/sqrt(covDeterms[ci]) * exp(-0.5f*mult);
    }
    return res;
}

int GMM::whichComponent( const Vec3d color ) const
{
    int k = 0;
    double max = 0;

    for( int ci = 0; ci < componentsCount; ci++ )
    {
        double p = (*this)( ci, color );
        if( p > max )
        {
            k = ci;
            max = p;
        }
    }
    return k;
}

void GMM::initLearning()
{
    for( int ci = 0; ci < componentsCount; ci++)
    {
        sums[ci][0] = sums[ci][1] = sums[ci][2] = 0;
        prods[ci][0][0] = prods[ci][0][1] = prods[ci][0][2] = 0;
        prods[ci][1][0] = prods[ci][1][1] = prods[ci][1][2] = 0;
        prods[ci][2][0] = prods[ci][2][1] = prods[ci][2][2] = 0;
        sampleCounts[ci] = 0;
    }
    totalSampleCount = 0;
}

void GMM::addSample( int ci, const Vec3d color )
{
    sums[ci][0] += color[0]; sums[ci][1] += color[1]; sums[ci][2] += color[2];
    prods[ci][0][0] += color[0]*color[0]; prods[ci][0][1] += color[0]*color[1]; prods[ci][0][2] += color[0]*color[2];
    prods[ci][1][0] += color[1]*color[0]; prods[ci][1][1] += color[1]*color[1]; prods[ci][1][2] += color[1]*color[2];
    prods[ci][2][0] += color[2]*color[0]; prods[ci][2][1] += color[2]*color[1]; prods[ci][2][2] += color[2]*color[2];
    sampleCounts[ci]++;
    totalSampleCount++;
}

void GMM::endLearning()
{
    const double variance = 0.01;
    for( int ci = 0; ci < componentsCount; ci++ )
    {
        int n = sampleCounts[ci];
        if( n == 0 )
            coefs[ci] = 0;
        else
        {
            coefs[ci] = (double)n/totalSampleCount;

            double* m = mean + 3*ci;
            m[0] = sums[ci][0]/n; m[1] = sums[ci][1]/n; m[2] = sums[ci][2]/n;

            double* c = cov + 9*ci;
            c[0] = prods[ci][0][0]/n - m[0]*m[0]; c[1] = prods[ci][0][1]/n - m[0]*m[1]; c[2] = prods[ci][0][2]/n - m[0]*m[2];
            c[3] = prods[ci][1][0]/n - m[1]*m[0]; c[4] = prods[ci][1][1]/n - m[1]*m[1]; c[5] = prods[ci][1][2]/n - m[1]*m[2];
            c[6] = prods[ci][2][0]/n - m[2]*m[0]; c[7] = prods[ci][2][1]/n - m[2]*m[1]; c[8] = prods[ci][2][2]/n - m[2]*m[2];

            double dtrm = c[0]*(c[4]*c[8]-c[5]*c[7]) - c[1]*(c[3]*c[8]-c[5]*c[6]) + c[2]*(c[3]*c[7]-c[4]*c[6]);
            if( dtrm <= std::numeric_limits<double>::epsilon() )
            {
                // Adds the white noise to avoid singular covariance matrix.
                c[0] += variance;
                c[4] += variance;
                c[8] += variance;
            }

            calcInverseCovAndDeterm(ci);
        }
    }
}

void GMM::calcInverseCovAndDeterm( int ci )
{
    if( coefs[ci] > 0 )
    {
        double *c = cov + 9*ci;
        double dtrm =
              covDeterms[ci] = c[0]*(c[4]*c[8]-c[5]*c[7]) - c[1]*(c[3]*c[8]-c[5]*c[6]) + c[2]*(c[3]*c[7]-c[4]*c[6]);

        CV_Assert( dtrm > std::numeric_limits<double>::epsilon() );
        inverseCovs[ci][0][0] =  (c[4]*c[8] - c[5]*c[7]) / dtrm;
        inverseCovs[ci][1][0] = -(c[3]*c[8] - c[5]*c[6]) / dtrm;
        inverseCovs[ci][2][0] =  (c[3]*c[7] - c[4]*c[6]) / dtrm;
        inverseCovs[ci][0][1] = -(c[1]*c[8] - c[2]*c[7]) / dtrm;
        inverseCovs[ci][1][1] =  (c[0]*c[8] - c[2]*c[6]) / dtrm;
        inverseCovs[ci][2][1] = -(c[0]*c[7] - c[1]*c[6]) / dtrm;
        inverseCovs[ci][0][2] =  (c[1]*c[5] - c[2]*c[4]) / dtrm;
        inverseCovs[ci][1][2] = -(c[0]*c[5] - c[2]*c[3]) / dtrm;
        inverseCovs[ci][2][2] =  (c[0]*c[4] - c[1]*c[3]) / dtrm;
    }
}

/*
  Calculate beta - parameter of GrabCut algorithm.
  beta = 1/(2*avg(sqr(||color[i] - color[j]||)))
*/
static double calcBeta( const std::vector<Mat> &img3d )
{
    double beta = 0;
    int nz = img3d.size();
    int cols = img3d[0].cols;
    int rows = img3d[0].rows;

    for( int z = 0; z < nz; z++) {
    	const Mat &img = img3d[z];

	    for( int y = 0; y < img.rows; y++ )
	    {
	        for( int x = 0; x < img.cols; x++ )
	        {
	            Vec3d color = img.at<Vec3b>(y,x);
	            if( x>0 ) // left
	            {
	                Vec3d diff = color - (Vec3d)img.at<Vec3b>(y,x-1);
	                beta += diff.dot(diff);
	            }
	            if( y>0 && x>0 ) // upleft
	            {
	                Vec3d diff = color - (Vec3d)img.at<Vec3b>(y-1,x-1);
	                beta += diff.dot(diff);
	            }
	            if( y>0 ) // up
	            {
	                Vec3d diff = color - (Vec3d)img.at<Vec3b>(y-1,x);
	                beta += diff.dot(diff);
	            }
	            if( y>0 && x<img.cols-1) // upright
	            {
	                Vec3d diff = color - (Vec3d)img.at<Vec3b>(y-1,x+1);
	                beta += diff.dot(diff);
	            }
	            if( z>0 ) {
	            	const Mat &imgBack = img3d[z-1];
	            	// back
	            	Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y,x);
	            	beta += diff.dot(diff);
	            	if( x>0 ) // back left
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y,x-1);
		                beta += diff.dot(diff);
		            }
		            if( y>0 && x>0 ) // back upleft
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y-1,x-1);
		                beta += diff.dot(diff);
		            }
		            if( y>0 ) // back up
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y-1,x);
		                beta += diff.dot(diff);
		            }
		            if( y>0 && x<imgBack.cols-1) // back upright
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y-1,x+1);
		                beta += diff.dot(diff);
		            }
		            if( x<imgBack.cols-1 ) // back right
		            {
		            	Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y,x+1);
		                beta += diff.dot(diff);
		            }
		            if( y<imgBack.rows-1 && x<imgBack.cols-1 ) // back downright
		            {
		            	Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y+1,x+1);
		                beta += diff.dot(diff);
		            }
		            if( y<imgBack.rows-1 ) // back down
		            {
		            	Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y+1,x);
		                beta += diff.dot(diff);
		            }
		            if( y<imgBack.rows-1 && x>0 ) // back downleft
		            {
		            	Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y+1,x-1);
		                beta += diff.dot(diff);
		            }
	            }
	        }
	    }
    }
    
    int inplaneCount = 4*cols*rows - 3*cols - 3*rows + 2;
    int backplaneCount = 9*cols*rows - 6*cols - 6*rows + 4;

    if( beta <= std::numeric_limits<double>::epsilon() )
        beta = 0;
    else
        beta = 1.f / (2 * beta/( nz*inplaneCount + (nz-1)*backplaneCount ) );

    return beta;
}


enum class Nhood { l, ul, u, ur, b, bl, bul, bu, bur, br, bdr, bd, bdl};

/*
  Calculate weights of noterminal vertices of graph.
  beta and gamma - parameters of GrabCut algorithm.
 */
static void calcNWeights( const std::vector<Mat> &img3d, std::vector< std::vector<Mat> > &weights3d, double beta, double gamma )
{
    const double gammaDivSqrt2 = gamma / std::sqrt(2.0f);
    const double gammaDivSqrt3 = gamma / std::sqrt(3.0f);
    // leftW.create( img.rows, img.cols, CV_64FC1 );
    // upleftW.create( img.rows, img.cols, CV_64FC1 );
    // upW.create( img.rows, img.cols, CV_64FC1 );
    // uprightW.create( img.rows, img.cols, CV_64FC1 );

    int nz = img3d.size();

    for( int z = 0; z < nz; z++ ) {
    	std::vector<Mat> &weights = weights3d[z];
    	const Mat &img = img3d[z];

    	for( int y = 0; y < img.rows; y++ )
	    {
	        for( int x = 0; x < img.cols; x++ )
	        {
	            Vec3d color = img.at<Vec3b>(y,x);
	            if( x-1>=0 ) // left
	            {
	                Vec3d diff = color - (Vec3d)img.at<Vec3b>(y,x-1);
	                weights[int(Nhood::l)].at<double>(y,x) = gamma * exp(-beta*diff.dot(diff));
	            }
	            else
	                weights[int(Nhood::l)].at<double>(y,x) = 0;
	            if( x-1>=0 && y-1>=0 ) // upleft
	            {
	                Vec3d diff = color - (Vec3d)img.at<Vec3b>(y-1,x-1);
	                weights[int(Nhood::ul)].at<double>(y,x) = gammaDivSqrt2 * exp(-beta*diff.dot(diff));
	            }
	            else
	                weights[int(Nhood::ul)].at<double>(y,x) = 0;
	            if( y-1>=0 ) // up
	            {
	                Vec3d diff = color - (Vec3d)img.at<Vec3b>(y-1,x);
	                weights[int(Nhood::u)].at<double>(y,x) = gamma * exp(-beta*diff.dot(diff));
	            }
	            else
	                weights[int(Nhood::u)].at<double>(y,x) = 0;
	            if( x+1<img.cols && y-1>=0 ) // upright
	            {
	                Vec3d diff = color - (Vec3d)img.at<Vec3b>(y-1,x+1);
	                weights[int(Nhood::ur)].at<double>(y,x) = gammaDivSqrt2 * exp(-beta*diff.dot(diff));
	            }
	            else
	                weights[int(Nhood::ur)].at<double>(y,x) = 0;

	            if( z > 0) {
	            	const Mat &imgBack = img3d[z-1];
	            	// back
	            	Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y,x);
		            weights[int(Nhood::b)].at<double>(y,x) = gamma * exp(-beta*diff.dot(diff));
	            	if( x>0 ) // back left
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y,x-1);
		                weights[int(Nhood::bl)].at<double>(y,x) = gammaDivSqrt2 * exp(-beta*diff.dot(diff));
		            }
		            else
		                weights[int(Nhood::bl)].at<double>(y,x) = 0;
		            if( x>0 && y>0 ) // back upleft
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y-1,x-1);
		                weights[int(Nhood::bul)].at<double>(y,x) = gammaDivSqrt3 * exp(-beta*diff.dot(diff));
		            }
		            else
		                weights[int(Nhood::bul)].at<double>(y,x) = 0;
		            if( y>0 ) // back up
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y-1,x);
		                weights[int(Nhood::bu)].at<double>(y,x) = gammaDivSqrt2 * exp(-beta*diff.dot(diff));
		            }
		            else
		                weights[int(Nhood::bu)].at<double>(y,x) = 0;
		            if( x<imgBack.cols-1 && y>0 ) // back upright
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y-1,x+1);
		                weights[int(Nhood::bur)].at<double>(y,x) = gammaDivSqrt3 * exp(-beta*diff.dot(diff));
		            }
		            else
		                weights[int(Nhood::bur)].at<double>(y,x) = 0;
		            if( x<imgBack.cols-1) // back right
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y,x+1);
		                weights[int(Nhood::br)].at<double>(y,x) = gammaDivSqrt2 * exp(-beta*diff.dot(diff));
		            }
		            else
		                weights[int(Nhood::br)].at<double>(y,x) = 0;
		            if( x<imgBack.cols-1 && y<imgBack.rows-1 ) // back downright
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y+1,x+1);
		                weights[int(Nhood::bdr)].at<double>(y,x) = gammaDivSqrt3 * exp(-beta*diff.dot(diff));
		            }
		            else
		                weights[int(Nhood::bdr)].at<double>(y,x) = 0;
		            if( y<imgBack.rows-1 ) // back down
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y+1,x);
		                weights[int(Nhood::bd)].at<double>(y,x) = gammaDivSqrt2 * exp(-beta*diff.dot(diff));
		            }
		            else
		                weights[int(Nhood::bd)].at<double>(y,x) = 0;
		            if( x>0 && y<imgBack.rows-1 ) // back downleft
		            {
		                Vec3d diff = color - (Vec3d)imgBack.at<Vec3b>(y+1,x-1);
		                weights[int(Nhood::bdl)].at<double>(y,x) = gammaDivSqrt3 * exp(-beta*diff.dot(diff));
		            }
		            else
		                weights[int(Nhood::bdl)].at<double>(y,x) = 0;
	            }
	            else { // No backplane
	            	weights[int(Nhood::b)].at<double>(y,x) = 0;
	            	weights[int(Nhood::bl)].at<double>(y,x) = 0;
	            	weights[int(Nhood::bul)].at<double>(y,x) = 0;
	            	weights[int(Nhood::bu)].at<double>(y,x) = 0;
	            	weights[int(Nhood::bur)].at<double>(y,x) = 0;
	            	weights[int(Nhood::br)].at<double>(y,x) = 0;
	            	weights[int(Nhood::bdr)].at<double>(y,x) = 0;
	            	weights[int(Nhood::bd)].at<double>(y,x) = 0;
	            	weights[int(Nhood::bdl)].at<double>(y,x) = 0;
	            }
	        }
	    }
    }
    
}

/*
  Check size, type and element values of mask matrix.
 */
static void checkMask( const std::vector<Mat> &img3d, const std::vector<Mat> &mask3d )
{
    // if( mask.empty() )
    //     CV_Error( CV_StsBadArg, "mask is empty" );
    // if( mask.type() != CV_8UC1 )
    //     CV_Error( CV_StsBadArg, "mask must have CV_8UC1 type" );
    // if( mask.cols != img.cols || mask.rows != img.rows )
    //     CV_Error( CV_StsBadArg, "mask must have as many rows and cols as img" );
    // for( int y = 0; y < mask.rows; y++ )
    // {
    //     for( int x = 0; x < mask.cols; x++ )
    //     {
    //         uchar val = mask.at<uchar>(y,x);
    //         if( val!=GC_BGD && val!=GC_FGD && val!=GC_PR_BGD && val!=GC_PR_FGD )
    //             CV_Error( CV_StsBadArg, "mask element value must be equel"
    //                 "GC_BGD or GC_FGD or GC_PR_BGD or GC_PR_FGD" );
    //     }
    // }
}

// /*
//   Initialize mask using rectangular.
// */
// static void initMaskWithRect( Mat& mask, Size imgSize, Rect rect )
// {
//     mask.create( imgSize, CV_8UC1 );
//     mask.setTo( GC_BGD );

//     rect.x = std::max(0, rect.x);
//     rect.y = std::max(0, rect.y);
//     rect.width = std::min(rect.width, imgSize.width-rect.x);
//     rect.height = std::min(rect.height, imgSize.height-rect.y);

//     (mask(rect)).setTo( Scalar(GC_PR_FGD) );
// }

/*
  Initialize GMM background and foreground models using kmeans algorithm.
*/
static void initGMMs( const std::vector<Mat> &img3d, const std::vector<Mat> &mask3d, GMM& bgdGMM, GMM& fgdGMM )
{
    const int kMeansItCount = 10;
    const int kMeansType = KMEANS_PP_CENTERS;

    Mat bgdLabels, fgdLabels;
    std::vector<Vec3f> bgdSamples, fgdSamples;
    
    int nz = img3d.size();
    for( int zz=0; zz<nz; zz++) {
    	const Mat &img = img3d[zz];
    	const Mat &mask = mask3d[zz];

    	Point p;
	    for( p.y = 0; p.y < img.rows; p.y++ )
	    {
	        for( p.x = 0; p.x < img.cols; p.x++ )
	        {
	            if( mask.at<uchar>(p) == GC_BGD || mask.at<uchar>(p) == GC_PR_BGD )
	                bgdSamples.push_back( (Vec3f)img.at<Vec3b>(p) );
	            else // GC_FGD | GC_PR_FGD
	                fgdSamples.push_back( (Vec3f)img.at<Vec3b>(p) );
	        }
	    }
    }

    CV_Assert( !bgdSamples.empty() && !fgdSamples.empty() );
    Mat _bgdSamples( (int)bgdSamples.size(), 3, CV_32FC1, &bgdSamples[0][0] );
    kmeans( _bgdSamples, GMM::componentsCount, bgdLabels,
            TermCriteria( CV_TERMCRIT_ITER, kMeansItCount, 0.0), 0, kMeansType );
    Mat _fgdSamples( (int)fgdSamples.size(), 3, CV_32FC1, &fgdSamples[0][0] );
    kmeans( _fgdSamples, GMM::componentsCount, fgdLabels,
            TermCriteria( CV_TERMCRIT_ITER, kMeansItCount, 0.0), 0, kMeansType );

    bgdGMM.initLearning();
    for( int i = 0; i < (int)bgdSamples.size(); i++ )
        bgdGMM.addSample( bgdLabels.at<int>(i,0), bgdSamples[i] );
    bgdGMM.endLearning();

    fgdGMM.initLearning();
    for( int i = 0; i < (int)fgdSamples.size(); i++ )
        fgdGMM.addSample( fgdLabels.at<int>(i,0), fgdSamples[i] );
    fgdGMM.endLearning();
}

/*
  Assign GMMs components for each pixel.
*/
static void assignGMMsComponents( const std::vector<Mat> &img3d, const std::vector<Mat> &mask3d, const GMM& bgdGMM, const GMM& fgdGMM, std::vector<Mat> &compIdxs3d )
{
	Point p;
	int nz = img3d.size();
	for( int z = 0; z < nz; z++ ) {
		const Mat &img = img3d[z];
		const Mat &mask = mask3d[z];
		Mat &compIdxs = compIdxs3d[z];

	    for( p.y = 0; p.y < img.rows; p.y++ )
	    {
	        for( p.x = 0; p.x < img.cols; p.x++ )
	        {
	            Vec3d color = img.at<Vec3b>(p);
	            compIdxs.at<int>(p) = mask.at<uchar>(p) == GC_BGD || mask.at<uchar>(p) == GC_PR_BGD ?
	                bgdGMM.whichComponent(color) : fgdGMM.whichComponent(color);
	        }
	    }
	}
    
}

/*
  Learn GMMs parameters.
*/
static void learnGMMs( const std::vector<Mat> &img3d, const std::vector<Mat> &mask3d, const std::vector<Mat> &compIdxs3d, GMM& bgdGMM, GMM& fgdGMM )
{
    bgdGMM.initLearning();
    fgdGMM.initLearning();
    Point p;

    int nz = img3d.size();
    for( int z = 0; z < nz; z++ )
    {
    	const Mat &img = img3d[z];
    	const Mat &mask = mask3d[z];
    	const Mat &compIdxs = compIdxs3d[z];

        for( p.y = 0; p.y < img.rows; p.y++ )
        {
            for( p.x = 0; p.x < img.cols; p.x++ )
            {
            	int ci = compIdxs.at<int>(p);
                if( mask.at<uchar>(p) == GC_BGD || mask.at<uchar>(p) == GC_PR_BGD )
                    bgdGMM.addSample( ci, img.at<Vec3b>(p) );
                else
                    fgdGMM.addSample( ci, img.at<Vec3b>(p) );
            }
        }
    }
    bgdGMM.endLearning();
    fgdGMM.endLearning();
}

/*
  Construct GCGraph
*/
static void constructGCGraph( const std::vector<Mat> &img3d, const std::vector<Mat> &mask3d, const GMM& bgdGMM, const GMM& fgdGMM, double lambda,
                       const std::vector< std::vector<Mat> > &weights3d, GCGraph<double>& graph )
{
    int nz = img3d.size();
    int cols = img3d[0].cols;
    int rows = img3d[0].rows;
    int vtxCount = cols*rows*nz;
    int inplaneEdgeCount = 4*cols*rows - 3*cols - 3*rows + 2;
    int backplaneEdgeCount = 9*cols*rows - 6*cols - 6*rows + 4;
    int edgeCount = 2*(nz*inplaneEdgeCount + (nz-1)*backplaneEdgeCount);

    graph.create(vtxCount, edgeCount);
    Point p;

    for( int z = 0; z < nz; z++ ) {
    	const Mat &img = img3d[z];
    	const Mat &mask = mask3d[z];
    	const std::vector<Mat> &weights = weights3d[z];

    	for( p.y = 0; p.y < img.rows; p.y++ )
	    {
	        for( p.x = 0; p.x < img.cols; p.x++)
	        {
	            // add node
	            int vtxIdx = graph.addVtx();
	            Vec3b color = img.at<Vec3b>(p);

	            // set t-weights
	            double fromSource, toSink;
	            if( mask.at<uchar>(p) == GC_PR_BGD || mask.at<uchar>(p) == GC_PR_FGD )
	            {
	                fromSource = -log( bgdGMM(color) );
	                toSink = -log( fgdGMM(color) );
	            }
	            else if( mask.at<uchar>(p) == GC_BGD )
	            {
	                fromSource = 0;
	                toSink = lambda;
	            }
	            else // GC_FGD
	            {
	                fromSource = lambda;
	                toSink = 0;
	            }
	            graph.addTermWeights( vtxIdx, fromSource, toSink );

	            // set n-weights
	            if( p.x>0 ) // left
	            {
	                double w = weights[int(Nhood::l)].at<double>(p);
	                graph.addEdges( vtxIdx, vtxIdx-1, w, w );
	            }
	            if( p.x>0 && p.y>0 ) // upleft
	            {
	                double w = weights[int(Nhood::ul)].at<double>(p);
	                graph.addEdges( vtxIdx, vtxIdx-img.cols-1, w, w );
	            }
	            if( p.y>0 ) // up
	            {
	                double w = weights[int(Nhood::u)].at<double>(p);
	                graph.addEdges( vtxIdx, vtxIdx-img.cols, w, w );
	            }
	            if( p.x<img.cols-1 && p.y>0 ) // upright
	            {
	                double w = weights[int(Nhood::ur)].at<double>(p);
	                graph.addEdges( vtxIdx, vtxIdx-img.cols+1, w, w );
	            }
	            if( z>0 ) {
	            	int planeSize = rows*cols;
	            	// back
	            	double w = weights[int(Nhood::b)].at<double>(p);
	                graph.addEdges( vtxIdx, vtxIdx-planeSize, w, w );
	                if( p.x>0 ) // back left
		            {
		                double w = weights[int(Nhood::bl)].at<double>(p);
		                graph.addEdges( vtxIdx, vtxIdx-1 - planeSize, w, w );
		            }
		            if( p.x>0 && p.y>0 ) // back upleft
		            {
		                double w = weights[int(Nhood::bul)].at<double>(p);
		                graph.addEdges( vtxIdx, vtxIdx-img.cols-1 - planeSize, w, w );
		            }
		            if( p.y>0 ) // back up
		            {
		                double w = weights[int(Nhood::bu)].at<double>(p);
		                graph.addEdges( vtxIdx, vtxIdx-img.cols - planeSize, w, w );
		            }
		            if( p.x<img.cols-1 && p.y>0 ) // back upright
		            {
		                double w = weights[int(Nhood::bur)].at<double>(p);
		                graph.addEdges( vtxIdx, vtxIdx-img.cols+1 - planeSize, w, w );
		            }
		            if( p.x<img.cols-1) // back right
		            {
		                double w = weights[int(Nhood::br)].at<double>(p);
		                graph.addEdges( vtxIdx, vtxIdx+1 - planeSize, w, w );
		            }
		            if( p.x<img.cols-1 && p.y<img.rows-1 ) // back downright
		            {
		                double w = weights[int(Nhood::bdr)].at<double>(p);
		                graph.addEdges( vtxIdx, vtxIdx+img.cols+1 - planeSize, w, w );
		            }
		            if( p.y<img.rows-1 ) // back down
		            {
		                double w = weights[int(Nhood::bd)].at<double>(p);
		                graph.addEdges( vtxIdx, vtxIdx+img.cols - planeSize, w, w );
		            }
		            if( p.x>0 && p.y<img.rows-1 ) // back downleft
		            {
		                double w = weights[int(Nhood::bdl)].at<double>(p);
		                graph.addEdges( vtxIdx, vtxIdx+img.cols-1 - planeSize, w, w );
		            }
	            }
	        }
	    }
    }
    
}

/*
  Estimate segmentation using MaxFlow algorithm
*/
static void estimateSegmentation( GCGraph<double>& graph, std::vector<Mat> &mask3d )
{
    graph.maxFlow();
    Point p;
    int nz = mask3d.size();
    for( int z = 0; z < nz; z++) {
    	Mat &mask = mask3d[z];
    	for( p.y = 0; p.y < mask.rows; p.y++ )
	    {
	        for( p.x = 0; p.x < mask.cols; p.x++ )
	        {
	            if( mask.at<uchar>(p) == GC_PR_BGD || mask.at<uchar>(p) == GC_PR_FGD )
	            {
	                if( graph.inSourceSegment( z*mask.cols*mask.rows + p.y*mask.cols+p.x /*vertex index*/ ) )
	                    mask.at<uchar>(p) = GC_PR_FGD;
	                else
	                    mask.at<uchar>(p) = GC_PR_BGD;
	            }
	        }
	    }
    }
    
}

void grabCut3d( std::vector<Mat> &img3d, std::vector<Mat> &mask3d,
                  InputOutputArray _bgdModel, InputOutputArray _fgdModel,
                  int iterCount, int mode )
{

    Mat img = img3d[0];
    // Mat& mask = mask3d[0];
    Mat& bgdModel = _bgdModel.getMatRef();
    Mat& fgdModel = _fgdModel.getMatRef();

    int nz = img3d.size();

    // Check for empty image
    bool isEmpty = true;
    for( Mat &slice : img3d) {
    	if (!slice.empty()) {
    		isEmpty = false;
    		break;
    	}
    }

    if( isEmpty )
        CV_Error( CV_StsBadArg, "image is empty" );
    if( img3d[0].type() != CV_8UC3 )
        CV_Error( CV_StsBadArg, "image must have CV_8UC3 type" );

    GMM bgdGMM( bgdModel ), fgdGMM( fgdModel );

    std::vector<Mat> compIdxs3d;
    for( int zz=0; zz<nz; zz++ ) {
    	Mat compIdxs( img3d[0].size(), CV_32SC1 );
    	compIdxs3d.push_back(compIdxs);
    }

    Mat compIdxs( img3d[0].size(), CV_32SC1 );

    if( mode == GC_INIT_WITH_RECT || mode == GC_INIT_WITH_MASK )
    {
        if( mode == GC_INIT_WITH_RECT )
            // initMaskWithRect( mask, img.size(), rect );
            CV_Error( CV_StsBadArg, "Rect initialization is not available in grabCut3d" );
        else // flag == GC_INIT_WITH_MASK
            checkMask( img3d, mask3d );
        initGMMs( img3d, mask3d, bgdGMM, fgdGMM );
    }

    if( iterCount <= 0)
        return;

    if( mode == GC_EVAL )
        checkMask( img3d, mask3d );

    const double gamma = 5;
    const double lambda = 27*gamma;
    const double beta = calcBeta( img3d );

    std::vector< std::vector<Mat> > weights3d;
    for (int zz=0; zz<nz; zz++) {
    	std::vector<Mat> weights;
    	for( int i = 0; i < 13; i++) { // 9 backplane + 4 inplane neighbors
    		Mat weight( img.rows, img.cols, CV_64FC1 );
    		weights.push_back(weight);
    	}
    	weights3d.push_back(weights);
    }
    // Mat leftW, upleftW, upW, uprightW;
    // calcNWeights( img, leftW, upleftW, upW, uprightW, beta, gamma );
    calcNWeights( img3d, weights3d, beta, gamma );

    for( int i = 0; i < iterCount; i++ )
    {
    	std::cout << "Iteration " << i << std::flush;
        GCGraph<double> graph;
        std::cout << " -> " << "assignGMMsComponents" << std::flush;
        assignGMMsComponents( img3d, mask3d, bgdGMM, fgdGMM, compIdxs3d );
        std::cout << " -> " << "learnGMMs" << std::flush;
        learnGMMs( img3d, mask3d, compIdxs3d, bgdGMM, fgdGMM );
        std::cout << " -> " << "constructGCGraph" << std::flush;
        constructGCGraph(img3d, mask3d, bgdGMM, fgdGMM, lambda, weights3d, graph );
        std::cout << " -> " << "maxFlow" << std::flush;
        estimateSegmentation( graph, mask3d );
        std::cout << " -> " << "END" << std::endl;
    }
}