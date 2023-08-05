depends = ('ITKPyBase', 'ITKMesh', 'ITKIOMeshBase', 'ITKCommon', )
templates = (  ('OFFMeshIO', 'itk::OFFMeshIO', 'itkOFFMeshIO', True),
  ('OFFMeshIOFactory', 'itk::OFFMeshIOFactory', 'itkOFFMeshIOFactory', True),
)
factories = (("MeshIO","OFF"),)
