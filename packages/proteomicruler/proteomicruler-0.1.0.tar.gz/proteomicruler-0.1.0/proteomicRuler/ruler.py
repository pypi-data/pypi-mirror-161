import os.path
from io import StringIO

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from uniprotparser.parser import UniprotSequence, UniprotParser

from proteomicRuler import constant
from proteomicRuler.histones import HistoneDB
import re
import seaborn as sns
from matplotlib import pylab as plt

sns.color_palette("magma", as_cmap=True)

class Ruler:
    regex_intensity = re.compile(r"^[Ii]ntensity(.*)$")

    def __init__(self, df, intensity_columns = [], mw_col = "Mol. weight [kDa]", protein_ids_column = "Majority protein IDs", ploidy = 2, total_cellular_protein_concentration = 200):
        self.protein_ids_column = protein_ids_column
        self.logarithmized = False
        self.averaging_mode = 0
        self.molecular_mass_column = mw_col
        self.detectability_correction = False
        self.scaling_mode = 1
        self.ploidy = ploidy
        self.total_cellular_protein_concentration = total_cellular_protein_concentration
        self.output = ["Copy number per cell", "Concentration [nM]", "Separate sample summary tab"]
        self.df = df
        self.sample_name_dict = {}
        self.total_molecules = 0
        self.total_protein = 0
        self.histone = HistoneDB()
        self.histone.get_histones()
        if len(intensity_columns) != 0:
            for i in intensity_columns:
                self.sample_name_dict[i] = i 
        else:
            for i in self.df.columns:
                s = self.regex_intensity.search(i)
                if s:
                    print(s.group(1))
                    self.sample_name_dict[i] = s.group(1)
        self.df["normalization_factor"] = self.df[self.molecular_mass_column]
        self.df["normalization_factor"] = self.df["normalization_factor"].fillna(1)
        self.df["normalization_factor"] = self.df["normalization_factor"].replace(0, 1)
        self.check_and_convert_dalton()
        self.get_organism()
        self.cvalue = self.organism[1] * constant.base_pair_weight/constant.avogadro
        self.genes = []
        weighted_normalized_summed_histone_intensities_dict = self.calculate_weighted_histone_sum_normalization_factor()

        self.calculate_normalization_factor(weighted_normalized_summed_histone_intensities_dict)

        self.calculate_copy_numbers()

        self.calculate_total_volume()

        for i, r in self.df.iterrows():
            for c in self.sample_name_dict:
                if pd.notnull(r[c]):
                    self.df.at[i, "concentration_" + c] = r[c + "_copyNumbers"] / (self.total_volume * 1e-15) / constant.avogadro * 1e9
                    self.df.at[i, "mass_fraction_" + c] = r[c + "_copyNumbers"] * r[self.molecular_mass_column] *1e12 / constant.avogadro / self.total_protein * 1e6
                    self.df.at[i, "mole_fraction_" + c] = r[c + "_copyNumbers"] / self.total_molecules * 1e6

        self.calculate_rank()

    def calculate_rank(self):
        for c in self.sample_name_dict:
            self.df["rank_" + c] = rankdata(self.df[c + "_copyNumbers"], method="dense")
        maxrank = {c: self.df.shape[0] for c in self.sample_name_dict}
        for i, r in self.df.iterrows():
            for c in self.sample_name_dict:
                if not pd.notnull(r[c]):
                    self.df.at["rank_" + c] = np.nan
                    maxrank[c] -= 1
        for i, r in self.df.iterrows():
            for c in self.sample_name_dict:
                if pd.notnull(r["rank_" + c]):
                    self.df.at[i, "rank_" + c] = self.df.shape[0] - r["rank_" + c]
                    self.df.at[i, "relative_rank_" + c] = self.df.at[i, "rank_" + c] / maxrank[c]

    def calculate_normalization_factor(self, weighted_normalized_summed_histone_intensities_dict):
        self.factor = {}
        for c in self.sample_name_dict:
            self.factor[c] = self.cvalue * self.ploidy * constant.avogadro / \
                             weighted_normalized_summed_histone_intensities_dict[c]

    def calculate_total_volume(self):
        self.total_volume = self.total_protein / self.total_cellular_protein_concentration * 1000

    def calculate_copy_numbers(self):
        self.histone_mass = 0
        for i, r in self.df.iterrows():
            for c in self.sample_name_dict:
                if pd.notnull(r[c]):
                    self.df.at[i, c + "_copyNumbers"] = r[c] / r["normalization_factor"] * self.factor[c]
                    self.total_molecules += self.df.at[i, c + "_copyNumbers"]
                    self.total_protein += self.df.at[i, c + "_copyNumbers"] * 1e12 / constant.avogadro
                    if pd.notnull(r["Histone"]):
                        if r["Histone"]:
                            self.histone_mass += self.df.at[i, c + "_copyNumbers"] * 1e12 / constant.avogadro

    def calculate_weighted_histone_sum_normalization_factor(self):
        organism_histones = self.histone.df[self.histone.df["name"] == self.organism[0]]
        set_organism_histones = set(organism_histones.index)
        weighted_normalized_summed_histone_intensities_dict = {i: 0 for i in self.sample_name_dict}
        for i, r in self.df.iterrows():
            if pd.notnull(r[self.protein_ids_column]):
                a = r[self.protein_ids_column].split(";")
                if not set_organism_histones.isdisjoint(a):
                    self.df.at[i, "Histone"] = True
                    for c in self.sample_name_dict:
                        if pd.notnull(r[c]):
                            weighted_normalized_summed_histone_intensities_dict[c] += \
                                r[c] / r["normalization_factor"] * \
                                r[self.molecular_mass_column]
        return weighted_normalized_summed_histone_intensities_dict

    def get_organism(self):
        ids = [i2 for i in self.df[self.protein_ids_column] for i2 in i.split(";")]
        ids = np.unique(ids)
        self.organism = self.histone.get_organism(ids)

    def check_and_convert_dalton(self):
        print(self.df[self.molecular_mass_column])
        print(np.median(self.df[self.molecular_mass_column]))
        if np.median(self.df[self.molecular_mass_column]) < 250:
            self.df[self.molecular_mass_column] = self.df[self.molecular_mass_column] * 1000

    def load_genes(self, path=r"C:\Users\toanp\PycharmProjects\proteomicRuler\proteomicRuler\selectedgene.txt", gene_list = []):
        if len(gene_list) > 0:
            self.genes = gene_list
        else:
            with open(path, "rt") as geneNames:
                self.genes = [i.strip() for i in geneNames]

        for i, r in self.df.iterrows():
            if r["Gene names"] in self.genes:
                self.df.at[i, "selected"] = "Selected"
            else:
                self.df.at[i, "selected"] = "Not selected"

    def plot(self, output_folder="", selected=[]):
        for i in self.sample_name_dict:
            temp = self.df[pd.notnull(self.df[i + "_copyNumbers"]) & (self.df[i + "_copyNumbers"] != 0)]
            if len(selected) > 0:
                for i2, r in temp.iterrows():
                    if r["Gene names"] in selected:
                        temp.at[i2, "selected"] = "+"
            temp["log(10) copy number"] = np.log10(temp[i + "_copyNumbers"])
            fig, ax = plt.subplots(figsize=(10, 10))
            if "selected" in temp.columns:
                temp = temp[["Gene names", i + "_copyNumbers", "rank_" + i, "selected"]]
                sns.scatterplot(data=temp, x="rank_"+i, y="log(10) copy number", hue="log(10) copy number", style="selected", style_order=["Not selected", "Selected"],legend=False, linewidth=0.1, ax=ax)
                for i2, r in temp.iterrows():
                    if r["selected"]=="Selected":
                        plt.text(r["rank_"+i], r["log(10) copy number"], r["Gene names"], size='medium', color='black', weight='semibold')
                plt.savefig(os.path.join(output_folder, i + "_result.svg"))
                plt.clf()
            else:

                sns.scatterplot(data=temp, x="rank_" + i, y="log(10) copy number", hue="log(10) copy number",
                                legend=False, linewidth=0.1,
                                ax=ax)
                plt.savefig(os.path.join(output_folder, i + "_result.svg"))
                plt.clf()


def add_mw(df, accession_id_col):
    df1 = df.copy()
    for i, r in df1.iterrows():
        seq = UniprotSequence(r[accession_id_col], True)
        if seq.accession:
            df1.at[i, "Accession"] = str(seq)
    accessions = df1["Accession"].unique()
    parser = UniprotParser(accessions, True)
    data = []
    for i in parser.parse("tab", method="post"):
        frame = pd.read_csv(StringIO(i), sep="\t")
        frame = frame.rename(columns={frame.columns[-1]: "query"})
        data.append(frame)
    data = pd.concat(data, ignore_index=True)
    unmatched = []
    for a in accessions:
        if a not in data["query"].values:
            unmatched.append(a)
    if unmatched:
        print("Non-Uniprot ID found:", unmatched)
    data["Gene names"] = data["Gene names"].fillna("")
    data["gene_name_list"] = data["Gene names"].str.split(" ")
    data.loc[:, "Gene names"] = data["gene_name_list"].map(lambda x: x[0])
    data1 = data[["query",  "Entry name", "Mass", "Gene names"]]
    data1["queries"] = data1["query"].str.split(",")
    data1 = data1.explode("queries")
    res = df1.merge(data1, how="left", left_on="Accession", right_on="queries")
    res = res.drop(columns=["Accession", "queries", "query"])
    res = res.groupby(accession_id_col).head(1)
    return res
