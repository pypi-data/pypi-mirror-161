depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('Bruker2dseqImageIO', 'itk::Bruker2dseqImageIO', 'itkBruker2dseqImageIO', True),
  ('Bruker2dseqImageIOFactory', 'itk::Bruker2dseqImageIOFactory', 'itkBruker2dseqImageIOFactory', True),
)
factories = (("ImageIO","Bruker2dseq"),)
