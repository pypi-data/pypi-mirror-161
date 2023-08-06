depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('BioRadImageIO', 'itk::BioRadImageIO', 'itkBioRadImageIO', True),
  ('BioRadImageIOFactory', 'itk::BioRadImageIOFactory', 'itkBioRadImageIOFactory', True),
)
factories = (("ImageIO","BioRad"),)
