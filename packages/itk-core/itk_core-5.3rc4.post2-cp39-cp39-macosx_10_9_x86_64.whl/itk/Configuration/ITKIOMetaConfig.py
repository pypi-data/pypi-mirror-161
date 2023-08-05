depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('MetaImageIO', 'itk::MetaImageIO', 'itkMetaImageIO', True),
  ('MetaImageIOFactory', 'itk::MetaImageIOFactory', 'itkMetaImageIOFactory', True),
)
factories = (("ImageIO","Meta"),)
