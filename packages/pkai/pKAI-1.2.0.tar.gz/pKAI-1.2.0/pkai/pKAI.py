import argparse
from os.path import dirname, isfile, abspath
from protein import Protein
from torch import device, jit, set_num_threads


def load_model(model_name: str, dev):
    path = dirname(abspath(__file__))
    fname = f"{model_name}_model.pt"
    fpath = f"{path}/models/{fname}"

    dev = device(dev)
    model = jit.load(f"{fpath}").to(dev)

    return model


def pKAI(pdb, model_name="pKAI", device="cpu", threads=None):
    if threads:
        set_num_threads(threads)
    model = load_model(model_name, device)
    prot = Protein(pdb)
    prot.apply_cutoff()
    pks = prot.predict_pkas(model, device)
    return pks


def main():
    parser = argparse.ArgumentParser(description="pKAI")
    parser.add_argument("pdb_file", type=str, help="PDB file")
    parser.add_argument(
        "--model",
        type=str,
        choices=["pKAI", "pKAI+"],
        help="Number of threads to use",
        default="pKAI",
    )
    parser.add_argument(
        "--device", type=str, help="Device on which to run the model on", default="cpu"
    )
    parser.add_argument("--threads", type=int, help="Number of threads to use")

    args = parser.parse_args()

    pKAI(args.pdb_file, model_name=args.model, device=args.device, threads=args.threads)


if __name__ == "__main__":
    main()
