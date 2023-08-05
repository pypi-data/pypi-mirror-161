depends = ('ITKPyBase', 'ITKCommon', )
templates = (  ('PyCommand', 'itk::PyCommand', 'itkPyCommand', False),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterISS2ISS2', False, 'itk::Image< signed short,2 >, itk::Image< signed short,2 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterISS3ISS3', False, 'itk::Image< signed short,3 >, itk::Image< signed short,3 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterISS4ISS4', False, 'itk::Image< signed short,4 >, itk::Image< signed short,4 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIUC2IUC2', False, 'itk::Image< unsigned char,2 >, itk::Image< unsigned char,2 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIUC3IUC3', False, 'itk::Image< unsigned char,3 >, itk::Image< unsigned char,3 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIUC4IUC4', False, 'itk::Image< unsigned char,4 >, itk::Image< unsigned char,4 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIUS2IUS2', False, 'itk::Image< unsigned short,2 >, itk::Image< unsigned short,2 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIUS3IUS3', False, 'itk::Image< unsigned short,3 >, itk::Image< unsigned short,3 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIUS4IUS4', False, 'itk::Image< unsigned short,4 >, itk::Image< unsigned short,4 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIF2IF2', False, 'itk::Image< float,2 >, itk::Image< float,2 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIF3IF3', False, 'itk::Image< float,3 >, itk::Image< float,3 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIF4IF4', False, 'itk::Image< float,4 >, itk::Image< float,4 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterID2ID2', False, 'itk::Image< double,2 >, itk::Image< double,2 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterID3ID3', False, 'itk::Image< double,3 >, itk::Image< double,3 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterID4ID4', False, 'itk::Image< double,4 >, itk::Image< double,4 >'),
)
factories = ()
