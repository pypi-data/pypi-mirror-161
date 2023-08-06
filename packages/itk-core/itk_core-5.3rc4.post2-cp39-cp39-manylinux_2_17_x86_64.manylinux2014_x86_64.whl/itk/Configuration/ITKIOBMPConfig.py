depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('BMPImageIO', 'itk::BMPImageIO', 'itkBMPImageIO', True),
  ('BMPImageIOFactory', 'itk::BMPImageIOFactory', 'itkBMPImageIOFactory', True),
)
factories = (("ImageIO","BMP"),)
