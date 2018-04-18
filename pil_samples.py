#
#
# from PIL import Image, ImageFilter
# import pyexifinfo
# import rawpy
# import imageio
#
#
#
# import os, sys
# import json
# import pandas as pd
#
#
# def make_thumb(infile, dest_dir, thumb_size=(720,720), thumb_file_type='JPEG'):
#
#     file_name = os.path.splitext(infile)[0].split('/')[-1]
#     thumb_file_name = '{}.thumbnail.jpg'.format(file_name)
#
#
#     thumb_file_path = '{}{}'.format(dest_dir, thumb_file_name)
#     # print(thumb_file_path)
#
#
#     # try to read raw file
#     try:
#
#         with rawpy.imread(infile) as raw:
#             rgb = raw.postprocess()
#             im = Image.fromarray(rgb)
#
#     # non raw file
#     except:
#         im = Image.open(infile)
#
#     # make thumbnail
#     im.thumbnail(thumb_size)
#     im.save(thumb_file_path, thumb_file_type)
#
#     print('Thumbnail written to {}'.format(thumb_file_path))
#
#
# dest_dir = './thumbnails/'
# for infile in sys.argv[1:]:
#     make_thumb(infile, dest_dir)
#
# #
# # size = (720, 720)
# #
# # for infile in sys.argv[1:]:
# #     filename = os.path.splitext(infile)[0].split('/')[-1]
# #
# #     # tempfile = os.path.splitext(infile)[0] + ".temp.jpg"
# #     # tempfile = './{}.temp.jpg'.format(filename)
# #     tempfile = './temp.jpg'
# #
# #     # outfile = os.path.splitext(infile)[0] + ".thumbnail.jpg"
# #     outfile = './thumbnails/{}.thumbnail.jpg'.format(filename)
# #
# #     if infile != outfile:
# #
# #         # try to read raw file
# #         try:
# #
# #             with rawpy.imread(infile) as raw:
# #                 rgb = raw.postprocess()
# #                 im = Image.fromarray(rgb)
# #
# #         # non raw file
# #         except:
# #             im = Image.open(infile)
# #
# #         # make thumbnail
# #         im.thumbnail(size)
# #         im.save(outfile, "JPEG")
# #
# #


from PIL import Image, ImageChops

# point_table = ([0] + ([255] * 255))

a = '/Users/samgutentag/Desktop/import/IMAGE/THUMB/CANON.EOS.7D.MARK.II/20180413/samgutentag.032021001510.20180413.142501.0.JPEG'
b = '/Users/samgutentag/Desktop/import/IMAGE/THUMB/CANON.EOS.7D.MARK.II/20180413/samgutentag.032021001510.20180413.142501.2.JPEG'


c = '/Users/samgutentag/Desktop/import/IMAGE/THUMB/CANON.EOS.7D.MARK.II/20180413/samgutentag.032021001510.20180413.142618.6.JPEG'
d = '/Users/samgutentag/Desktop/import/IMAGE/THUMB/CANON.EOS.7D.MARK.II/20180413/samgutentag.032021001510.20180413.142835.7.JPEG'
#
# def black_or_b(a, b):
#     diff = ImageChops.difference(a, b)
#     diff = diff.convert('L')
#     diff = diff.point(point_table)
#     new = diff.convert('RGB')
#     new.paste(b, mask=diff)
#     return new
#
# a = Image.open(a)
# b = Image.open(b)
# c = black_or_b(a, b)
# c.save('c.png')



def image_match_check(im1, im2):
    if im1.size == im2.size and im1.mode == im2.mode:
        width = im1.size[0]
        height = im1.size[1]
        for i in range(width):
            for j in range(height):
                pixel1 = im1.getpixel((i,j))
                pixel2 = im2.getpixel((i,j))
                if pixel1 != pixel2:
                    return False
    elif im1.size != im2.size or im1.mode != im2.mode:
        return False

    return True


a = '/Users/samgutentag/Desktop/import/IMAGE/THUMB/CANON.EOS.7D.MARK.II/20180413/samgutentag.032021001510.20180413.142501.0.JPEG'
a = Image.open(a)

b = '/Users/samgutentag/Desktop/import/IMAGE/THUMB/CANON.EOS.7D.MARK.II/20180413/samgutentag.032021001510.20180413.142501.2.JPEG'
b = Image.open(b)

c = '/Users/samgutentag/Desktop/import/IMAGE/THUMB/CANON.EOS.7D.MARK.II/20180413/samgutentag.032021001510.20180413.142618.6.JPEG'
c = Image.open(c)

d = '/Users/samgutentag/Desktop/import/IMAGE/THUMB/CANON.EOS.7D.MARK.II/20180413/samgutentag.032021001510.20180413.142835.7.JPEG'
d = Image.open(d)

print('same file')
result = image_match_check(a, a)
print(result)

print('slightly different')
result = image_match_check(a, b)
print(result)

print('very different')
result = image_match_check(c, d)
print(result)

print('different dims different')
result = image_match_check(a, d)
print(result)
