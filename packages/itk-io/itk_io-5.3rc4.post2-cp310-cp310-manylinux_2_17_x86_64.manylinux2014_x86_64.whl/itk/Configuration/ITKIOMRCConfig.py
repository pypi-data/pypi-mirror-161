depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('MRCImageIO', 'itk::MRCImageIO', 'itkMRCImageIO', True),
  ('MRCImageIOFactory', 'itk::MRCImageIOFactory', 'itkMRCImageIOFactory', True),
)
factories = (("ImageIO","MRC"),)
