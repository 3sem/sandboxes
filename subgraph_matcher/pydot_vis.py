import networkx as nx 
import pydot
from enum import Enum 

palette = {
    "r" : ('red', 'filled'),
    "g" : ('red' + ":"+ 'green' + ";0.25:" + 'blue', 'filled, rounded, wedged'),
    "b" : ('lightblue', 'filled')
}

def save_colored_pydot_graph(G: nx.DiGraph, nm="____ddd____.dot", num_palette=palette, label='group', visualize_by_colors=True):
    pdot = to_pydot(G)
    #num_palette = dict()
    #if visualize_by_colors:
        #num_palette = prepare_colors_dict(G)

    for i, node in enumerate(pdot.get_nodes()):
        if visualize_by_colors:
            try:
                clr_p = num_palette[int(node.obj_dict['attributes'].get(label, 1))]
                node.set_color('white')
                node.set_fillcolor(clr_p[0]) #+";0.15:"+clrs)
                node.set_style(clrp[1])
                
            except Exception as e:
                print(e)
                node.set_color('black')
            node.set_style('filled, rounded, wedged')
        
        else:
            node.set_style('rounded, filled')
       
        node.set_label( node.obj_dict['attributes'].get(label, None))
       
    pdot.write_dot(nm)
    
    return
