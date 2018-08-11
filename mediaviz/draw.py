import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fa2l import force_atlas2_layout
from adjustText import adjust_text
import networkx as nx

from .utils import set_node_size, set_node_color, set_node_label
from .utils import edgecolor_by_source, filter_graph, get_subgraph_pos
from .utils import draw_networkx_nodes_custom
from .scaling import get_auto_scale, scale_layout


def draw_forceatlas2_network(G,
                             pos=None,
                             fa2l_iterations=50, fa2l_scaling_ratio=38,
                             scale="auto",
                             num_labels=None,
                             node_list=None,
                             node_color='red', color_by=None, colormap=None,
                             node_size=10,
                             size_field=None, min_size=0.1, max_size=100,
                             with_labels=False, label_field=None,
                             filter_by=None, top=None,
                             adjust_labels=True,
                             node_opacity=1, edge_opacity=0.05,
                             font_size=8, font_color='k', font_family='sans-serif',
                             filename="untitled.png", title=None,
                             edge_color="lightgray",
                             edge_color_by_source=False,
                             figsize=(10, 10), fig_dpi=100, **kwargs):
    """ Main function for drawing graph.

    The function has sensible defaults. If no scale is provided scale for the graph is set automatically. 
    If no pos is given then force atlas 2 layout is used. Other parameters can be described below can be 
    used to customize different aspects of the visualization. 

    See Notes section for dependencies. 

    Check README for examples.


    Parameters
    ----------
    G : nx.Graph

        A networkx graph.

    pos : dict or None. optional. default None.

        pos containing positions for the graph generated by some network layout algorithm. 

        If None, force_atlas2_layout function from fa2l package is used with default parameters to generate 
        the layout for the graph. To use with user given parameters for the force_atlas2_layout, calculate
        pos outside draw function and then pass to the draw function.

        Pos can also be calculated with  any other network layout algorithms like nx.spring_layout(G) 
        and passed to the draw function. 

    fa2l_iterations : int, optional. Default 50..

        number of times to run the default force atlas 2 layout algorithm from fa2l package.

    fa2l_scaling_ratio : float, optional. Default 38.

        How much repulsion you want. More makes a more sparse graph.

    scale : "auto" or float or int. optional. default "auto".

        Used for scaling the graph automatically.Also used for expanding and contracting the graph.

        If "auto", then scale is set automatically. see : mediaviz.scaling.get_auto_scale(...) for how
        scale is set. If given a float or int, positions are scaled according to the number. 

        For example, scale = 2 will expand the graph to twice of its current size while scale = 0.5 will 
        contract the graph to half of its original size. 

        When scaling graph node sizes are not changed, only the relative positions are changed. 

        For example, after doubling a position (2,4) will become (4,8).

    num_labels : int, optional. default None.

        Number of nodes to label sorted by the node size. 

        Recommended to use only with varying node sizes.

        If all node sizes are equal it will just return the nodes from G.nodes() in the same order.

    node_list : list. optional, default None.
        list of nodes to draw. if None and there's no filtering done all nodes are drawn.

    node_color : str or list. default 'red'.

        Multiple variations are allowed. 

        node_color can be color name like "r","b" or hex code in string format.

        node_color can also be a list of colors like ["r","b"...] or ["#FFFFFF","#..."...]. 

        If node_colors are being passed then color_by and colormap should be None(their defaults)

    color_by : node attribute. optional. Default None.

        categorical node attribute to color the nodes by. 

        If color by is given, a colormap dictionary must also be provided.

        Example : if "gender" in graph node attribute, then color_by = "gender" and 
        colormap = {"M":'b',"F":'r'}

    colormap : dict, optional. Default None.

        dictionaries containing color assignment for each value of the categorical node attribute in color_by.

        Assumes color_by is a categorical node_attribute like "gender" or "partition" or "country". 

        colormap is then a dictionary that assigns color for each unique value of that categorical node 
        attribute. 

        Example : If there's two unique values "M" and "F" in "gender" node attribute, then 
        color_by = "gender" and colormap = {"M":'b',"F":'r'}.

    node_size : int or float or list. Default 10.

        Multiple values are supported.
        
        int or float value can be provided to make all node sizes same.

        list of node sizes can also be passed.

        if node_size is given, size_field should not be used. Default of size_field is None.

    size_field : str, optional. Default None.

        Node attribute to resize the nodes by. Must be numeric node attribute.

        If given node sizes are resized to [min_size, max_size] using set_node_size from utils module.

    min_size : float, optional. Default 0.1

        Minimum size for the nodes.

    max_size : float , optional. Default : 100.

        maximum size for the nodes

    with_labels: bool, optional. Default False.

        Whether to show the labels or not. If label_field is not provided node names are used.

    filter_by : str, optional. Default None.
         
         Numeric Node attribute to filter the graph by. If filter_by is given, top must be provided. 

        Filter_by filters the graph to draw only the top k nodes. 

        For example, if filter_by = "inlink_count" and top = 100, the graph is filtered to
        the subgraph containing the top 100 nodes sorted by inlink count and only the subgraph 
        is drawn.

    top : int, optional. Default None.

        Number of largest nodes to keep after filtering using filter_by.

    label_field : str, optional. Default None.

        Node attribute to label the nodes by.

    adjust_labels : bool, optional. Default True.

        If True, Adjust Text package is used for adjusting the labels to prevent label overlap.

        Label texts are iteratively adjusted until there's no overlap.

        See : https://github.com/Phlya/adjustText for details. 

    node_opacity : float. Default 1

        Node alpha.
    
    edge_opacity : float.Default 0.05.

        Edge alpha.

    font_size : int, optional. Default 8.
        
        Label font size.

    font_color : str, optional. Default 'k'

        Label font color. 

    font_family : str. optional. Default 'sans-serif'

        Label font family.

    filename : str, optional. Default "untitled.png"

        File name to save the figure by. 
        See fname from https://matplotlib.org/api/_as_gen/matplotlib.pyplot.savefig.html

    title : str, optional. Default None.

        Plt title.

    edge_color_by_source : bool, optional. Default False.

        If true, edge colors are same as the source node for the edge. If edge_color is given, then 
        edge_color_by_source should be set to default False.

    figsize : tuple, optional. Default : (10,10)
        figure size.

    fig_dpi : float, optional. Default : 100. 
        See https://matplotlib.org/api/figure_api.html for details.


    """
    if node_list:
        G = nx.subgraph(node_list)

    if type(G) == nx.DiGraph:
        G = max(nx.weakly_connected_component_subgraphs(
            G), key=len).to_undirected()

    if pos is None:
        pos = force_atlas2_layout(
            G,
            iterations=fa2l_iterations,
            pos_list=None,
            node_masses=None,
            outbound_attraction_distribution=False,
            lin_log_mode=False,
            prevent_overlapping=False,
            edge_weight_influence=1.0,
            jitter_tolerance=1.0,
            barnes_hut_optimize=True,
            barnes_hut_theta=1.0,
            scaling_ratio=fa2l_scaling_ratio,
            strong_gravity_mode=False,
            multithread=False,
            gravity=1.0)

    if scale == "auto":
        if size_field:
            original_node_sizes = dict(zip(G.nodes(), set_node_size(
                G, size_field=size_field, min_size=min_size, max_size=max_size)))
        elif type(node_size) == int or type(node_size) == float:
            original_node_sizes = dict(
                zip(G.nodes(), [node_size]*len(G.nodes())))
        else:
            original_node_sizes = dict(zip(G.nodes(), node_size))
        scale = get_auto_scale(G, pos, original_node_sizes, k=20)
        print("scale is " + str(scale))
        pos = scale_layout(pos, scale)
    elif scale:
        pos = scale_layout(pos, scale)

    if with_labels is True and num_labels is None:
        num_labels = len(G.nodes())

    if filter_by:
        G = filter_graph(G, filter_by=filter_by, top=top)
        pos = get_subgraph_pos(G, pos)

    if color_by:
        node_color = set_node_color(G, color_by=color_by, colormap=colormap)

    if size_field:
        node_size = set_node_size(
            G, size_field=size_field, min_size=min_size, max_size=max_size)
    elif type(node_size) == int or type(node_size) == float:
        node_size = [node_size]*len(G.nodes())

    if edge_color_by_source:
        edge_color = edgecolor_by_source(G, node_color)

    if with_labels and label_field:
        node_labels = set_node_label(G, label_field=label_field)
        subset_label_nodes = sorted(zip(G.nodes(), node_size),
                                    key=lambda x: x[1],
                                    reverse=True)[0:num_labels]
        subset_labels = {n[0]: node_labels[n[0]] for n in subset_label_nodes}

    if with_labels and label_field is None:
        subset_labels = dict((n, n) for n in G.nodes())

    # plot the visualization

    fig = plt.figure(figsize=figsize, dpi=fig_dpi, **kwargs)
    ax = fig.add_subplot(111)

    # Draw the nodes, edges, labels separately

    draw_networkx_nodes_custom(G,
                               pos=pos, node_size=node_size,
                               node_color=node_color,
                               ax=ax,
                               alpha=node_opacity,
                               **kwargs)
    plt.axis("scaled")
    nx.draw_networkx_edges(
        G, pos=pos, edge_color=edge_color, alpha=edge_opacity, **kwargs)

    if with_labels:
        labels = nx.draw_networkx_labels(
            G, pos=pos, labels=subset_labels, font_size=font_size,
            font_color=font_color, font_family=font_family, **kwargs)
        if adjust_labels:
            # Adjust label overlapping
            x_pos = [v[0] for k, v in pos.items()]
            y_pos = [v[1] for k, v in pos.items()]
            adjust_text(
                texts=list(labels.values()),
                x=x_pos,
                y=y_pos)

    # add title
    if title:
        plt.title(title)

    ax.axis("off")
    # save the plot

    plt.savefig(filename)

    # Show the plot
    plt.show()
