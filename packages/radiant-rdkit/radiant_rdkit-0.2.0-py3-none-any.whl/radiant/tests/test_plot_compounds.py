from radiant.plot_compounds import save_mols

def test_plot_compounds(): 
    """
    The test_plot_compounds function plots a set of compounds in the same figure.
    It takes as input a list of smiles strings and plots them in the same figure.
    
    :return: A list of matplotlib figures.
    
    :doc-author: Trelent
    """
    from rdkit import Chem
    
    smiles_list = ['c1ccccc1','Cc1occc1C(=O)Nc2ccccc2', 'CN1CCN(S(=O)(C2=CC=C(OCC)C(C3=NC4=C(N(C)N=C4CCC)C(N3)=O)=C2)=O)CC1']
    mols = [Chem.MolFromSmiles(x) for x in smiles_list]
    legends = ['1', '2', '3']

    save_mols(mols, legends=legends, file_name='radiant/tests/test.png')
    save_mols(mols, legends=legends, file_name='radiant/tests/test_large.png', min_font_size=30)