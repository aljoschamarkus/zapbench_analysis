import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import alpha

# Create directed graph
G = nx.DiGraph()

size = 2000

# Add nodes with attributes
# G.add_node("A", size=800, color="red", shape="o", pos=(0, 0))   # circle
for i in range(2):
    if i == 0:
        sign = -1
        string = "l"
    else:
        sign = 1
        string = "r"
    G.add_node("Ret_" + string, size=size * 1.7, color="grey", pos=(150, 410 * sign), shape="o")
    G.add_node("AF5_" + string, size=size * 0.55, color="red", pos=(200, 230 * sign), shape="o")
    G.add_node("AF6_" + string, size=size * 0.55, color="yellow", pos=(215, 400 * sign), shape="o")
    G.add_node("TN_" + string, size=size * 1, color="blue", pos=(250, 350 * sign),  shape="o")
    G.add_node("Th_" + string, size=size * 0.5, color="orange", pos=(180, 75 * sign),  shape="s")
    G.add_node("PT_" + string, size=size * 0.5, color="green", pos=(220, 80 * sign),  shape="s")
    G.add_node("MT_" + string, size=size * 1, color="grey", pos=(280, 150 * sign),  shape="s")

for i in range(2):
    if i == 0:
        sign = -1
        string = "l"
        string2 = "r"
    else:
        sign = 1
        string = "r"
        string2 = "l"
    G.add_edge("Ret_" + string, "AF5_" + string, weight=1, sign="+")
    G.add_edge("Ret_" + string, "AF6_" + string, weight=1, sign="+")
    G.add_edge("Ret_" + string, "TN_" + string, weight=1, sign="+")
    G.add_edge("AF5_" + string, "PT_" + string, weight=1, sign="+")
    G.add_edge("AF6_" + string, "PT_" + string, weight=1, sign="+")
    G.add_edge("TN_" + string, "PT_" + string, weight=1, sign="+")
    G.add_edge("TN_" + string, "Th_" + string, weight=1, sign="+")
    G.add_edge("PT_" + string, "Th_" + string, weight=1, sign="+")
    G.add_edge("PT_" + string, "Th_" + string2, weight=1, sign="-")
    G.add_edge("Th_" + string, "MT_" + string, weight=1, sign="+")

# Positions
pos = nx.get_node_attributes(G, "pos")

# Edge attributes
edges = G.edges(data=True)
edge_widths = [e[2]["weight"] for e in edges]
edge_colors = ["green" if e[2]["sign"] == "+" else "red" for e in edges]
# edge_colors = ["green" if e[2] == "+" else "red" for e in edges]

# Draw edges (with arrows)
nx.draw_networkx_edges(
    G,
    pos,
    width=edge_widths,
    edge_color=edge_colors,
    arrows=True,
    arrowstyle="->",
    arrowsize=20,
    alpha=0.5,
)

# Draw nodes by shape (NetworkX limitation workaround)
shapes = set(nx.get_node_attributes(G, "shape").values())

for shape in shapes:
    nodes_of_shape = [n for n in G.nodes if G.nodes[n]["shape"] == shape]
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=nodes_of_shape,
        node_shape=shape,
        node_size=[G.nodes[n]["size"] for n in nodes_of_shape],
        node_color=[G.nodes[n]["color"] for n in nodes_of_shape],
        alpha=0.5,
        # font_size=10
    )

# Labels
nx.draw_networkx_labels(G, pos)

# Edge labels (signs)
# edge_labels = {(u, v): d["sign"] for u, v, d in G.edges(data=True)}
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
nx.draw_networkx_edge_labels(G, pos, edge_labels="")
plt.xlim(120, 320)
plt.ylim(-550, 550)
plt.axis("off")
# plt.show()
plt.savefig("/Users/aljoscha/Downloads/networksx_vis.pdf", format="pdf")
plt.close()