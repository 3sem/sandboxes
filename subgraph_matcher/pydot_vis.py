import networkx as nx 
import pydot
from enum import Enum 


border_color_palette = [
    'aqua',
    'azure',
    'beige',
    'blue',
    'brown',
    'charteuse',
    'coral',
    'crimson',
    'darkgreen',
    'fuchsia',
    'grey',
    'lavender',
    'magenta',
    'maroon',
    'navy',
    'salmon',
    'red',
    'wheat',
    'yellowgreen'

]


node_classes_palette = {
    "r" : ('red', 'filled'),
    "g" : ('red' + ":"+ 'green' + ";0.25:" + 'blue', 'filled, rounded, wedged'),
    "b" : ('lightblue', 'filled')
}

edle_classes_palette = border_color_palette





def save_colored_pydot_graph(G: nx.DiGraph, nm="____ddd____.dot",
                             node_palette=node_classes_palette, 
                             label='group', visualize_by_colors=True,
                             color_edges=True, edge_palette=edge_classes_palette):
    pdot = to_pydot(G)
    

    for i, node in enumerate(pdot.get_nodes()):
        if visualize_by_colors:
            try:
                clr_p = node_palette[int(node.obj_dict['attributes'].get(label, 1))]
                border_color = border_color_palette[node.obj_dict['attributes'].get('border_color', 1)]
                node.set_color(border_color)
                node.set_fillcolor(clr_p[0]) #+";0.15:"+clrs)
                node.set_style(clrp[1])
                
            except Exception as e:
                print(e)
                node.set_color('black')
            node.set_style('filled, rounded, wedged')
        
        else:
            node.set_style('rounded, filled')
       
        node.set_label(node.obj_dict['attributes'].get(label, None))

    if color_edges:
        for i, edge in enumerate(pdot.get_edges()):
            ek = edge.obj_dict['attributes'].get('border_color', '1')
            edge.set_label(ek)
            edge.set_color(edge_classes_palette[int(ek)])

    pdot.write_dot(nm)
    
    return
