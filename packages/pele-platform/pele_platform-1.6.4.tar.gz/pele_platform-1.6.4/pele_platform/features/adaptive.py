import os
import pele_platform.constants.constants as cs
import pele_platform.constants.pele_params as pcs

from copy import deepcopy

"""
Description of the file: This file specifies what files to use
for each job.

"""

SOFTWARE_CONSTANTS = {
    "adap_ex_output": None,
    "ad_ex_temp": os.path.join("{}", "adaptive.conf"),
    "pele_exit_temp": os.path.join("{}", "pele.conf"),
    "folders": [
        "",
        "DataLocal/Templates/OPLS2005/HeteroAtoms/",
        "DataLocal/Templates/AMBER99sb/HeteroAtoms/",
        "DataLocal/Templates/AMBER99sbBSC0/HeteroAtoms/",
        "DataLocal/LigandRotamerLibs",
        "DataLocal/OBC",
    ],
    "file_names": ["adaptive.conf", "pele.conf"],
    "files": [
        os.path.join(cs.DIR, "Templates/template_adaptive.conf"),
        os.path.join(cs.DIR, "Templates/pele_template.conf"),
    ],
    "simulation_params": {
        "out_in": {
            "spawning_type": "inverselyProportional",
            "density": "continuous",
            "simulation_type": "pele",
            "iterations": 100,
            "pele_steps": 8,
            "cluster_values": "[2, 5, 7]",
            "cluster_conditions": "[1, 0.6, 0.0]",
            "steric_trials": 250,
            "overlap_factor": 0.65,
            "params": pcs.OUT_IN,
            "box_radius": 30,
            "bias_column": 7,
            "anm_freq": 4,
            "sidechain_freq": 1,
            "min_freq": 1,
            "water_freq": 1,
            "COMligandConstraint": 1.0,
            "sidechain_resolution": 10,
        },
        "gpcr_orth": {
            "spawning_type": "epsilon",
            "density": "null",
            "simulation_type": "pele",
            "iterations": 50,
            "pele_steps": 8,
            "cluster_values": "[1.75, 2.5, 4]",
            "cluster_conditions": "[0.7, 0.4, 0.0]",
            "steric_trials": 100,
            "overlap_factor": 0.65,
            "epsilon": 0.25,
            "bias_column": 6,
            "params": pcs.GPCR_ORTH,
            "box_radius": 15,
            "ca_constr": 5.0,
            "terminal_constr": 5.0,
            "ca_interval": 5,
        },
        "global": {
            "spawning_type": "inverselyProportional",
            "bias_column": 5,
            "epsilon": 0.25,
            "density": "continuous",
            "simulation_type": "pele",
            "iterations": 100,
            "pele_steps": 8,
            "cluster_values": "[2.0, 5, 7]",
            "cluster_conditions": "[1, 0.6, 0.0]",
            "steric_trials": 200,
            "overlap_factor": 0.65,
            "params": pcs.GLOBAL,
            "box_radius": None,
        },
        "induced_fit_long": {
            "spawning_type": "inverselyProportional",
            "bias_column": 5,
            "epsilon": 0.25,
            "density": "null",
            "simulation_type": "pele",
            "iterations": 10,
            "pele_steps": 100,
            "cluster_values": "[2.0, 5, 7]",
            "cluster_conditions": "[1, 0.6, 0.0]",
            "steric_trials": 500,
            "overlap_factor": 0.65,
            "params": pcs.INDUCED_FIT,
            "box_radius": 6,
            "min_freq": 1,
            "COMligandConstraint": 1.0,
            "constraints_level": 2,
        },
        "induced_fit_fast": {
            "spawning_type": "inverselyProportional",
            "bias_column": 5,
            "epsilon": 0.25,
            "density": "null",
            "simulation_type": "pele",
            "iterations": 25,
            "pele_steps": 12,
            "cluster_values": "[2.0, 5, 7]",
            "cluster_conditions": "[1, 0.6, 0.0]",
            "steric_trials": 500,
            "overlap_factor": 0.65,
            "params": pcs.INDUCED_FIT,
            "box_radius": 6,
            "min_freq": 1,
            "COMligandConstraint": 1.0,
            "constraints_level": 2,
        },
        "in_out": {
            "spawning_type": "epsilon",
            "bias_column": 6,
            "epsilon": 0.75,
            "density": "exitContinuous",
            "simulation_type": "pele",
            "iterations": 1000,
            "pele_steps": 2,
            "cluster_values": "[1, 2.5]",
            "cluster_conditions": "[1.1]",
            "steric_trials": 500,
            "overlap_factor": 0.65,
            "params": pcs.IN_OUT,
            "box_radius": 50,
            "spawning_condition": "max",
        },
        "in_out_soft": {
            "spawning_type": "independentMetric",
            "bias_column": 6,
            "epsilon": 0.75,
            "density": "exitContinuous",
            "simulation_type": "pele",
            "iterations": 1000,
            "pele_steps": 2,
            "cluster_values": "[1, 2.5]",
            "cluster_conditions": "[1.1]",
            "steric_trials": 500,
            "overlap_factor": 0.65,
            "params": pcs.IN_OUT,
            "box_radius": 50,
            "spawning_condition": "max",
        },
        "rescoring": {
            "spawning_type": "independent",
            "bias_column": 5,
            "epsilon": 0.25,
            "density": "null",
            "simulation_type": "pele",
            "iterations": 20,
            "pele_steps": 12,
            "cluster_values": "[1.75, 2.5, 4, 6]",
            "cluster_conditions": "[1, 0.6, 0.4, 0.0]",
            "steric_trials": 500,
            "overlap_factor": 0.65,
            "params": pcs.RESCORING,
            "box": False,
            "anm_freq": 0,
            "sidechain_freq": 1,
            "min_freq": 1,
            "temperature": 1000,
            "anm_displacement": 0.5,
            "anm_modes_change": 3,
            "ca_constr": 2.5,
            "terminal_constr": 5.0,
            "ca_interval": 8,
            "constraints_level": 3,
        },
        "anm": {
            "spawning_type": "independent",
            "bias_column": 5,
            "epsilon": 0.15,
            "density": "null",
            "simulation_type": "pele",
            "iterations": 50,
            "pele_steps": 8,
            "cluster_values": "[1.5, 2, 5]",
            "cluster_conditions": "[0.6, 0.4, 0.0]",
            "steric_trials": 250,
            "overlap_factor": 0.65,
            "params": pcs.ANM,
            "box_radius": 30,
        },
        "interaction_restrictions": {
            "spawning_type": "independent",
            "bias_column": 5,
            "epsilon": 0.25,
            "density": "null",
            "simulation_type": "pele",
            "iterations": 1,
            "pele_steps": 500,
            "cluster_values": "[2.0, 5, 7]",
            "cluster_conditions": "[2.0, 5, 7]",
            "steric_trials": 500,
            "overlap_factor": 0.65,
            "params": pcs.INTERACTION_RESTRICTIONS,
            "box_radius": 6,
        },
        "site_finder_global": {
            "spawning_type": "inverselyProportional",
            "epsilon": 0.25,
            "iterations": 50,
            "pele_steps": 12,
            "cluster_values": "[2.5, 4, 6]",
            "cluster_conditions": "[1, 0.5, 0.0]",
            "sidechain_freq": 2,
            "temperature": 1500,
            "overlap_factor": 0.65,
            "steric_trials": 200,
            "params": pcs.SITE_FINDER_GLOBAL,
        },
        "site_finder_local": {
            "spawning_type": "inverselyProportional",
            "epsilon": 0.25,
            "iterations": 10,
            "pele_steps": 50,
            "cluster_values": "[2.0, 4, 6]",
            "cluster_conditions": "[1, 0.5, 0.0]",
            "sidechain_freq": 2,
            "temperature": 1500,
            "overlap_factor": 0.65,
            "steric_trials": 200,
            "params": pcs.SITE_FINDER_LOCAL,
            "min_cluster_population": 0.005,
            "bandwidth": "auto",
            "cluster_representatives_criterion": "interaction_min"
        },
        "covalent_docking": {
            "anm_freq": 5,
            "overlap_factor": 0.6,
            "perturbation_trials": 100,
            "pele_steps": 400,
            "iterations": 1,
            "params": "",
        },
        "covalent_docking_refinement": {
            "perturbation_trials": 10,
            "pele_steps": 100,
            "refinement_distance": 10,
            "iterations": 1,
            "refinement_angle": 10,
            "params": "",
        },
        "saturated_mutagenesis": {
            "spawning": "independent",
            "bias_column": 5,
            "epsilon": 0.25,
            "density": "null",
            "simulation_type": "pele",
            "iterations": 1,
            "pele_steps": 1000,
            "cluster_values": "[2.0, 5, 7]",
            "cluster_conditions": "[1, 0.6, 0.0]",
            "steric_trials": 500,
            "overlap_factor": 0.65,
            "params": pcs.INDUCED_FIT,
            "box_radius": 6,
            "clust_type": "null",
        },
    },
}


def retrieve_software_settings(args, pele_dir):
    software_settings = deepcopy(SOFTWARE_CONSTANTS)

    if args.full:
        type_simulation = "global"
    elif args.in_out:
        type_simulation = "in_out"
    elif args.in_out_soft:
        type_simulation = "in_out_soft"
    elif args.induced_fit_long:
        type_simulation = "induced_fit_long"
    elif args.induced_fit_fast:
        type_simulation = "induced_fit_fast"
    elif args.rescoring:
        type_simulation = "rescoring"
    elif args.out_in:
        type_simulation = "out_in"
    elif args.gpcr_orth:
        type_simulation = "gpcr_orth"
    elif args.interaction_restrictions:
        type_simulation = "interaction_restrictions"
    elif args.site_finder_global:
        type_simulation = "site_finder_global"
    elif args.site_finder_local:
        type_simulation = "site_finder_local"
    elif args.covalent_docking_refinement:
        type_simulation = "covalent_docking_refinement"
    elif args.covalent_residue:
        type_simulation = "covalent_docking"
    elif args.saturated_mutagenesis:
        type_simulation = "saturated_mutagenesis"
    else:
        # Standard file (user will change the parameters)
        type_simulation = "induced_fit_fast"

    software_settings["ad_ex_temp"] = software_settings["ad_ex_temp"].format(pele_dir)
    software_settings["pele_exit_temp"] = software_settings["pele_exit_temp"].format(pele_dir)
    software_settings["simulation_params"] = software_settings["simulation_params"].get(type_simulation)
    return software_settings
