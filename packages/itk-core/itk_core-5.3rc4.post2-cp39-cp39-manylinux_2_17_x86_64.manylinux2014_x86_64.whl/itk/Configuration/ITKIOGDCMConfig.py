depends = ('ITKPyBase', 'ITKIOImageBase', 'ITKCommon', )
templates = (  ('GDCMImageIOFactory', 'itk::GDCMImageIOFactory', 'itkGDCMImageIOFactory', True),
  ('GDCMSeriesFileNames', 'itk::GDCMSeriesFileNames', 'itkGDCMSeriesFileNames', True),
  ('GDCMImageIOEnums', 'itk::GDCMImageIOEnums', 'itkGDCMImageIOEnums', False),
  ('GDCMImageIO', 'itk::GDCMImageIO', 'itkGDCMImageIO', True),
)
factories = (("ImageIO","GDCM"),)
