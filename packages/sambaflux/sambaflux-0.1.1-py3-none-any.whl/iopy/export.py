"""Functions for exporting and writing files."""
import os
from sambaflux.src.setup.prepare_reactions import parse_rxns


def write_sampling(s_results, out_path, model_name, n_samples, type, fname):
    final_path = str(out_path) + str(fname) + "_" + str(os.path.basename(os.path.splitext(model_name)[0])) + "_sampling_" + str(
                n_samples) + "_" + type + ".csv.gz"
    s_results.to_csv(final_path, index=False, compression='gzip')
    print("Wrote to "+final_path)


def extract_results(s, results, model):
    # Extract from results
    if results is None:
        if model.exchanges is not None:
            results_columns = [rxn.id for rxn in model.exchanges]
        else:
            results_columns = [col for col in s if col.startswith('EX_')]
    else:
        results_columns = parse_rxns(results)
    s_results = s[results_columns].round(3)
    return s_results


def export_metab_dict(model):
    # Create a metabolite ID to name dict for plotting in R
    metab_dict = {}
    # ex_rxn = model.exchanges.EX_A
    for ex_rxn in model.exchanges:
        name = next(iter(ex_rxn.metabolites)).name
        if len(name) < 30:
            if name != "":
                metab_dict[ex_rxn.id] = name
            else:
                metab_dict[ex_rxn.id] = next(iter(ex_rxn.metabolites)).id
        else:
            if next(iter(ex_rxn.metabolites)).name.endswith("(e)"):
                metab_dict[ex_rxn.id] = next(iter(ex_rxn.metabolites)).id[:-3]
            else:
                metab_dict[ex_rxn.id] = next(iter(ex_rxn.metabolites)).id
    return metab_dict


def export_gene_to_rxn_dict(model, ids_to_ko):
    # Create a gene to rxn ID using GPRs
    gene_to_rxn_dict = {}
    for gene in ids_to_ko:
        # gene is a list of 1 item for compatibility with using multiple reaction names in one row/group
        rxns = [rxn.id for rxn in model.genes.get_by_id(gene[0]).reactions]
        gene_to_rxn_dict[gene[0]] = " ".join(rxns)
    return gene_to_rxn_dict
