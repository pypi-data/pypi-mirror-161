import os

############################
# PRIVATE CONSTANTS
#############################

SCHRODINGER = os.environ.get("SCHRODINGER", "")
PELE = os.environ.get("PELE", "")
SINGULARITY_EXEC = os.environ.get("SINGULARITY_EXEC", "")
PELE_EXEC = os.environ.get("PELE_EXEC", "")
PELE_DATA = os.environ.get("PELE_DATA", "")
PELE_DOCUMENTS = os.environ.get("PELE_DOCUMENTS", "")
PELE_LICENSE = os.environ.get("PELE_LICENSE", "")
PELE_MPI_PARAMS = os.environ.get("PELE_MPI_PARAMS", "")

DEFAULT_PELE_EXEC = (
    # Priority for the default pele_exec variable:
    #    1. Environment variable (PELE_EXEC)
    #    2. Path_to_PELE + bin/Pele_mpi
    PELE_EXEC
    if PELE_EXEC
    else os.path.join(PELE, "bin/Pele_mpi")
)
DEFAULT_PELE_DATA = (
    # Priority for the default data variable:
    #    1. Environment variable (PELE_DATA)
    #    2. Path_to_PELE + Data
    PELE_DATA
    if PELE_DATA
    else os.path.join(PELE, "Data")
)
DEFAULT_PELE_DOCUMENTS = (
    # Priority for the default data variable:
    #    1. Environment variable (PELE_DOCUMENTS)
    #    2. Path_to_PELE + Documents
    PELE_DOCUMENTS
    if PELE_DOCUMENTS
    else os.path.join(PELE, "Documents")
)
DEFAULT_PELE_LICENSE = (
    # Priority for the default license variable:
    #    1. Environment variable (PELE_LICENSE)
    #    2. Path_to_PELE + licenses
    PELE_LICENSE
    if PELE_LICENSE
    else os.path.join(PELE, "licenses")
)

DEFAULT_PELE_MPI_PARAMS = PELE_MPI_PARAMS if PELE_MPI_PARAMS else ""

# DEFAULTS
# --------

COMPLEX = "complex.pdb"
RESULTS = "results"
LIG_RES = "LIG"
LIG_CHAIN = "Z"
FORCEFIELD = "OPLS2005"
PELE_CONFILE = "pele.conf"
CPUS = 140
RESTART = "true"
CLUSTERS = 40
PLATFORM_RESTART = "all"
EQ_STEPS = 50
GRIDRES = "10.0"
NATIVE = """\n
                                   {{
       
                                      "type": "rmsd",
                                      "Native": {{\n\
                                       "path":\n\
                                       "{}" }},\n\
                                      "selection": {{ "chains": {{ "names": [ "{}" ] }} }},\n\
                                      "includeHydrogens": false,\n\
                                      "doSuperposition": false,\n\
                                      "tag" : "ligandRMSD"\n\
                                   }},\n\
            """

WATER_ENERGY = """\n
                            {{
                            "type": "bindingEnergy",\n\
                            "boundPartSelection": {{ "chains": {{ "names": ["{0}"] }} }},\n\
                            "tag": "water{0}"\n\
                            }},\n\
                           """

UNBINDING = """\n
            "modeMovingBox" : "unbinding",
            "exitCondition" : {{
                "type" : "metricMultipleTrajectories",
                "params" : {{
                       "metricCol" : {},
                       "exitValue" : {},
                       "condition" : "{}",
                       "numberTrajectories" : {}
            }}
            }},
            """

DISTANCE_ATOMS = """\n
                     {{
                     "type":"com_distance",
                     "tag":"{metric_name}",
                     "selection_group_1":{{
                     "{atom1_tag}": {{ "ids":["{atom1}"]}}
                     }},
                     "selection_group_2":{{
                     "{atom2_tag}": {{ "ids":["{atom2}"]}}
                     }}
                     }},
                     """

LOCAL_NONBONDING_ENERGY = """\n
                     {{
                     "type": "localNonBondingEnergy",
                     "selection": {{ "links": {{ "ids": ["{}"] }} }},
                      "radius": {}
                      }},
"""

DISTANCE_ATOMS_TAG = """\n
                     {{
                     "type":"com_distance",
                     "tag":"{0}",
                     "selection_group_1":{{
                     "atoms": {{ "ids":["{1}"]}}
                     }},
                     "selection_group_2":{{
                     "atoms": {{ "ids":["{2}"]}}
                     }}
                     }},
                     """

ANGLE_ATOMS_TAG = """\n
                     {{
                     "type":"atomsAngle",
                     "tag":"{0}",
                     "selection_group_1":{{
                     "atoms": {{ "ids":["{1}"]}}
                     }},
                     "selection_group_2":{{
                     "atoms": {{ "ids":["{2}"]}}
                     }},
                     "selection_group_3":{{
                     "atoms": {{ "ids":["{3}"]}}
                     }}
                     }},
                     """

BOX = """\n
                "Box": {{
                    "type": "sphericalBox",
                    "radius": {0},
                    "fixedCenter": {1}
                }},
"""

WATER = """\n
         "WaterPerturbation":
         {{
             "watersToPerturb": {{ "links": {{ "ids": [ {} ] }} }},
             "parameters":
             {{
                 {}
                 "temperature": {},
                 "numberOfStericTrials": {},
                 "overlapFactor": {},
                 "COMConstraintConstant": {}
             }},
             "waterSites": {}
         }}, 
"""

PCA = """\n\t\t\t"preloadedModesIn" : "{}","""

SIDECHAIN_PERTURBATION = """\n
         "SideChainPerturbation":{
                        "sideChainsToPerturb": { "links": {"ids": ["$COVALENT_RESIDUE"] } },
                        "parameters":{
                                "overlapFactor": $OVERLAP,
                                "numberOfTrials": $TRIALS,
                                $REFINEMENT_ANGLE
                                "maxTrialsForAtLeastOne": $MAXTRIALSFORONE,
                                "atLeastOneSelectedTrial": true 
                        }
                },
"""

SELECTION_TO_PERTURB = (
    '"selectionToPerturb" : { "chains" : { "names" : [ "$CHAIN" ] } },'
)

PERTURBATION = """\n
          "Perturbation": {
                $BOX
                "perturbationType":"naive",
                "translationDirection": "steered",
                "rotationAngles": "nonCoupled",
                "parameters": {
                    "numberOfStericTrials": $STERIC_TRIALS,
                    "steeringUpdateFrequency": $STEERING,
                    "overlapFactor": $OVERLAP
                }          
            },
"""

CONFORMATION_PERTURBATION = '''\n
        "ConformationPerturbation":{
            "parameters": {
                "overlapFactor": $OVERLAP_CONFORMATION
            }
        },
'''

BE = """\n
                        { "type": "bindingEnergy",
                           "boundPartSelection": { "chains": { "names": ["$CHAIN"] } }
                        },
"""

SASA = """\n
                        { "type": "sasa",
                           "tag": "sasaLig",
                           "selection": { "chains": { "names": ["$CHAIN"] } }
                        },
"""

SASA_COVALENT = """\n
                        {{ "type": "sasa",
                           "tag": "sasaLig",
                           "selection": {{ "links": {{ "ids": ["{}"] }} }}
                        }},
"""

INTERACTION_RESTRICTIONS = """
\n,
"interactionRestrictions":
[
	"{0}"
]
"""

LIGAND = '"ligandResname" : "$LIG_RES",'

# PPI waters
water_O = "HETATM {}  OW  HOH {}{:>4}     {}  1.00  0.00           O\n"
water_H1 = "HETATM {}  1HW HOH {}{:>4}     {}  1.00  0.00           H\n"
water_H2 = "HETATM {}  2HW HOH {}{:>4}     {}  1.00  0.00           H\n"
water = [water_O, water_H1, water_H2]

# Amino acids
AMINO_ACIDS = [
    "VAL",
    "ASN",
    "GLY",
    "LEU",
    "ILE",
    "SER",
    "ASP",
    "LYS",
    "MET",
    "GLN",
    "TRP",
    "ARG",
    "ALA",
    "THR",
    "PRO",
    "PHE",
    "GLU",
    "HIS",
    "HIP",
    "TYR",
    "CYS",
    "HID",
]

# Nucleotides
NUCLEOTIDES = ["G", "U", "A", "C"]

# Metals

metals = [
    "LI",
    "BE",
    "NA",
    "MG",
    "AL",
    "K",
    "CA",
    "SC",
    "TI",
    "V",
    "CR",
    "MN",
    "FE",
    "CO",
    "NI",
    "CU",
    "ZN",
    "GA",
    "RB",
    "SR",
    "Y",
    "ZR",
    "NB",
    "MO",
    "TC",
    "RU",
    "RH",
    "PD",
    "AG",
    "CD",
    "IN",
    "SN",
    "CS",
    "BA",
    "LA",
    "CE",
    "PR",
    "ND",
    "PM",
    "SM",
    "EU",
    "GD",
    "TB",
    "DY",
    "HO",
    "ER",
    "TM",
    "YB",
    "LU",
    "HF",
    "TA",
    "W",
    "RE",
    "OS",
    "IR",
    "PT",
    "AU",
    "HG",
    "TL",
    "PB",
    "BI",
    "PO",
    "FR",
    "RA",
    "AC",
    "TH",
    "PA",
    "U",
    "NP",
    "PU",
    "AM",
    "CM",
    "BK",
    "CF",
    "ES",
    "FM",
    "MD",
    "NO",
    "LR",
    "RF",
    "DB",
    "SG",
    "BH",
    "HS",
    "MT",
    "DS",
    "RG",
    "CN",
    "NH",
    "FL",
    "MC",
    "LV",
]

# Group 9 ions
ions9 = ["F", "CL", "BR", "I", "AT"]

# FLAGS WITH ATOM STRINGS
atom_string_flags = [
    "atom_dist",
    "final_site",
    "orthosteric_site",
    "initial_site",
    "center_of_interface",
]

# TEMPLATE KEYWORDS
# ------------------

GLIDE_TEMPLATE = ["INPUT", "PRECISION"]

# PATHS
# -------

DIR = os.path.dirname(os.path.dirname(__file__))
ADAPTIVE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "Adaptive/clusterAdaptiveRun.py")
)

# MESSAGES & ERRORS
# -----------------

CLUSTER_ERROR = "Number of cpus ({}) must be bigger than clusters ({})"
SYSTEM = "\n\t**Missing residues found {}\n\t**Gaps found {}\n\t**Metals found {}"

constraint_levels = {
    0: {"ca_constr": 0.0, "terminal_constr": 0.0, "ca_interval": 0},
    1: {"ca_constr": 0.5, "terminal_constr": 5.0, "ca_interval": 10},
    2: {"ca_constr": 2.5, "terminal_constr": 5.0, "ca_interval": 8},
    3: {"ca_constr": 5.0, "terminal_constr": 5.0, "ca_interval": 5},
}

custom_colors = (
    (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
    (0.6823529411764706, 0.7803921568627451, 0.9098039215686274),
    (1.0, 0.4980392156862745, 0.054901960784313725),
    (1.0, 0.7333333333333333, 0.47058823529411764),
    (0.17254901960784313, 0.6274509803921569, 0.17254901960784313),
    (0.596078431372549, 0.8745098039215686, 0.5411764705882353),
    (0.8392156862745098, 0.15294117647058825, 0.1568627450980392),
    (1.0, 0.596078431372549, 0.5882352941176471),
    (0.5803921568627451, 0.403921568627451, 0.7411764705882353),
    (0.7725490196078432, 0.6901960784313725, 0.8352941176470589),
    (0.5490196078431373, 0.33725490196078434, 0.29411764705882354),
    (0.7686274509803922, 0.611764705882353, 0.5803921568627451),
    (0.8901960784313725, 0.4666666666666667, 0.7607843137254902),
    (0.9686274509803922, 0.7137254901960784, 0.8235294117647058),
    (0.7372549019607844, 0.7411764705882353, 0.13333333333333333),
    (0.8588235294117647, 0.8588235294117647, 0.5529411764705883),
    (0.09019607843137255, 0.7450980392156863, 0.8117647058823529),
    (0.6196078431372549, 0.8549019607843137, 0.8980392156862745),
)

# INTER STEP LOGGER
#-------------------
INTERSTEPLOGGER = ''',
            "useInterStepLogger": true'''

# MINIMUM STEPS
#-------------------
MINIMUMSTEPS = '''"activateMinimumSteps": true,'''


# ANALYSIS
# ---------
# Top cluster selection - mapping between table metrics and YAML arguments
metric_top_clusters_criterion = {
    "total_25_percentile": "currentEnergy 25-percentile",
    "total_5_percentile": "currentEnergy 5-percentile",
    "total_mean": "currentEnergy mean",
    "total_min": "currentEnergy minb",
    "interaction_25_percentile": "Binding Energy 25-percentile",
    "interaction_5_percentile": "Binding Energy 5-percentile",
    "interaction_mean": "Binding Energy mean",
    "interaction_min": "Binding Energy min",
    "population": "Population",
}

# Cluster representatives selection - mapping between table metrics and
# YAML arguments
cluster_representatives_criterion = {
    "total_25_percentile": "currentEnergy 25-percentile",
    "total_5_percentile": "currentEnergy 5-percentile",
    "total_mean": "currentEnergy mean",
    "total_min": "currentEnergy min",
    "interaction_25_percentile": "Binding Energy 25-percentile",
    "interaction_5_percentile": "Binding Energy 5-percentile",
    "interaction_mean": "Binding Energy mean",
    "interaction_min": "Binding Energy min",
    "local_nonbonding_energy": "LocalNonBondingEnergy",
}

# LIGAND PARAMETERIZATION
# ------------------------
# Templates in PELE Data folder, no need to parametrize those
in_pele_data = ["caz", "clz", "cuiz", "cuz", "hohz", "mgz", "mnz", "naz", "spcz", "znz"]


refinement_angle = '"refinementAngle": {},'

CONFORMATION_FREQUENCY = '\n"conformationPerturbationFrequency": {},'

version_header = """
PELE Platform {}
--------------------------
Nostrum Biodiscovery SL
All rights reserved, 2021.
"""

plotter_version_header = """
PELE Platform Plotter {}
-------------------------
Nostrum Biodiscovery SL
All rights reserved, 2021.
"""

converter_version_header = """
PELE Platform Converter {}
---------------------------
Nostrum Biodiscovery SL
All rights reserved, 2021.
"""

pathway_extractor_version_header = """
PELE Platform Pathway Extractor {}
-----------------------------------
Nostrum Biodiscovery SL
All rights reserved, 2021.
"""
