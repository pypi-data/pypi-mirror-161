depends = ('ITKPyBase', 'ITKIOTransformBase', )
templates = (  ('MatlabTransformIOTemplate', 'itk::MatlabTransformIOTemplate', 'itkMatlabTransformIOTemplateD', False, 'double'),
  ('MatlabTransformIOTemplate', 'itk::MatlabTransformIOTemplate', 'itkMatlabTransformIOTemplateF', False, 'float'),
  ('MatlabTransformIOFactory', 'itk::MatlabTransformIOFactory', 'itkMatlabTransformIOFactory', True),
)
factories = (("TransformIO","Matlab"),)
