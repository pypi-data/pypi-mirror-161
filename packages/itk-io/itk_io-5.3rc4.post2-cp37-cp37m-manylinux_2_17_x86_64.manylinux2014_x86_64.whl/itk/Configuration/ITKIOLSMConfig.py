depends = ('ITKPyBase', 'ITKIOTIFF', 'ITKIOImageBase', )
templates = (  ('LSMImageIO', 'itk::LSMImageIO', 'itkLSMImageIO', True),
  ('LSMImageIOFactory', 'itk::LSMImageIOFactory', 'itkLSMImageIOFactory', True),
)
factories = (("ImageIO","LSM"),)
