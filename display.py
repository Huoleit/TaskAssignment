import cv2
import numpy as np
from TaskAssignment import *

class Visualization:
    def __init__(self, path_to_map: str, grid_num_in_x) -> None:
        self._img_origin = cv2.imread(path_to_map)
        self._img = self._img_origin.copy()
        self._trolley = []
        self._worker = []
        self._groups = []
        self._match = []
        self._paths = []
        self._show = {"worker": True, "trolley":True, "groups":True, "match":True, "paths":True}

        cv2.namedWindow('img') 
        cv2.moveWindow('img', 100, 200)
        cv2.setMouseCallback('img', self.mouse_event) 

        X = np.linspace(start=0, stop= self._img_origin.shape[1], num=grid_num_in_x)
        step = X[1] - X[0]
        Y = np.arange(start=0, stop= self._img_origin.shape[0], step=step)
        for x in X:
            cv2.line(self._img, (int(x), 0),(int(x),  self._img.shape[0]-1), (0,0,255), 1)
        for y in Y:
            cv2.line(self._img, (0, int(y)),( self._img.shape[1]-1, int(y)), (0,0,255), 1)
    
    def draw_worker(self, img, worker: list[Worker]):
        for w in worker:
            cv2.circle(img, w.get_position_int(), 8, (0,255,0), -1)

    def draw_trolley(self, img, trolley: list[Trolley]):
        for t in trolley:
            cv2.circle(img, t.get_position_int(), 12, (0,0,255), -1)

    def draw_groups(self, img, groups: list[TrolleyGroup]):
        for i in groups:
            cv2.circle(img, i.get_position_int(), 8, (150,0,255), -1)
            for j in i.get_trolleys():
                cv2.line(img, i.get_position_int(),j.get_position_int(), (0,120,255), 5)
            cv2.putText(img,str(round(i.get_reward(),4)), i.get_position_int(), cv2.FONT_HERSHEY_SIMPLEX , 1,(0,0,0),thickness=2)
    
    def draw_match(self, img, worker: list[Worker], groups: list[TrolleyGroup], match: list):
        for i, m in enumerate(match):
            if m != -1:
                cv2.line(img, worker[i].get_position_int(), groups[m].get_position_int(), (0,195,255), 5)
    
    def draw_path(self, img, worker: list[Worker], groups: list[TrolleyGroup], match: list, paths:list[list[int]]):
        for i, p in enumerate(paths):
            from_pos = worker[i].get_position_int()
            trolleys_pos = groups[match[i]].get_trolleys_pos()
            for node in p[:-1]:
                to_pos = trolleys_pos[node]
                cv2.line(img, (int(from_pos[0]), int(from_pos[1])), (int(to_pos[0]), int(to_pos[1])), (0,120,120), 3)
                from_pos = to_pos

    def mouse_event(self, event, x, y, flags, param):
        print("x: %f y:%f"%(x,y))

    def update(self, trolley: list[Trolley] = None, worker: list[Worker]= None, groups: list[TrolleyGroup] = None, match: list = None, paths=None):
        if trolley is not None:
            self._trolley = trolley
        if worker is not None:
            self._worker = worker
        if groups is not None:
            self._groups = groups
        if match is not None:
            self._match = match
        if paths is not None:
            self._paths = paths

    def on_off_show(self, **kwargs):
        for k in kwargs.keys():
            if k in self._show.keys():
                self._show[k] = not self._show[k]


    def draw(self):
        img = self._img.copy()
        if self._show["match"]:
            self.draw_match(img, self._worker, self._groups, self._match)
        if self._show["groups"]:
            self.draw_groups(img, self._groups)
        if self._show["paths"]:
            self.draw_path(img, self._worker, self._groups, self._match, self._paths)
        if self._show["trolley"]:
            self.draw_trolley(img,  self._trolley)
        if self._show["worker"]:
            self.draw_worker(img,  self._worker)

        cv2.imshow("img", img)
        

if __name__ == "__main__":
    v = Visualization("Map.jpg", 60)
    num_w = 10
    num_t = 50
    w = np.concatenate((np.random.rand(num_w,1) * 1078, np.random.rand(num_w,1)*730), axis=1)
    t = np.concatenate((np.random.rand(num_t,1) * 1078, np.random.rand(num_t,1)*730), axis=1)
    t_list = []
    w_list = []
    for i in range(len(t)):
        t_list.append(Trolley(t[i, 0], t[i, 1]))
    for i in range(len(w)):
        w_list.append(Worker(w[i, 0], w[i, 1]))

    v.update(worker=w_list, trolley=t_list)
    assign = TaskAssignment(t_list, w_list)
    groups = assign.grouping()

    while True:
        v.draw()
        if cv2.waitKey(1) == ord('q'):
            break



