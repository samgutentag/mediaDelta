#!/usr/bin/end python

#------------------------------------------------------------------------------
#		Sample Usage
#------------------------------------------------------------------------------
#
#   > python printExifTags.py -d ~/Desktop/testPhotos
#
#------------------------------------------------------------------------------


import argparse
from PIL import Image
from PIL import ImageStat
import sys
import utils



#------------------------------------------------------------------------------
#		comparisons
#------------------------------------------------------------------------------

def imageMatch(image1, image2):
    isSame = True
    # img1 = Image.open(image1)
    # img2 = Image.open(image2)

    deviation01 = image1.stddev[0] - image2.stddev[0]
    deviation02 = image1.stddev[1] - image2.stddev[1]
    deviation03 = image1.stddev[2] - image2.stddev[2]

    print 'Deviation01:\t%s' % deviation01
    print 'Deviation02:\t%s' % deviation02
    print 'Deviation03:\t%s' % deviation03

    if deviation01 > 1.0:
        isSame = False
    if deviation02 > 1.0:
        isSame = False
    if deviation03 > 1.0:
        isSame = False

    return isSame

def compareImages(image1, image2):
    print 'image1:\t%s' % image1
    print 'image2:\t%s' % image2

    img1 = Image.open(image1)
    img1_histogram = img1.histogram()
    img2 = Image.open(image2)
    img2_histogram = img2.histogram()

    # print diffHistograms(img1_histogram, img2_histogram)


    img1_stat = ImageStat.Stat(img1)
    img2_stat = ImageStat.Stat(img2)

    # print 'img1_stat.extrema\t%s' % img1_stat.extrema
    # print 'img2_stat.extrema\t%s' % img2_stat.extrema
    #
    # print 'img1_stat.count\t\t%s' % img1_stat.count
    # print 'img2_stat.count\t\t%s' % img2_stat.count
    #
    # print 'img1_stat.sum\t\t%s' % img1_stat.sum
    # print 'img2_stat.sum\t\t%s' % img2_stat.sum
    #
    # print 'img1_stat.sum2\t\t%s' % img1_stat.sum2
    # print 'img2_stat.sum2\t\t%s' % img2_stat.sum2
    #
    # print 'img1_stat.mean\t\t%s' % img1_stat.mean
    # print 'img2_stat.mean\t\t%s' % img2_stat.mean
    #
    # print 'img1_stat.median\t%s' % img1_stat.median
    # print 'img2_stat.median\t%s' % img2_stat.median
    #
    # print 'img1_stat.rms\t\t%s' % img1_stat.rms
    # print 'img2_stat.rms\t\t%s' % img2_stat.rms
    #
    # print 'img1_stat.vars\t\t%s' % img1_stat.var
    # print 'img2_stat.vars\t\t%s' % img2_stat.var
    #
    # print 'img1_stat.stddev\t%s' % img1_stat.stddev
    # print 'img2_stat.stddev\t%s' % img2_stat.stddev

    # utils.spacer()

    if imageMatch(img1_stat, img2_stat):
        print 'these images are very likely matches!'
    else:
        print 'these images are probably not matches'



#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():
    print 'lets compare some images!'

    script = sys.argv[0]
    image1 = sys.argv[1]
    image2 = sys.argv[2]
    

if __name__ == '__main__':
    main()
