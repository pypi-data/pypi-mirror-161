depends = ('ITKPyBase', 'ITKMesh', 'ITKIOMeshBase', 'ITKCommon', )
templates = (  ('BYUMeshIO', 'itk::BYUMeshIO', 'itkBYUMeshIO', True),
  ('BYUMeshIOFactory', 'itk::BYUMeshIOFactory', 'itkBYUMeshIOFactory', True),
)
factories = (("MeshIO","BYU"),)
