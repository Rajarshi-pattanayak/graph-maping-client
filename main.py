from algorithms import floyd_warshall, johnsons_algorithm, repeated_dijkstra
from graph_utils import input_graph, visualize_graph

def main():
    print("Welcome to the All-Pairs Shortest Path Visualizer!")
    graph = input_graph()
    visualize_graph(graph)
    print("\nChoose an algorithm:")
    print("1. Floyd-Warshall")
    print("2. Johnson's Algorithm")
    print("3. Repeated Dijkstra")
    choice = int(input("Enter your choice: "))
    
    if choice == 1:
        result = floyd_warshall(graph)
    elif choice == 2:
        adj_list = [[] for _ in range(len(graph))]
        for u in range(len(graph)):
            for v in range(len(graph)):
                if graph[u][v] != float('inf'):
                    adj_list[u].append((v, graph[u][v]))
        result = johnsons_algorithm(adj_list)
    elif choice == 3:
        adj_list = [[] for _ in range(len(graph))]
        for u in range(len(graph)):
            for v in range(len(graph)):
                if graph[u][v] != float('inf'):
                    adj_list[u].append((v, graph[u][v]))
        result = repeated_dijkstra(adj_list)
    else:
        print("Invalid choice!")
        return
    
    print("\nAll-Pairs Shortest Paths:")
    for i in range(len(result)):
        print(f"From Node {i}: {result[i]}")
    visualize_graph(result)

if __name__ == "__main__":
    main()
