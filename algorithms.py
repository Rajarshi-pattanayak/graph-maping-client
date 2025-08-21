import heapq

def floyd_warshall(graph):
    V = len(graph)
    dist = [[float('inf')] * V for _ in range(V)]
    for u in range(V):
        for v in range(V):
            dist[u][v] = graph[u][v]
    for k in range(V):
        for i in range(V):
            for j in range(V):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist

def bellman_ford(graph, source):
    V = len(graph)
    dist = [float('inf')] * V
    dist[source] = 0
    for _ in range(V - 1):
        for u in range(V):
            for v, weight in graph[u]:
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
    return dist

def dijkstra(graph, source):
    V = len(graph)
    dist = [float('inf')] * V
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, weight in graph[u]:
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(heap, (dist[v], v))
    return dist

def johnsons_algorithm(graph):
    V = len(graph)
    new_graph = graph + [[(i, 0) for i in range(V)]]
    h = bellman_ford(new_graph, V)
    reweighted_graph = [[] for _ in range(V)]
    for u in range(V):
        for v, weight in graph[u]:
            reweighted_graph[u].append((v, weight + h[u] - h[v]))
    all_pairs_dist = []
    for u in range(V):
        all_pairs_dist.append(dijkstra(reweighted_graph, u))
    for u in range(V):
        for v in range(V):
            if all_pairs_dist[u][v] < float('inf'):
                all_pairs_dist[u][v] += h[v] - h[u]
    return all_pairs_dist

def repeated_dijkstra(graph):
    V = len(graph)
    all_pairs_dist = []
    for u in range(V):
        all_pairs_dist.append(dijkstra(graph, u))
    return all_pairs_dist

