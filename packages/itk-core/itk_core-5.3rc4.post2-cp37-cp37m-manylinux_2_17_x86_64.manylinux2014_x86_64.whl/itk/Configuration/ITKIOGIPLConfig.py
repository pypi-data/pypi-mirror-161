depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('GiplImageIO', 'itk::GiplImageIO', 'itkGiplImageIO', True),
  ('GiplImageIOFactory', 'itk::GiplImageIOFactory', 'itkGiplImageIOFactory', True),
)
factories = (("ImageIO","Gipl"),)
