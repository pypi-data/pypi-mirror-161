import os
import shutil
import frag_pele
from peleffy.topology import Molecule, Topology, RotamerLibrary
from peleffy.forcefield import OpenForceField, OPLS2005ForceField
from peleffy.template import Impact
from peleffy.utils import get_data_file_path
import frag_pele.Covalent.correct_template_of_backbone_res as cov
import frag_pele.constants as c
from frag_pele.Helpers import folder_handler
from frag_pele.Helpers.plop_rot_temp import prepare_pdb
from peleffy.utils import Logger

logger = Logger()
logger.set_level('INFO')
logger.set_file_handler('peleffy.log')

def create_template_path(path, name, forcefield='OPLS2005', protein=False, templates_generated=False):
    if templates_generated:
        templ_string = "templates_generated"
    else:
        templ_string = ""
    if forcefield == 'OPLS2005' and protein:
        path = os.path.join(path, 
                            'DataLocal/Templates/OPLS2005/Protein',
                            templ_string, name.lower())
    if forcefield == 'OFF' and protein:
        path = os.path.join(path, 
                            'DataLocal/Templates/OpenFF/Protein',
                            templ_string, aminoacid.lower())
    if forcefield == 'OPLS2005' and not protein:
        path = os.path.join(path,         
                            'DataLocal/Templates/OPLS2005/HeteroAtoms',
                            templ_string, name.lower()+"z")
    if forcefield == 'OFF' and not protein:
        path = os.path.join(path,
                            'DataLocal/Templates/OpenFF/Parsley',
                            templ_string, name.lower()+"z")
    return path

def get_template_and_rot(pdb, complex_pdb, c_chain, forcefield='OPLS2005', template_name='grw', aminoacid=False, outdir='.', rot_res=30,
                         contrained_atoms=None, aminoacid_type=None, sch_path=c.SCHRODINGER, original_pdb=None):
    p, pdb_name = os.path.split(pdb)
    out = pdb_name.split(".pdb")[0] + "_p" + ".pdb"
    currdir = os.getcwd()
    pdb_dir = os.path.dirname(pdb)
    # Check if the residue is an amino-acid from the library
    path = os.path.dirname(frag_pele.__file__)
    aa_pdb = os.path.join(path, f"Templates/Aminoacids/{aminoacid_type}.pdb")
    if not os.path.exists(aa_pdb) or aminoacid_type == None:
        output_pdb = os.path.join(pdb_dir,out)
        print(f"{aa_pdb} does not exist, using {output_pdb} instead")
    else:
        output_pdb = aa_pdb
    # Check if the output path exist to dont repeat calculations
    if not os.path.exists(output_pdb):
        os.chdir(pdb_dir)
        prepare_pdb(pdb_in=pdb_name, 
                    pdb_out=out, 
                    sch_path=sch_path)
        os.chdir(currdir)
    os.environ['SCHRODINGER'] = sch_path
    template_path = create_template_path(outdir, template_name, forcefield, aminoacid, True)
    if aminoacid:
        print("Aminoacid template")
        if not contrained_atoms:
            contraints = [' CA ', ' C  ', ' N  ']
        else:
            contraints = contrained_atoms
        m = Molecule(output_pdb, 
                     core_constraints=contraints,
                     rotamer_resolution=rot_res)
        print(f"Using PDB from {output_pdb} to generate the template!")
    else:
        print("Heteroatom template")
        if not contrained_atoms:
            m = Molecule(output_pdb,
                         rotamer_resolution=rot_res)
        else:
            m = Molecule(output_pdb,
                         core_constraints=contrained_atoms,
                         rotamer_resolution=rot_res)
    if forcefield == 'OPLS2005':
        ff = OPLS2005ForceField()
    if forcefield == 'OFF': # Not tested yet
        ff = OpenForceField('openff_unconstrained-2.0.0.offxml')
    parameters = ff.parameterize(m)
    topology = Topology(m, parameters)

    impact = Impact(topology)
    impact.to_file(template_path) 
    print("Template in {}.".format(template_path))
    rot_path = os.path.join(outdir, 
                            "DataLocal/LigandRotamerLibs/{}.rot.assign".format(template_name.upper()))
    rotamer_library = RotamerLibrary(m)
    rotamer_library.to_file(rot_path)
    print("Rotamer library stored in {}".format(rot_path))

    # Generate parameters for the rest of hetero molecules found in the PDB
    from peleffy.utils.input import PDBFile

    if original_pdb is not None and os.path.isfile(original_pdb):
        pdb_file = PDBFile(original_pdb)
    else:
        pdb_file = PDBFile(complex_pdb)

    molecules = pdb_file.get_hetero_molecules()

    topologies = [topology, ]

    # Load quickly core molecule to discard it later
    mols = pdb_file._extract_molecules_from_chain(c_chain, 30, True, True, [])

    if len(mols) > 0:
        core_mol_tag = mols[0].tag
    else:
        core_mol_tag = None

    for molecule in molecules:
        # Skip ligand since it has already been parameterized
        if core_mol_tag == molecule.tag:
            continue

        parameters = ff.parameterize(molecule)
        topology = Topology(molecule, parameters)
        impact = Impact(topology)
        impact.to_file(os.path.join(outdir,
                                    f"DataLocal/Templates/OpenFF/Parsley/{molecule.tag.lower()}z"))

        topologies.append(topology)

    # Generate OBC solvent parameters
    if forcefield == 'OFF': # Not tested yet
        from peleffy.solvent import OBC2
        solvent = OBC2(topologies)
        solvent.to_file(os.path.join(outdir,
                                     "DataLocal/OBC/ligandParams.txt"))


def add_off_waters_to_datalocal(outdir):
    path = os.path.dirname(frag_pele.__file__)
    shutil.copy(os.path.join(path, "Templates/OFF/hohz"),
                os.path.join(outdir, "DataLocal/Templates/OpenFF/Parsley/hohz"))
 
def get_datalocal(pdb, complex_pdb, c_chain, outdir='.', forcefield='OPLS2005', template_name='grw', aminoacid=False, rot_res=30,
                  constrainted_atoms=None, aminoacid_type=None, sch_path=c.SCHRODINGER, original_pdb=None):
    folder_handler.check_and_create_DataLocal(working_dir=outdir)
    get_template_and_rot(pdb, complex_pdb, c_chain, forcefield=forcefield, template_name=template_name,
                         aminoacid=aminoacid, outdir=outdir, rot_res=rot_res,
                         contrained_atoms=constrainted_atoms, aminoacid_type=aminoacid_type,
                         sch_path=sch_path,
                         original_pdb=original_pdb)
#    if forcefield == 'OFF':
#        add_off_waters_to_datalocal(outdir)
