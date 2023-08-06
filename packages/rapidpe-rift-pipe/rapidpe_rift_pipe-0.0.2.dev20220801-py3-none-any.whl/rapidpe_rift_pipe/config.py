import sys
from ast import literal_eval
from typing import List, Optional
from dataclasses import dataclass
import json
import shutil
from rapidpe_rift_pipe.modules import *


@dataclass
class Config:
    """
    # Example usage
    cfg = Config.load(config_fname)
    cfg.output_parent_directory
    """
    # GraceDB settings
    gracedb_url: Optional[str]
    # Condor info
    accounting_group: str
    email_address_for_job_complete_notice: Optional[str]
    # Paths
    output_parent_directory: str
    injections_filename: str
    # Sampling settings
    n_iterations_per_job: int
    # Parameters
    intrinsic_param_to_search: List[str]
    # Flags
    # TODO: should convert from ints to bool (only have values 0 and 1 currently)
    event_params_in_cfg: bool
    overwrite_existing_event_dag: int
    submit_only_at_exact_signal_position: int
    submit_dag: int
    use_skymap: int

    # Grid refinement options
    distance_coordinates: str

    # Executable paths
    exe_create_event_dag: str
#    exe_compute_intrinsic_grid: str
    exe_generate_initial_grid: str
    exe_grid_refine: str
    exe_integration_extrinsic_likelihood: str

    # Entire sections parsed as dicts
    common_event_info: dict
    integrate_likelihood_cmds_dict: dict

    # Mutually exclusive groups
    event: "EventConfig"
    initial_grid_setup: "InitialGridSetupConfig"

    # Entire sections parsed as command line args
    initial_grid_only_cli_args: str

    @staticmethod
    def load(fname) -> "Config":
        from configparser import ConfigParser

        cfg = ConfigParser()
        cfg.optionxform = str
        cfg.read(fname)
        if cfg.getint("General","event_parameters_in_config_file") == 1:
            sys.exit("ERROR: this cfg file expects the event params to by in the cfg file, instead of passed from here")

        attrs = {}

        ###########
        # General #
        ###########
        # GraceDB info
        attrs["gracedb_url"] = cfg.get(
            "General", "gracedb_url",
            fallback="https://gracedb.ligo.org/api/",
        )

        # Condor info
        attrs["accounting_group"] = cfg.get("General","accounting_group")
        attrs["email_address_for_job_complete_notice"] = cfg.get(
            "General", "email_address_for_job_complete_notice",
            fallback="",
        )
        # Paths
        attrs["output_parent_directory"] = cfg.get("General", "output_parent_directory")
        attrs["injections_filename"] = cfg.get("General", "injections_file", fallback=None)
        # Sampling settings
        attrs["n_iterations_per_job"] = cfg.getint("General", "n_iterations_per_job")
        # Parameters
        attrs["intrinsic_param_to_search"] = literal_eval(correct_list_string_formatting(
            cfg.get("General","intrinsic_param_to_search", fallback="[mass1,mass2]")
        ))
        # Flags
        attrs["event_params_in_cfg"] = cfg.getboolean(
            "General", "event_parameters_in_config_file",
        )
        attrs["overwrite_existing_event_dag"] = cfg.getint(
            "General", "overwrite_existing_event_dag",
            fallback=0,
        )
        attrs["submit_only_at_exact_signal_position"] = cfg.getint(
            "General", "submit_only_at_exact_signal_position",
            fallback=0,
        )
        attrs["submit_dag"] = cfg.getint("General", "submit_dag")
        attrs["use_skymap"] = cfg.getint("General", "use_skymap")
        # Executables
        attrs["exe_create_event_dag"] = os.path.abspath(shutil.which(
            cfg.get(
                "General", "exe_create_event_dag",
                fallback="rapidpe_create_event_dag",
            )
        ))
        attrs["exe_generate_initial_grid"] = shutil.which(
            cfg.get(
                "General", "exe_generate_initial_grid",
                fallback=""
            )
        )
        if attrs["exe_generate_initial_grid"] is not None:
            attrs["exe_generate_initial_grid"] = os.path.abspath(
                attrs["exe_generate_initial_grid"]
            )
        attrs["exe_grid_refine"] = os.path.abspath(shutil.which(
            cfg.get(
                "General", "exe_grid_refine",
                fallback="rapidpe_compute_intrinsic_grid",
            )
        ))
        attrs["exe_integration_extrinsic_likelihood"] = (
            os.path.abspath(shutil.which(
                cfg.get(
                    "General", "exe_integration_extrinsic_likelihood",
                    fallback="rapidpe_integrate_extrinsic_likelihood",
                )
            ))
        )

        ##############
        # GridRefine #
        ##############
        attrs["distance_coordinates"] = cfg.get(
            "GridRefine", "distance-coordinates",
            fallback="",
        )

        #########
        # Event #
        #########
        attrs["event"] = EventConfig(cfg)

        ####################
        # InitialGridSetup #
        ####################
        attrs["initial_grid_setup"] = InitialGridSetupConfig(cfg)

        #####################
        # Sections as Dicts #
        #####################
        attrs["common_event_info"] = convert_section_args_to_dict(cfg, "Event")
        attrs["integrate_likelihood_cmds_dict"] = (
            convert_section_args_to_dict(cfg, "LikelihoodIntegration")
        )

        #################################
        # Sections as command line args #
        #################################
        attrs["initial_grid_only_cli_args"] = (
            convert_cfg_section_to_cmd_line(cfg, "InitialGridOnly")
            if cfg.has_section("InitialGridOnly")
            else ""
        )

        return Config(**attrs)


_INACCESSIBLE = object()


def possibly_inaccessible_property(field_name):
    protected_field_name = f"_{field_name}"

    def wrapper(self):
        field = getattr(self, protected_field_name)
        if field is _INACCESSIBLE:
            raise AttributeError(
                "Cannot access field {field_name} in mode {self.mode}"
            )

        return field

    return property(wrapper)


def parse_str(cfg, section, option, fallback=None):
    return cfg.get(section, option, fallback=fallback)

def parse_int(cfg, section, option, fallback=None):
    return cfg.getint(section, option, fallback=fallback)

def parse_bool(cfg, section, option, fallback=None):
    return cfg.getboolean(section, option, fallback=fallback)

def parse_list(cfg, section, option, fallback=None):
    if not cfg.has_option(section, option):
        return fallback

    return literal_eval(
        correct_list_string_formatting(cfg.get(section, option))
    )

def parse_dict(cfg, section, option, fallback=None):
    if not cfg.has_option(section, option):
        return fallback

    json_str = cfg.get(section, option)
    return json.loads(json_str)

def fields_match(fields, field_descriptors) -> bool:
    """
    Returns `True` if the fields match precisely with the fields named in the
    descriptors, though if the descriptors have a `"fallback"` value, they do
    not need to be present.  Otherwise return `False`.
    """
    # Make copies that we can modify
    fields_remaining = fields.copy()
    field_descriptors_remaining = field_descriptors.copy()

    # Iterate through fields, removing from both data structures if present, and
    # returning `False` if a field is not in the descriptors.
    while fields_remaining:
        field, _ = fields_remaining.pop()
        if field not in field_descriptors_remaining:
            return False
        del field_descriptors_remaining[field]

    # Now the only remaining descriptors should have `"fallback"` values.
    for field, descriptor in field_descriptors_remaining.items():
        if "fallback" not in descriptor:
            return False

    # Everything matched, return `True`.
    return True





def _make_config_group(type_name: str, section_name: str, spec: dict):
    """
    Programmatically defines the `EventConfig` class.
    """
    # Set of field names which occur under all possible groups.
    possible_field_names = set()
    for _, group_field_descriptors in spec.items():
        possible_field_names |= set(group_field_descriptors)


    def __init__(self, cfg):
        # Ensure "Event" section is present.
        if not cfg.has_section(section_name):
            raise RuntimeError(f"Missing section '{section_name}'")

        # Initialize all possible fields to be inaccessible.  Accessible ones
        # will be overwritten later.
        for field_name in possible_field_names:
            protected_field_name = f"_{field_name}"
            setattr(self, protected_field_name, _INACCESSIBLE)

        # Get the names of all options in "Event" section
        fields = set(cfg.items(section_name))

        # Attempt to find a group that matches the options in the config file.
        for group_name, group_field_descriptors in spec.items():
            if fields_match(fields, group_field_descriptors):
                # Found a match.

                # Set the mode
                self._mode = group_name

                # Add each field as an attribute, prefixed by `_` so they cannot
                # be modified later.
                for field_name, descriptor in group_field_descriptors.items():
                    protected_field_name = f"_{field_name}"

                    # Get information needed for parsing the line in the config
                    # file.
                    parser = descriptor["parser"]
                    fallback = descriptor.get("fallback")
                    # Parse the value from the config file.
                    value = parser(
                        cfg, section_name, field_name,
                        fallback=fallback,
                    )

                    # Store the value.
                    setattr(self, protected_field_name, value)

                # No need to process any other groups.
                return

        # No group matched, config is malformed.
        raise RuntimeError(
            f"'{section_name}' section does not have all required fields."
        )

    def mode(self) -> str:
        return self._mode

    # Superclass
    type_bases = (object,)
    # Define the class's methods
    type_dict = {
        "__init__" : __init__,
        "mode" : property(mode),
    }
    # Track information included in `__repr__`
    repr_fields = ["mode"]

    # Dynamically add properties for each possible field
    for field_name in possible_field_names:
        type_dict[field_name] = possibly_inaccessible_property(field_name)
        repr_fields.append(field_name)

    # Define __repr__
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        field_descriptors = []
        for field in repr_fields:
            if hasattr(self, field):
                value = getattr(self, field)
                field_descriptors.append(f"{field}={value!r}")
        return f"{class_name}({', '.join(field_descriptors)})"

    type_dict["__repr__"] = __repr__

    return type(type_name, type_bases, type_dict)


_event_group_spec = {
    "gid" : {
        "gracedb_id" : {
            "parser" : parse_str,
        },
    },
    "sid" : {
        "superevent_id" : {
            "parser" : parse_str,
        },
    },
    "injections" : {
        "injections_file" : {
            "parser" : parse_str,
            "fallback" : "/home/caitlin.rose/my_rapidPE_work/f2y2016data/subset_f2y2016inj/exact_inj/f2y2016_HLV_100shuffled_exactmasses.txt",
        },
        "cache_file" : {
            "parser" : parse_str,
            "fallback" : "/home/caitlin.rose/my_rapidPE_work/f2y2016data/create_2016_L1H1_data/2016injecteddata/injected_frames.cache",
        },
        "psd_file" : {
            "parser" : parse_list,
            "fallback" : [
                "H1=/home/caitlin.rose/my_rapidPE_work/f2y2016data/create_2016_L1H1_data/firstattempt/H1_psd_mid.xml.gz",
                "L1=/home/caitlin.rose/my_rapidPE_work/f2y2016data/create_2016_L1H1_data/firstattempt/L1_psd_mid.xml.gz",
                "V1=/home/caitlin.rose/my_rapidPE_work/f2y2016data/check_virgo_psd/V1_psd.xml.gz",
            ],
        },
        "skymap_file" : {
            "parser" : parse_str,
            "fallback" : "/home/vinaya.valsan/rapidPE/sinead_rapidPE/pp-plots-from-scratch/skymap/2016_fits/$INJINDEX$/bayestar.fits.gz",
        },
        "channel_name" : {
            "parser" : parse_list,
            "fallback" : [
                "H1=INJ_GAUSSIAN",
                "L1=INJ_GAUSSIAN",
                "V1=INJ_GAUSSIAN",
            ],
        },
    }
}

EventConfig = _make_config_group("EventConfig", "Event", _event_group_spec)


_initial_grid_setup_spec = {
    "overlap_bank" : {
        "overlap_bank" : {
            "parser" : parse_str,
        },
        "initial_region" : {
            "parser" : parse_dict,
            "fallback" : None,
        },
    },
    # TODO: split this into 2 groups, one for gstLAL templates and one for
    #       fixed region.
    "default" : {
    }
}

InitialGridSetupConfig = _make_config_group(
    "InitialGridSetupConfig", "InitialGridSetup",
    _initial_grid_setup_spec,
)
