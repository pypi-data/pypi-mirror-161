depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('JPEGImageIO', 'itk::JPEGImageIO', 'itkJPEGImageIO', True),
  ('JPEGImageIOFactory', 'itk::JPEGImageIOFactory', 'itkJPEGImageIOFactory', True),
)
factories = (("ImageIO","JPEG"),)
