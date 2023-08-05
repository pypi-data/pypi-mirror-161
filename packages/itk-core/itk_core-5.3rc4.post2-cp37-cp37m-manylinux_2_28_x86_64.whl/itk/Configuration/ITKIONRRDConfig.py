depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('NrrdImageIO', 'itk::NrrdImageIO', 'itkNrrdImageIO', True),
  ('NrrdImageIOFactory', 'itk::NrrdImageIOFactory', 'itkNrrdImageIOFactory', True),
)
factories = (("ImageIO","Nrrd"),)
