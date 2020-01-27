#! /usr/bin/env python3
# Sets up stuff for running FEAST/SourceTracker2 (either through QIIME 2) in
# order to detect misclassified samples.
#
# Inputs:
# - smooshed-metadata.txt: QIIME 2 metadata file containing AGP data and study
#   data where some samples seem to be misclassified
# - host_ids: a list of host subject IDs in the metadata file to subset the
#   sinks to
#
# Outputs: Three modified metadata files, where each file includes just:
# - 300 "source" samples
# - All "sink" samples of a specified empo_3 category
# Furthermore, a "SourceSink" column will be added to each metadata file and
# set accordingly.

from qiime2 import Metadata
from collections import Counter

host_ids = ["host1", "host2"]

print('loading metadata...')
df = Metadata.load("smooshed-metadata.txt").to_dataframe()
agp_sample_ids = set(df.loc[df.index.str.startswith("10317.")].index)

# 1. Construct a "Source" from each of the 3 AGP empo3 vals
agp_ids_to_use = []
for e in ["Animal distal gut", "Animal secretion", "Animal surface"]:
    # save the df subsets so we only have to do this once
    empo3subset = df[df["empo_3"] == e]

    agp_from_this_empo3 = set(empo3subset.index) & agp_sample_ids

    # Sort the list of IDs then take the first 100
    agp_empo3_subset = sorted(agp_from_this_empo3)[:100]
    agp_ids_to_use += agp_empo3_subset

# TODO subset the sinks as well? We could theoretically parallelize this across
# runs e.g. by unique coarse host id

for e in ["Animal distal gut", "Animal secretion", "Animal surface"]:
    print('finagling stuff for {}...'.format(e))

    empo3subset = df[df["empo_3"] == e]

    empo3_sampleids = list(
        empo3subset[
            empo3subset["coarse_host_id"].isin(host_ids)
        ].index
    )
    # Subset the metadata to only:
    # 1. the 300 prev selected AGP samples
    # 2. samples where empo_3 == e and the coarse_host_id matches one of
    #    the host subjects we care about
    df_subset = df.loc[agp_ids_to_use + empo3_sampleids]

    # Set all samples to Sink by default, then set the AGP ones to Source.
    # This will leave the samples with this empo_3 val as the Sinks.
    df_subset["SourceSink"] = "Sink"
    df_subset.loc[agp_ids_to_use, ["SourceSink"]] = "Source"
    output_md_name = "smooshed-metadata-agp-and-empo3-{}.txt".format(
        e.split()[-1]
    )
    print(Counter(df_subset["SourceSink"]))
    print(Counter(df_subset["empo_3"]))
    df_subset.to_csv(output_md_name, sep="\t")
