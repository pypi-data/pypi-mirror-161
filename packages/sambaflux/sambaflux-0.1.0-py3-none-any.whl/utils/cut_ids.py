import argparse
import pandas as pd

if __name__ == '__main__':
    description = "Utils script for cutting gene to reaction ID files into multiple files for parallel sampling."

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-i", "--input", help="Gene to reaction ID file (generated using utils/export_dicts.py).")
    parser.add_argument("-o", "--outputfolder", help="Path to a folder for outputting each group of reactions to a "
                                                     "file.")
    args = parser.parse_args()
    # path = "/home/juliette/these/data/models/gene_rxn_dicts/Human1_GWAS_all_genes_to_rxns_dict.tsv"
    # infile = pd.read_csv(path, sep="\t")
    infile = pd.read_csv(args.input, sep="\t")
    outputfolder = "/home/juliette/these/data/GWAS/rxns_all/"
    for i, row in infile.iterrows():
        gname = row["GeneID"].replace(" ", "_")
        # outfile = outputfolder+gname+".txt"
        outfile = args.outputfolder+gname+".txt"
        with open(outfile, 'w') as f:
            f.write(row["Rxns"])
