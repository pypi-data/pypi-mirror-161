depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('MINCImageIO', 'itk::MINCImageIO', 'itkMINCImageIO', True),
  ('MINCImageIOFactory', 'itk::MINCImageIOFactory', 'itkMINCImageIOFactory', True),
)
factories = (("ImageIO","MINC"),)
