from sys import path
from external import *
from scipy.cluster.vq import kmeans
import typing
import math
import logging
from scipy.optimize import linear_sum_assignment
from tsp import TSP

class TaskAssignment:
    def __init__(self, trolley: list[Trolley], worker: list[Worker]):
        self._trolley = trolley
        self._worker = worker
        self._worker_capacity = 7
        self._dis_penalty_weight = 1.0/4.0

    def update(self, trolley: typing.Optional[list[Trolley]], worker: list[Worker]):
        if trolley is not None:
            self._trolley = trolley
        if worker is not None:
            self._worker = worker

    def get_pos_array(self, l: list[Target]):
        pos = []
        for i in l:
            pos.append(i.get_position())
        return pos

    def assign_trolley_to_centroid(self, trolley: list[Target], centroids: list):
        t = self.get_pos_array(trolley)
        group_index = [0 for _ in range(len(trolley))]
        for i in range(len(t)):
            min_norm = math.inf
            min_index = 0
            for j in range(len(centroids)):
                dist = (t[i][0] - centroids[j][0]) **2 + (t[i][1] - centroids[j][1])  **2
                if dist < min_norm:
                    min_norm = dist
                    min_index = j
            group_index[i] = min_index
        return (group_index, centroids)

    def cluster(self, trolley: list[Trolley], num_cluster: int):
        t = self.get_pos_array(trolley)
        centroids= kmeans(t, num_cluster)[0]
        group_index, centroids = self.assign_trolley_to_centroid(trolley, centroids)
        return (group_index, centroids)

    def grouping(self) -> list[TrolleyGroup]:
        num_trolley = len(self._trolley)
        num_cluster = num_trolley // self._worker_capacity
        remaining_trolley = self._trolley
        remaining_centroids = []
        iter = 0
        while len(remaining_trolley) != 0:
            iter += 1
            group_index, centroids = self.cluster(remaining_trolley, num_cluster)
            keep_index = [0 for _ in range(len(centroids))]
            for i in range(len(centroids)):
                if group_index.count(i) <= self._worker_capacity:
                    keep_index[i] = 1  

            remaining_centroids += [d for d, s in zip(centroids, keep_index) if s]
            remaining_trolley = [d for d, s in zip(remaining_trolley, group_index) if not keep_index[s]]
            logging.debug("Iter: %d Re: %d", iter, len(remaining_trolley))
            num_cluster = keep_index.count(0) + 1

        group_index, _= self.assign_trolley_to_centroid(self._trolley, remaining_centroids)
        group = []
        for i in range(len(remaining_centroids)):
            trolley = [d for d, s in zip(self._trolley, group_index) if s==i]
            x, y = remaining_centroids[i]
            group.append(TrolleyGroup(x, y, trolley))

        return group

    def assign_workers_to_groups(self, groups: list[TrolleyGroup]):
        graph = []
        for w in self._worker:
            row = []
            for g in groups:
                cost = g.get_reward() - self._dis_penalty_weight*w.get_distance(g.get_position())
                row.append(cost)
            graph.append(row)
        print(graph)
        _, match = linear_sum_assignment(graph, True)
        return match
    
    def calculate_picking_order(self, worker: Worker, group: TrolleyGroup):
        start_ind = group.get_closest_trolley(worker.get_position())

        solver = TSP()
        order = solver.solve(group.get_trolleys_pos(), start_ind)
        return order

if __name__ == "__main__":
    import numpy as np
    num_w = 5
    num_t = 50
    w = np.concatenate((np.random.rand(num_w,1) * 1078, np.random.rand(num_w,1)*730), axis=1)
    t = np.concatenate((np.random.rand(num_t,1) * 1078, np.random.rand(num_t,1)*730), axis=1)
    t_list = []
    w_list = []
    for i in range(len(t)):
        t_list.append(Trolley(t[i, 0], t[i, 1]))
    for i in range(len(w)):
        w_list.append(Worker(w[i, 0], w[i, 1]))

    assign = TaskAssignment(t_list, w_list)
    groups = assign.grouping()
    match = assign.assign_workers_to_groups(groups)
    print(match)
    paths = []
    for i, w in enumerate(w_list):
        order = assign.calculate_picking_order(w, groups[match[i]])
        paths.append(order)

    from display import *
    v = Visualization("Map.jpg", 60)
    v.update(worker=w_list, trolley=t_list, groups=groups, match=match, paths=paths)

    while True:
        v.draw()

        k = cv2.waitKey(1)
        if k == ord('q'):
            break
        elif k == ord('g'):
            v.on_off_show(groups=False)
        

