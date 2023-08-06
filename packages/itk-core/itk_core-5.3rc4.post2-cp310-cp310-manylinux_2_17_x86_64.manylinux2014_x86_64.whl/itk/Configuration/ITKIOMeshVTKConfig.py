depends = ('ITKPyBase', 'ITKMesh', 'ITKIOMeshBase', 'ITKCommon', )
templates = (  ('VTKPolyDataMeshIO', 'itk::VTKPolyDataMeshIO', 'itkVTKPolyDataMeshIO', True),
  ('VTKPolyDataMeshIOFactory', 'itk::VTKPolyDataMeshIOFactory', 'itkVTKPolyDataMeshIOFactory', True),
)
factories = (("MeshIO","VTKPolyData"),)
