depends = ('ITKPyBase', 'ITKMesh', 'ITKIOMeshBase', 'ITKCommon', )
templates = (  ('OBJMeshIO', 'itk::OBJMeshIO', 'itkOBJMeshIO', True),
  ('OBJMeshIOFactory', 'itk::OBJMeshIOFactory', 'itkOBJMeshIOFactory', True),
)
factories = (("MeshIO","OBJ"),)
