import networkx as nx
import matplotlib.pyplot as plt

def input_graph():
    print("Enter number of vertices:")
    V = int(input())
    graph = [[float('inf')] * V for _ in range(V)]
    print("Enter edges as 'u v weight' (type 'done' to finish):")
    while True:
        line = input()
        if line.lower() == "done":
            break
        u, v, w = map(int, line.split())
        graph[u][v] = w
    return graph

def visualize_graph(graph):
    G = nx.DiGraph()
    for u in range(len(graph)):
        for v in range(len(graph)):
            if graph[u][v] != float('inf'):
                G.add_edge(u, v, weight=graph[u][v])
    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()
