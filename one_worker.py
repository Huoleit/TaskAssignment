from external import *
from TaskAssignment import *
from display import *

v = Visualization("Map.jpg", 60)
num_t = 50
t = np.concatenate((np.random.rand(num_t,1) * 1078, np.random.rand(num_t,1)*730), axis=1)
t_list = []

for i in range(len(t)):
    t_list.append(Trolley(t[i, 0], t[i, 1]))

assign = TaskAssignment(t_list, [])
groups = assign.grouping()

go_match = True
while True:
    t_group = TrolleyGroup(0,0,t_list)
    if v.read_click_flag():
        go_match = False
        t_group.elimanate_trolleys_nearby(v.get_mouse_pos())
        t_list = t_group.get_trolleys()

        new_groups = []
        for g in groups:
            g.elimanate_trolleys_nearby(v.get_mouse_pos())
            if len(g.get_trolleys()) != 0:
                new_groups.append(TrolleyGroup(*g.get_position(), g.get_trolleys()))
            else:
                go_match = True
        groups = new_groups

    w_list = [Worker(*v.get_mouse_pos()), ]
    assign.update(worker=w_list)

    if go_match:
        match = assign.assign_workers_to_groups(groups)
    paths = []
    for i, w in enumerate(w_list):
        order = assign.calculate_picking_order(w, groups[match[i]])
        paths.append(order)

    v.update(worker=w_list, trolley=t_list, groups=groups, match=match, paths=paths)
    v.draw()
    k = cv2.waitKey(1)
    if k == ord('q'):
        break
    elif k == ord('g'):
        v.on_off_show(groups=False)
