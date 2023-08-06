import os
import socket
import dotenv

from dptools.cli import BaseCLI
from dptools.utils import typemap2str, str2typemap, read_type_map, graph2typemap
from dptools.hpc import hpc_defaults

basedir = os.path.abspath(os.path.dirname(__file__))
default_env_file = os.path.join(basedir, ".env")
env_file = default_env_file


def set_env(key, value):
    dotenv.set_key(env_file, key, value)


def get_env():
    values = dotenv.dotenv_values(env_file)
    return values


def set_custom_env(label):
    global env_file
    env_file = default_env_file + "." + label


def get_dpfaults(key="model"):
    """ like defaults but for dp (haha... ha..) """
    print(env_file)
    default_vals = get_env()

    if key == "model":
        keys = ["DPTOOLS_MODEL", "DPTOOLS_TYPE_MAP"]
        defaults = tuple([default_vals.get(k) for k in keys])

    elif key == "sbatch":
        keys = ["SBATCH_COMMENT", 
                "OMP_NUM_THREADS", 
                "TF_INTRA_OP_PARALLELISM_THREADS", 
                "TF_INTER_OP_PARALLELISM_THREADS"]

        if not default_vals.get(keys[0], None):
            host = socket.gethostname()
            try:
                for k, v in hpc_defaults[host].items():
                    set_env(k, str(v))
            except KeyError:
                raise Exception("Host unrecognized and no default HPC parameters found."\
                    "\nUse 'dptools set script.sh' with desired #SBATCH comment in script.sh")
                    # XXX: What kind of exception would this be?

            default_vals = get_env(env)
            print("WARNING: set new default HPC parameters to env")
            print("\nSettings:")
            print("-" * 64)
            for k in keys:
                print(k, "=", default_vals[k])
            print("-" * 64)
        # this section is not going as smoothly as I envisioned 
        defaults = {k: default_vals[k] for k in keys}
    return defaults


def set_model(model):
    graph = os.path.abspath(model)
    type_map = graph2typemap(graph)
    type_map_str = typemap2str(type_map)
    set_env("DPTOOLS_MODEL", graph)
    set_env("DPTOOLS_TYPE_MAP", type_map_str)


def set_sbatch(script):
    raise NotImplementedError("Harass me for this if you need it")


def set_params(params):
    raise NotImplementedError("Harass me for this if you need it")


class CLI(BaseCLI): # XXX: Everything about this could surely be improved
    def add_args(self):
        help="Path to DP model, params.yaml, or {script}.sh to set as default.\n"\
             "Need .pb, .yaml, or .sh extension to set model, params, or sbatch, respectively."
        self.parser.add_argument(
            "thing",
            nargs=1,
            help=help
        )

    def main(self, args):
        self.set(args.thing[0])

    def set(self, thing):
        ext2function = {"pb": set_model, "sh": set_sbatch, "yaml": set_params}
        ext = thing.split(".")[-1]
        if ext not in ext2function:
            raise TypeError(f"Unrecognized file type for {thing}. Try 'dptools set -h'")
        self.set_thing = ext2function[ext]
        self.set_thing(thing)
