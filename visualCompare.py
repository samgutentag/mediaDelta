#!/usr/bin/end python

#------------------------------------------------------------------------------
#		Sample Usage
#------------------------------------------------------------------------------
#
#   > python printExifTags.py -d ~/Desktop/testPhotos
#
#------------------------------------------------------------------------------


import argparse
import PIL
from PIL import Image
from PIL import ImageStat
import sys



#------------------------------------------------------------------------------
#		comparisons
#------------------------------------------------------------------------------

def diffHistograms(hist1, hist2):

    if hist1 == hist2:
        print 'this images match!'
    else:

        histogramCompare = []

        if len(hist1) == len(hist2):
            index = 0
            for item in hist1:
                histogramPair = (hist1[index], hist2[index])
                histogramCompare.append(histogramPair)
                index += 1


        for item in histogramCompare:
            if item[0] == item[1]:
                print '\t%s\t%s' % (item[0], item[1])
            else:
                print '\t%s\t%s\tDIFF!' % (item[0], item[1])


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

    print 'img1_stat.extrema\t%s' % img1_stat.extrema
    print 'img2_stat.extrema\t%s' % img2_stat.extrema

    print 'img1_stat.count\t\t%s' % img1_stat.count
    print 'img2_stat.count\t\t%s' % img2_stat.count

    print 'img1_stat.sum\t\t%s' % img1_stat.sum
    print 'img2_stat.sum\t\t%s' % img2_stat.sum

    print 'img1_stat.sum2\t\t%s' % img1_stat.sum2
    print 'img2_stat.sum2\t\t%s' % img2_stat.sum2

    print 'img1_stat.mean\t\t%s' % img1_stat.mean
    print 'img2_stat.mean\t\t%s' % img2_stat.mean

    print 'img1_stat.median\t%s' % img1_stat.median
    print 'img2_stat.median\t%s' % img2_stat.median

    print 'img1_stat.rms\t\t%s' % img1_stat.rms
    print 'img2_stat.rms\t\t%s' % img2_stat.rms

    print 'img1_stat.vars\t\t%s' % img1_stat.var
    print 'img2_stat.vars\t\t%s' % img2_stat.var

    print 'img1_stat.stddev\t%s' % img1_stat.stddev
    print 'img2_stat.stddev\t%s' % img2_stat.stddev















    # # print histogram1
    # print len(histogram1)
    # # print histogram2
    # print len(histogram2)





    # if img1_histogram == img2_histogram:
    #     print 'these images match!'
    # else:
    #     print 'these images do not match'


#------------------------------------------------------------------------------
#		main function
#------------------------------------------------------------------------------

def main():
    print 'lets compare two images!'

    script = sys.argv[0]
    image1 = sys.argv[1]
    image2 = sys.argv[2]
    compareImages(image1, image2)





if __name__ == '__main__':
    main()
