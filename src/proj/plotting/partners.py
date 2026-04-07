import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from proj.processing.data_loader import DATASETS, OA_MAP_DF
from proj.config.consts import OA_FAFB, OA_MCNS

def get_num_ax_ylabel(scale, direction, reference_oa):
    """Helper function to get y-axis label for # of shared partners plot."""
    if scale == "absolute" and direction == "upstream":
        title = f"↑ Types Shared With {reference_oa}"
    elif scale == "absolute" and direction == "downstream":
        title = f"↓ Types Shared With {reference_oa}"
    elif scale == "ratio" and direction == "upstream":
        title = f"Proportion ↑ Shared w/ {reference_oa} ↑"
    elif scale == "ratio" and direction == "downstream":
        title = f"Proportion ↓ Shared w/ {reference_oa} ↓"
    return title

def get_syn_ax_ylabel(scale, direction, reference_oa):
    """Helper function to get y-axis label for # of synapses with shared partners plot."""
    if scale == "absolute" and direction == "upstream":
        title = f"Input From {reference_oa} Upstream"
    elif scale == "absolute" and direction == "downstream":
        title = f"Output To {reference_oa} Downstream"
    elif scale == "ratio" and direction == "upstream":
        title = f"Proportion Synaptic Input From {reference_oa} ↑"
    elif scale == "ratio" and direction == "downstream":
        title = f"Proportion Synaptic Output To {reference_oa} ↓"
    return title

def ref2ref(ref_type, dataset, direction, scale):
    """Helper function to compare neurons in a reference type to themselves."""
    ref2ref_num_shared = []
    ref2ref_syns = []

    if direction == "upstream":
        target_side = "post_root_id"
        partner_side = "pre_root_id"

    elif direction == "downstream":
        target_side = "pre_root_id"
        partner_side = "post_root_id"

    # Get partners of each reference neuron.
    id_to_type = DATASETS[dataset].celltypes_df.set_index("root_id")["primary_type"]
    ref_neurons = DATASETS[dataset].celltypes_df.loc[
        DATASETS[dataset].celltypes_df["primary_type"] == ref_type,
        "root_id"
    ].values
    ref_edge_df = DATASETS[dataset].cell_connections_df.loc[
        DATASETS[dataset].cell_connections_df[target_side].isin(ref_neurons),
    ]
    ref_edge_df[partner_side] = ref_edge_df[partner_side].map(id_to_type)
    ref_edge_df = ref_edge_df.groupby([target_side, partner_side])["syn_count"].sum().reset_index()
    ref_edge_groups = ref_edge_df.groupby(target_side)[[partner_side, "syn_count"]]

    # Compare neurons to the rest of the neurons in the cell type and capture the values that reflect shared connectivity.
    for neuron in ref_neurons:
        ref_complement = set(ref_neurons)  - {neuron}
        ref_complement_partners = set()
        for comp in ref_complement:
            ref_complement_partners.update(ref_edge_groups.get_group(comp)[partner_side].values)
        ref_neuron_edge_df = ref_edge_groups.get_group(neuron)
        ref_neuron_totsyn = ref_neuron_edge_df["syn_count"].sum()

        ref_neuron_partners = set(ref_neuron_edge_df[partner_side].values)
        shared_partners = ref_neuron_partners & ref_complement_partners

        ref_neuron_syn2shared = ref_neuron_edge_df.loc[
            ref_neuron_edge_df[partner_side].isin(shared_partners),
            "syn_count"
        ].sum()
        if scale == "absolute":
            ref2ref_num_shared.append(len(shared_partners))
            ref2ref_syns.append(ref_neuron_syn2shared)
        elif scale == "ratio":
            ref2ref_num_shared.append(len(shared_partners) / len(ref_neuron_partners))
            ref2ref_syns.append(ref_neuron_syn2shared / ref_neuron_totsyn)
    return ref2ref_num_shared, ref2ref_syns, ref_neurons

def compare_oa(
        type1, type2, scale, direction, 
        t1_num_ax=None, t1_syn_ax=None, t2_num_ax=None, t2_syn_ax=None
        ):
    """Find the shared partners and synapses with shared partners between OA type1/2 and other OA types."""
    if scale not in ["ratio", "absolute"]:
        raise ValueError("scale must be 'ratio' or 'absolute'")
    if direction not in ["upstream", "downstream"]:
        raise ValueError("direction must be 'upstream' or 'downstream'")
    
    if all(ax is not None for ax in [t1_num_ax, t1_syn_ax, t2_num_ax, t2_syn_ax]):
        fig = t1_num_ax.get_figure()
    else:
        fig, (t1_num_ax, t1_syn_ax, t2_num_ax, t2_syn_ax) = plt.subplots(4, figsize=(24, 8))

    oa_type1 = type1
    oa_type2 = type2

    ref_ax = {}
    ref_ax[oa_type1] = (t1_num_ax, t1_syn_ax)
    ref_ax[oa_type2] = (t2_num_ax, t2_syn_ax)

    m_dataset = "mcns"
    f_dataset = "fafb"

    f_canon = OA_MAP_DF.loc[OA_MAP_DF["connectome"] == f_dataset, "canonical_type"].unique()
    m_canon = OA_MAP_DF.loc[OA_MAP_DF["connectome"] == m_dataset, "canonical_type"].unique()
    if set(f_canon) != set(m_canon):
        raise Exception("Male and female canonical types do not match.")
    canon_order = list(f_canon)

    canon_to_oa = {
        "VUMa2": "OA-VUMa2",
        "VUMa5": "OA-VUMa5"
    }

    colormap = {
        f_dataset: "#c90076",
        m_dataset: "#2986cc"
    }

    dataset_names = ["fafb", "mcns"]
    dataset_types = [OA_FAFB, OA_MCNS]

    target_types = [oa_type1, oa_type2]

    for i in range(2):

        reference_oa = target_types[i]
        comparison_oa = target_types[1 - i]
        all_oatypes = canon_order.copy()
        all_oatypes.remove(reference_oa)
        all_oatypes.remove(comparison_oa)
        all_oatypes.insert(0, comparison_oa)

        complement_oas = all_oatypes

        # fig, (num_ax, syn_ax), = plt.subplots(2, figsize=(12, 8))
        num_ax, syn_ax = ref_ax[reference_oa]
        x = np.arange(0, len(complement_oas) + 1)
        width = 0.40

        # Will contain data about the amount of shared partners and the synapses going to shared partners between the reference and complement OAs.
        shared_partner_data_df = pd.DataFrame()
        shared_partner_data_df["oa_types"] = complement_oas

        for d_name, d_types in zip(dataset_names, dataset_types):
            
            oa_neurons = DATASETS[d_name].celltypes_df.loc[DATASETS[d_name].celltypes_df["primary_type"].isin(d_types), "root_id"]
            map_df = OA_MAP_DF.loc[OA_MAP_DF["connectome"] == d_name]

            # Get partners of canonical OA types.
            id_to_canon = map_df.set_index("connectome_id")["canonical_type"]
            id_to_type = DATASETS[d_name].celltypes_df.set_index("root_id")["primary_type"]

            # Plot bars where we compare the neurons in each reference type to each other
            ref2ref_num_shared, ref2ref_syns, ref_neurons = ref2ref(canon_to_oa[reference_oa], d_name, direction, scale)

            r2r_num_shared_mean, r2r_num_shared_min, r2r_num_shared_max = np.mean(ref2ref_num_shared), np.min(ref2ref_num_shared), np.max(ref2ref_num_shared)
            r2r_syns_mean, r2r_syns_min, r2r_syns_max = np.mean(ref2ref_syns), np.min(ref2ref_syns), np.max(ref2ref_syns)
            if d_name == "fafb":
                offset = -width / 2
            elif d_name == "mcns":
                offset = width / 2

            num_ax.errorbar(0 + offset, r2r_num_shared_mean, yerr=[[r2r_num_shared_mean - r2r_num_shared_min], [r2r_num_shared_max - r2r_num_shared_mean]], capsize=3, color="black")
            num_ax.bar(0 + offset, r2r_num_shared_mean, width, color=colormap[d_name])
            num_ax.plot(0 + offset, ref2ref_num_shared[0], marker="o", label=f"{ref_neurons[0]}, w/ reference {ref_neurons[1]}")
            num_ax.plot(0 + offset, ref2ref_num_shared[1], marker="X", label=f"{ref_neurons[1]}, w/ reference {ref_neurons[0]}")

            syn_ax.errorbar(0 + offset, r2r_syns_mean, yerr=[[r2r_syns_mean - r2r_syns_min], [r2r_syns_max - r2r_syns_mean]], capsize=3, color="black")
            syn_ax.bar(0 + offset, r2r_syns_mean, width, color=colormap[d_name])
            syn_ax.plot(0 + offset, ref2ref_syns[0], marker="o", label=f"{ref_neurons[0]}, w/ reference {ref_neurons[1]}")
            syn_ax.plot(0 + offset, ref2ref_syns[1], marker="X", label=f"{ref_neurons[1]}, w/ reference {ref_neurons[0]}")
            

            if direction == "upstream":
                oatypes_edge_df = DATASETS[d_name].cell_connections_df.loc[DATASETS[d_name].cell_connections_df["post_root_id"].isin(oa_neurons)]
                oatypes_edge_df = oatypes_edge_df.rename(columns={"pre_root_id": "partner_root_id", "post_root_id": "oa_root_id"})
            elif direction == "downstream":
                oatypes_edge_df = DATASETS[d_name].cell_connections_df.loc[DATASETS[d_name].cell_connections_df["pre_root_id"].isin(oa_neurons)]
                oatypes_edge_df = oatypes_edge_df.rename(columns={"pre_root_id": "oa_root_id", "post_root_id": "partner_root_id"})

            
            oatypes_edge_df["oa_root_id"] = oatypes_edge_df["oa_root_id"].map(id_to_canon)
            oatypes_edge_df["partner_root_id"] = oatypes_edge_df["partner_root_id"].map(id_to_type)
            canon_edge_df = oatypes_edge_df.rename(columns={"oa_root_id": "oa_type", "partner_root_id": "partner_type"})

            canon_edge_df = canon_edge_df.groupby(["oa_type", "partner_type"], as_index=False)["syn_count"].sum()


            # Get number of common partners the two specified types have with other canonical OA types.
            grouped = canon_edge_df.groupby("oa_type")["partner_type"].apply(set)
            ref_partners = grouped[reference_oa]
            if scale == "absolute":
                num_shared = grouped.apply(lambda s: len(s & ref_partners))
            elif scale == "ratio":
                num_shared = grouped.apply(lambda s: len(s & ref_partners) / len(s))
            num_shared = num_shared.loc[complement_oas]
            shared_partner_data_df[f"{d_name}_num_shared_partners"] = num_shared.values

            # Get number of synapses going to common targets the two specified types have with other canonical OA types.
            grouped = canon_edge_df.groupby("oa_type")[["partner_type", "syn_count"]]
            ref_partners_to_syn = grouped.get_group(reference_oa).set_index("partner_type")
            syns = []
            for com_oa in complement_oas:
                com_partners_to_syn = grouped.get_group(com_oa).set_index("partner_type")
                shared_partners = com_partners_to_syn.index.intersection(ref_partners_to_syn.index)
                com_shared_syn = com_partners_to_syn.loc[shared_partners].values.sum()
                com_total_syn = com_partners_to_syn.values.sum()
                if scale == "absolute":
                    syns.append(com_shared_syn)
                elif scale == "ratio":
                    syns.append(com_shared_syn / com_total_syn)
            shared_partner_data_df[f"{d_name}_syn_w_shared_partners"] = syns

        num_ax.bar(x[1:] - width/2, shared_partner_data_df["fafb_num_shared_partners"], width, label="FAFB", color=colormap["fafb"])
        num_ax.bar(x[1:] + width/2, shared_partner_data_df["mcns_num_shared_partners"], width, label="MCNS", color=colormap["mcns"])
        num_ax.set_xticks(x, [reference_oa] + complement_oas, rotation=90)
        num_ax.set_ylabel(get_num_ax_ylabel(scale, direction, reference_oa))
        if scale == "ratio":
            num_ax.set_ylim(0, 1)

        syn_ax.bar(x[1:] - width/2, shared_partner_data_df["fafb_syn_w_shared_partners"], width, label="FAFB", color=colormap["fafb"])
        syn_ax.bar(x[1:] + width/2, shared_partner_data_df["mcns_syn_w_shared_partners"], width, label="MCNS", color=colormap["mcns"])
        syn_ax.set_xticks(x, [reference_oa] + complement_oas, rotation=90)
        syn_ax.set_ylabel(get_syn_ax_ylabel(scale, direction, reference_oa))
        if scale == "ratio":
            syn_ax.set_ylim(0, 1)

        num_ax.legend()
        syn_ax.legend()
    
    return fig, t1_num_ax, t1_syn_ax, t2_num_ax, t2_syn_ax