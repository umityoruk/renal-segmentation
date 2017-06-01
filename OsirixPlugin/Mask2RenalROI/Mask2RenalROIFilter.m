//
//  Mask2RenalROIFilter.m
//  Mask2RenalROI
//
//  Created by Umit Yoruk on Wed May 24 2017.
//  Modified from https://osirixpluginbasics.wordpress.com/2010/11/05/brush-roi-tplain/
//  Copyright (c) 2017 Stanford University. All rights reserved.
//

#import "Mask2RenalROIFilter.h"

@implementation Mask2RenalROIFilter

- (long) filterImage:(NSString*) menuName
{
    NSArray *roiNames = @[@"Aorta", @"L_Ctx", @"R_Ctx", @"L_Med", @"R_Med", @"L_CS", @"R_CS"];
    NSArray *roiValues = @[@300, @350, @400, @450, @500, @550, @600];
    NSArray *roiColors = @[@[@255, @0, @0],
                           @[@109, @232, @122],
                           @[@109, @152, @232],
                           @[@232, @109, @165],
                           @[@232, @136, @109],
                           @[@232, @154, @109],
                           @[@232, @218, @109]];
    
    NSArray         *pixList = [viewerController pixList:0];
    
    int             curSlice = [[viewerController imageView] curImage];
    DCMPix          *curPix = [pixList objectAtIndex:curSlice];
    
    float           pixHeight = [curPix pheight];
    float           pixWidth = [curPix pwidth];
    float           numPixels = pixHeight * pixWidth;
    float           *fImageA = [curPix fImage]; // load the pixels of the current image
    
    unsigned char   *textureBuffer;
    
    // Allocate memory for the texture buffer and initialize the values.
    textureBuffer = (unsigned char*)malloc(numPixels * sizeof(unsigned char));
    for (int i=0; i < numPixels; i++) {
        textureBuffer[i] = 0x00;
    }
    
    // Iterate over all slices in the 3D image.
    for (int sliceId=0; sliceId < [pixList count]; sliceId++) {
        curPix = [pixList objectAtIndex:sliceId];
        fImageA = [curPix fImage]; // load the pixels of the current slice
        
        // Iterate over all ROI regions.
        for (int regionId=0; regionId < [roiNames count]; regionId++) {
            ROI *newRoi;
            
            // Map the values to ROI texture buffers.
            for (int i=0; i < numPixels; i++) {
                if (fImageA[i] == [roiValues[regionId] integerValue]) {
                    textureBuffer[i] = 0xFF;
                }
                else {
                    textureBuffer[i] = 0x00;
                }
            }
            
            // Create the new ROI.
            newRoi = [[[ROI alloc] initWithTexture:textureBuffer textWidth:pixWidth textHeight:pixHeight textName:roiNames[regionId] positionX:0 positionY:0 spacingX:[curPix pixelSpacingX] spacingY:[curPix pixelSpacingY] imageOrigin:[self originCorrectedAccordingToOrientation: curPix]] autorelease];
            
            // Set color of the new ROI
            [newRoi setColor:(RGBColor){256*[roiColors[regionId][0] integerValue],
                256*[roiColors[regionId][1] integerValue],
                256*[roiColors[regionId][2] integerValue]}];
            
            //Alternative ROI representation
            // Convert "NewROI" from Brush to Polygon ROI
            // the number limits the points of which the polygon will be created
            // newRoi = [viewerController convertBrushROItoPolygon:newRoi numPoints:500];
            
            // Add the new ROIs to the ROI list of the current slice.
            NSMutableArray *roiSeriesList = [viewerController roiList];
            NSMutableArray *roiImageList = [roiSeriesList objectAtIndex:sliceId];
            [roiImageList addObject:newRoi];
        }
    }
    
    // Free texture buffer memory.
    free(textureBuffer);
    
    // Update Osirix display.
    [viewerController needsDisplayUpdate];
    
    return 0;
}


- (NSPoint) originCorrectedAccordingToOrientation: (DCMPix*) pix1
{
    double destOrigin[ 2];
    double vectorP1[ 9];
    
    [pix1 orientationDouble: vectorP1];
    
    destOrigin[ 0] = [pix1  originX] * vectorP1[ 0] + [pix1  originY] * vectorP1[ 1] + [pix1  originZ] * vectorP1[ 2];
    destOrigin[ 1] = [pix1  originX] * vectorP1[ 3] + [pix1  originY] * vectorP1[ 4] + [pix1  originZ] * vectorP1[ 5];
    
    return NSMakePoint( destOrigin[ 0], destOrigin[ 1]);
}

@end
