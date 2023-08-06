from rdkit import Chem
from rdkit.Chem import AllChem
from collections import defaultdict
from rdkit.Chem import rdFMCS
from rdkit.Chem import Draw


#needed for show_mols
from rdkit.Chem.Draw import rdMolDraw2D
import cairosvg
import math
import os

#inspired by https://github.com/rdkit/UGM_2020/blob/master/Notebooks/Landrum_WhatsNew.ipynb
#from https://colab.research.google.com/drive/1mf5Oce15L_57Yj7bWbSjdmURELMcj1eV?usp=sharing#scrollTo=Ni58g7BkkkAE



def save_mols(mols, mols_per_row = 5, size=200, min_font_size=12, legends=[], file_name=''):
  """
  The show_mols function accepts a list of molecules and their corresponding legends,
  and shows them in a grid format. The function is designed to work with the RDKit's 
  Draw.MolsToGridImage function, which allows for the creation of SVG images using 
  the Python package CairoSVG.
  
  :param mols: Used to pass a list of molecules to the function.
  :param mols_per_row=5: Used to specify the number of molecules to display in each row.
  :param size=200: Used to set the size of the image.
  :param min_font_size=12: Used to set the minimum font size for the legends.
  :param legends=[]: Used to show the name of each molecule.
  :param file_name='': Used to save the drawing as an svg file.
  :return: A matplotlib plot of the molecules.
  
  :doc-author: Julian M. Kleber
  """
    
  if legends and len(legends) < len(mols):
    print('legends is too short')
    return None

  mols_per_row = min(len(mols), mols_per_row)  
  rows = math.ceil(len(mols)/mols_per_row)
  d2d = rdMolDraw2D.MolDraw2DSVG(mols_per_row*size,rows*size,size,size)
  d2d.drawOptions().minFontSize = min_font_size
  d2d.drawOptions().legendFontSize = min_font_size
  if legends:
    d2d.DrawMolecules(mols, legends=legends)
  else:
    d2d.DrawMolecules(mols)
  d2d.FinishDrawing()

  if file_name:
    with open('d2d.svg', 'w') as f:
      f.write(d2d.GetDrawingText())
      if 'pdf' in file_name:
        cairosvg.svg2pdf(url='d2d.svg', write_to=file_name)
      else:
        cairosvg.svg2png(url='d2d.svg', write_to=file_name)
      os.remove('d2d.svg')