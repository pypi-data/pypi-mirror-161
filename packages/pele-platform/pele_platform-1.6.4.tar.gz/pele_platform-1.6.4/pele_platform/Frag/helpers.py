import os
import random
import string
import pele_platform.Frag.fragments as fr
import pele_platform.Frag.atoms as at
import pele_platform.Frag.checker as ch
import pele_platform.Errors.custom_errors as ce

from rdkit import Chem
import rdkit.Chem.rdmolops as rd
import rdkit.Chem.rdchem as rc

def _search_core_fragment_linker(ligand,
                                 ligand_core,
                                 result=0,
                                 check_symmetry=False,
                                 frag_core_atom=None):
    """
    Given mol1 and mol2 return the linker atoms.

    Parameters
    ----------
    ligand : RDKit molecule object
             Ligand to grow during the simulation.

    ligand_core : RDKit molecule object
                  Common structure of each grown ligand.
    result : int
             Index to extract core atoms from the substructure search.

    check_symmetry : bool
                     Check the symmetry of the ligand.

    Returns
    -------
    atom_core_idx : int
                    Atom of the core attached to the fragment.

    atoms_core : tuple
                 Common atoms from original ligand and grown ligand.

    atom_fragment : int
                    Atom of the fragment attached to the core.

    Raises
    ------
    IndexError
        If the substructure search fails.
    """
    substructure_results = ligand.GetSubstructMatches(ligand_core)

    try:
        print("Running substructure search on {}...".format(ligand.GetProp('_Name')))
        core_atoms = substructure_results[result]
        print("RESULT SUBSTRUCTURE", core_atoms)
    except IndexError:
        raise IndexError(
            "Make sure core from pdb and full fragment are the same. Make sure that both core and fragment have "
            "correctly defined aromatic bonds. Also, all fragments must have different molecule name.")

    # Sometimes substructure search messes up symmetry. Check that!
    if check_symmetry:
        core_atoms = ch.check_substructure_match(ligand, ligand_core, core_atoms)
    for atom in ligand.GetAtoms():
        if atom.GetIdx() in core_atoms or atom.GetAtomicNum() == 1:
            continue
        else:
            atoms_bonded = atom.GetNeighbors()
            for neighbour in atoms_bonded:
                if neighbour.GetIdx() in core_atoms:
                    return core_atoms.index(neighbour.GetIdx()), core_atoms, atom.GetIdx()


def _build_fragment_from_complex(complex,
                                 residue,
                                 ligand,
                                 ligand_core,
                                 result=0,
                                 substructure=True,
                                 symmetry=False,
                                 frag_core_atom=None):
    """

    Parameters
    ----------
    complex : str
              Path of PDB file with protein-ligand complex.

    residue : str
              Residue name.

    ligand : RDKit molecule object
             Ligand to grow during the simulation.

    ligand_core : RDKit molecule object
                  Common structure of each grown ligand.

    result : int
             Index to extract core atoms from the substructure search.

    substructure : bool
                   Delete core for full ligand with substructure.

    symmetry : bool
               Check the symmetry of the ligand.

    Returns
    -------
    fragment : RDKit molecule object
               Grown ligand with deleted core atoms.

    old_atoms : list
                Idx for each atom of grown ligand without core.

    hydrogen_core : pele_platform.Frag.atoms.Atom
                    Hydrogen core attached to linking atom.

    atom_core : pele_platform.Frag.atoms.Atom
                Atom object of the hydrogen core atom attached to linking atom.

    atom_fragment : int
                    Atom of the fragment attached to the core.

    mapping : dict
              Mapping of Idx for old atoms and full fragment atoms.

    correct : bool
              Checks if the fragment is correct (fragment size, chirality, missing hydrogens)

    Raises
    ------
    TypeError
        If the core and ligand are the same molecule.
    """

    # Retrieve atom core linking fragment
    try:
        atom_core_idx, atoms_core, atom_fragment = _search_core_fragment_linker(ligand, ligand_core, result, symmetry, frag_core_atom)
        print("ATOM OF FRAGMENT ATTACHED TO CORE:", atom_fragment)
        print("ATOM OF CORE ATTACHED TO FRAGMENT:", atom_core_idx)
    except TypeError:
        raise ce.SameMolecule("Core and ligand are the exact same molecule. Check your inputs.")
    atom_core = at.Atom(ligand_core, atom_core_idx)
    mol = Chem.MolFromPDBFile(complex, removeHs=False)

    # Retrieve hydrogen core attach to linking atom
    original = rd.SplitMolByPDBResidues(mol)[residue]
    hydrogen_core_idx = \
        [atom.GetIdx() for atom in original.GetAtomWithIdx(atom_core_idx).GetNeighbors() if atom.GetAtomicNum() == 1][0]
    hydrogen_core = at.Atom(original, hydrogen_core_idx)

    # Delete core for full ligand with substructure and if it fails manually
    if substructure:
        fragment = rd.DeleteSubstructs(ligand, ligand_core)
        new_mol = rc.EditableMol(fragment)
        for atom in reversed(fragment.GetAtoms()):
            neighbours = atom.GetNeighbors()
            if len(neighbours) == 0 and atom.GetAtomicNum() == 1:
                new_mol.RemoveAtom(atom.GetIdx())
    else:
        new_mol = rc.EditableMol(ligand)

        for atom in reversed(atoms_core):
            new_mol.RemoveAtom(atom)

        for atom in reversed(new_mol.GetMol().GetAtoms()):
            neighbours = atom.GetNeighbors()
            if len(neighbours) == 0 and atom.GetAtomicNum() == 1:
                new_mol.RemoveAtom(atom.GetIdx())
    print("FRAGMENT ATOMS", [atom.GetIdx() for atom in new_mol.GetMol().GetAtoms()])

    # Add missing hydrogen to full ligand and create pdb differently depending on the previous step
    fragment = new_mol.GetMol()
    old_atoms = [atom.GetIdx() for atom in fragment.GetAtoms() if atom.GetAtomicNum() != 1]
    new_atoms = [atom.GetIdx() for atom in ligand.GetAtoms() if
                 atom.GetIdx() not in atoms_core and atom.GetAtomicNum() != 1]
    print("old_atoms", old_atoms, "new_atoms", new_atoms)
    mapping = {new_atom: old_atom for new_atom, old_atom in zip(new_atoms, old_atoms)}
    atom_fragment_mapped = mapping[atom_fragment]

    # Retrieve all atom idxs before adding hydrogen to fragment_atom
    fragment_atoms_wo_hydrogen = [atom.GetIdx() for atom in fragment.GetAtoms()]

    fragment = Chem.AddHs(fragment, False, True)
    correct = _check_fragment(fragment, ligand, mapping, atom_fragment, atom_fragment_mapped, ligand_core)
    Chem.MolToPDBFile(fragment, "int0.pdb")
    assert len(old_atoms) == len(new_atoms)
    return fragment, old_atoms, hydrogen_core, atom_core, atom_fragment, mapping, correct, fragment_atoms_wo_hydrogen


def random_string(string_length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def _retrieve_fragment(fragment,
                       old_atoms,
                       atom_core,
                       hydrogen_core,
                       atom_fragment,
                       mapping,
                       fragment_atoms_wo_hydrogen):
    """

    Parameters
    ----------
    old_atoms : list
                Idx for each atom of grown ligand without core.

    atom_core : pele_platform.Frag.atoms.Atom
                Atom object of the hydrogen core atom attached to linking atom.

    hydrogen_core : pele_platform.Frag.atoms.Atom
                    Hydrogen core attached to linking atom.

    atom_fragment : int
                    Atom of the fragment attached to the core.

    mapping : dict
              Mapping of Idx for old atoms and full fragment atoms.

    Returns
    -------
    fragment : pele_platform.Frag.fragments.Fragment
               Fragment grown to the ligand during the simulation.

    Raises
    ------
    IndexError
        If the hydrogen detection failed.
    """
    from rdkit import Chem

    # Get new added hydrogen
    try:
        # Identify idx from added hydrogen
        added_hydrogen_idx = [atom.GetIdx() for atom in fragment.GetAtoms() if atom.GetIdx() not in fragment_atoms_wo_hydrogen][0]
        no_hydrogens = False
        # Get fragment atom attached to newly added hydrogen
        atom_fragment_idx = fragment.GetAtomWithIdx(added_hydrogen_idx).GetNeighbors()[0].GetIdx()
    except IndexError:
        print("Hydrogen detection failed won't have into account stereochemistry")
        added_hydrogen_idx = 0
        no_hydrogens = True
        atom_fragment_idx = mapping[atom_fragment]
        print("Final atom fragment", atom_fragment_idx)

    # Save fragment
    # string = random_string(8)
    # fragment_filename = fragment.GetProp("_Name").replace(" ", "_") + string + ".pdb"
    fragment_name = fragment.GetProp("_Name").replace(" ", "_")
    fragment_filename = fragment_name + ".pdb"
    while os.path.exists(fragment_filename):
        fragment_filename = os.path.splitext(fragment_filename)[0]
        last_field = fragment_filename.split('_')[-1]

        if last_field.isdigit() and last_field != fragment_name:
            next_int = int(last_field) + 1
            fragment_filename = '_'.join(fragment_filename.split('_')[:-1])
        else:
            next_int = 1

        fragment_filename = fragment_filename + f"_{next_int}.pdb"

    Chem.MolToPDBFile(fragment, fragment_filename)
    fragment = Chem.MolFromPDBFile(fragment_filename, removeHs=False)
    added_hydrogen = at.Atom(fragment, added_hydrogen_idx)
    atom_fragment_attach_to_hydrogen = at.Atom(fragment, atom_fragment_idx)

    # Build fragment object
    fragment = fr.Fragment(fragment_filename, atom_fragment_attach_to_hydrogen,
                           added_hydrogen, atom_core, hydrogen_core, no_hydrogens)
    return fragment


def _check_fragment(fragment,
                    ligand,
                    mapping,
                    atom_fragment,
                    atom_fragment_mapped,
                    ligand_core):
    """
    Checks if the fragment is correct. Adds missing hydrogens and checks the fragment size and chirality.

    Parameters
    ----------
    fragment : rdkit.Chem.rdchem.Mol
               Fragment grown to the ligand during the simulation.

    ligand : rdkit.Chem.rdchem.Mol
             Input ligand of the simulation.

    mapping : dict
              Mapping of Idx for old atoms and full fragment atoms.

    atom_fragment : int
                    Atom of the fragment attached to the core.

    atom_fragment_mapped : int
                           Atom of the fragment attached to the core mapped.

    ligand_core : rdkit.Chem.rdchem.Mol
                  Core of the growing result.

    Returns
    -------
    correct : bool
              If true, the fragment is correct.

    """

    from rdkit import Chem

    frag_neighbours = fragment.GetAtomWithIdx(atom_fragment_mapped).GetNeighbors()
    lig_neighbours = ligand.GetAtomWithIdx(atom_fragment).GetNeighbors()

    # Check, if atom_fragments has correct number of hydrogens by comparing to the original ligand
    if len(frag_neighbours) < len(lig_neighbours):
        to_add = len(lig_neighbours) - len(frag_neighbours)
        fragment.GetAtomWithIdx(atom_fragment_mapped).SetNumExplicitHs(to_add)

    # Add hydrogens
    fragment = Chem.AddHs(fragment, False, True)

    # Compare chirality
    lig_chir = Chem.FindMolChiralCenters(ligand, force=True, includeUnassigned=True)
    frag_chir = Chem.FindMolChiralCenters(fragment, force=True, includeUnassigned=True)

    # Check fragment size
    ligand_len = ligand.GetNumHeavyAtoms()
    frag_len = fragment.GetNumHeavyAtoms()
    core_len = ligand_core.GetNumHeavyAtoms()

    if ligand_len - core_len == frag_len:
        if lig_chir and frag_chir:
            for lg, fg in zip(lig_chir, frag_chir):
                # If chirality different or atom number different --> ? as incorrect
                if lg[0] in mapping and fg[0] in mapping:
                    if lg[1] != fg[1] or mapping[lg[0]] != fg[0]:
                        if lg[1] != "?" and fg[1] != "?":
                            correct = False
                            break
                        else:
                            correct = True
                    else:
                        correct = True
                else:
                    correct = True
        else:
            correct = True
    else:
        correct = False

    return correct
