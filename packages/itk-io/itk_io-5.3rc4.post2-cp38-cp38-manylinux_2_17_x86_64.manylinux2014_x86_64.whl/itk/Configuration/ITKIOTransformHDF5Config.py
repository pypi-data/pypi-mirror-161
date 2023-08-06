depends = ('ITKPyBase', 'ITKIOTransformBase', )
templates = (  ('HDF5CommonPathNames', 'itk::HDF5CommonPathNames', 'itkHDF5CommonPathNames', False),
  ('HDF5TransformIOTemplate', 'itk::HDF5TransformIOTemplate', 'itkHDF5TransformIOTemplateD', False, 'double'),
  ('HDF5TransformIOTemplate', 'itk::HDF5TransformIOTemplate', 'itkHDF5TransformIOTemplateF', False, 'float'),
  ('HDF5TransformIOFactory', 'itk::HDF5TransformIOFactory', 'itkHDF5TransformIOFactory', True),
)
factories = (("TransformIO","HDF5"),)
