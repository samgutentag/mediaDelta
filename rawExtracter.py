import rawpy
import imageio

def extract(inputImage, outputImage):
    raw = rawpy.imread(inputImage)
    rgb = raw.postprocess(no_auto_bright=True,use_auto_wb =False,gamma=None)

    imageio.imsave(outputImage, rgb)


def main():
    print 'extracint image from raw file...'

if __name__ == '__main__':
    main()




#EOF
