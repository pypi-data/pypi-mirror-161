depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('VTKImageIO', 'itk::VTKImageIO', 'itkVTKImageIO', True),
  ('VTKImageIOFactory', 'itk::VTKImageIOFactory', 'itkVTKImageIOFactory', True),
)
factories = (("ImageIO","VTK"),)
