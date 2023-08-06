depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('PNGImageIO', 'itk::PNGImageIO', 'itkPNGImageIO', True),
  ('PNGImageIOFactory', 'itk::PNGImageIOFactory', 'itkPNGImageIOFactory', True),
)
factories = (("ImageIO","PNG"),)
