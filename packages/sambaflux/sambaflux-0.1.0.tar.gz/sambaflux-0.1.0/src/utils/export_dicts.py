import argparse
import pandas as pd
from sambaflux.src.iopy.export import export_metab_dict, export_gene_to_rxn_dict
from sambaflux.src.iopy.read_model import import_model
from sambaflux.src.setup.prepare_reactions import parse_rxns

if __name__ == '__main__':
    description = "Utils script for exporting model-specific dictionaries."

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-m", "--model", help="Metabolic model. Supported file formats: SBML, json, mat.")
    parser.add_argument("--createmetabdict", type=str, help="Add a path to create and write a metabolite ID to name "
                                                            "dictionary from the imported model.", default=None)
    parser.add_argument("--convertgenestorxns", type=str, help="Add a path to create and write a gene to reaction "
                                                               "dictionary from the imported model.", default=None)
    parser.add_argument("-g", "--genes", help="Gene ID file containing a single column of gene IDs for the model to KO")
    parser.add_argument("-s", "--sepko", help="Separator for the KO file", default=" ")
    args = parser.parse_args()

    model_file = args.model
    model = import_model(model_file)

    # Write the metab dict if requested
    # metab_dict_path = "/home/juliette/these/data/models/metab_dicts/Recon-2_from_matlab_metab_id_name.tsv"
    metab_dict_path = args.createmetabdict
    if metab_dict_path is not None:
        metab_dict = export_metab_dict(model)
        pd.DataFrame.from_dict(metab_dict, orient="index").to_csv(metab_dict_path, sep="\t", header=["Name"],
                                                                  index_label="ID")

    # Write the gene to reactions dict if requested (requires genes as ko input)
    # metab_dict_path = "/home/juliette/these/data/models/gene_rxn_dicts/Human1_GWAS_all_genes_to_rxns.tsv"
    gene_rxn_dict_path = args.convertgenestorxns
    if gene_rxn_dict_path is not None:
        ids_to_knockout = parse_rxns(args.genes, args.sepko)
        gene_to_rxn_dict = export_gene_to_rxn_dict(model, ids_to_knockout)
        pd.DataFrame.from_dict(gene_to_rxn_dict, orient="index").to_csv(gene_rxn_dict_path, sep="\t", header=["Rxns"],
                                                                        index_label="GeneID")
