#!/usr/bin/end python


from moviepy.editor import *



def resizeClip(inputFile, outputFile, width, height):

    #   get the input file clip
    inputClip = VideoFileClip(inputFile, audio=False)

    #   resize this clip
    clip_resized = inputClip.resize( (width, height) )

    #   write resized clip to a new file
    clip_resized.write_videofile(outputFile,
                        # fps=24,
                        codec='libx264',
                        audio=False)


if __name__ == '__main__':
    main()



#   EOF
