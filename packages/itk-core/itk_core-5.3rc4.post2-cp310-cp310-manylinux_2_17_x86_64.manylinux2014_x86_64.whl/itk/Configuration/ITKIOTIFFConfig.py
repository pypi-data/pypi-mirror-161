depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('TIFFImageIO', 'itk::TIFFImageIO', 'itkTIFFImageIO', True),
  ('TIFFImageIOFactory', 'itk::TIFFImageIOFactory', 'itkTIFFImageIOFactory', True),
)
factories = (("ImageIO","TIFF"),)
