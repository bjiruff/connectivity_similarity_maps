import matplotlib.pyplot as plt
import proj.plotting.partners as p
from proj.config.paths import SAVEFIGS_DIR

def main():
    """Plot shared partner among OA types plots. Figures 5K-L, S5C-D."""
    # Specify which types you want as references when finding shared partners among OA types.
    oa_type1 = "VUMa2" # This will very likely break if you change to anything other than VUMa2 and VUMa5.
    oa_type2 = "VUMa5"
    scale = "ratio" # 'absolute' or 'ratio', specify if you want absolute number of shared partners/synapses or shared partners/synapses as a fraction of total partners/synapses.
    direction = "downstream" # 'upstream' or 'downstream'

    fig, (t1_num_ax, t1_syn_ax, t2_num_ax, t2_syn_ax) = plt.subplots(4, figsize=(16, 16))
    fig, *_ = p.compare_oa(
        oa_type1, oa_type2, scale, direction,
        t1_num_ax, t1_syn_ax, t2_num_ax, t2_syn_ax
    )
    fig.tight_layout()
    fig.savefig(str(SAVEFIGS_DIR / f"{oa_type1}_{oa_type2}_shared_{direction}_partners.png"), dpi=300)

if __name__ == "__main__":
    main()