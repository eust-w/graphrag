import os
import pandas as pd
import pyarrow.parquet as pq
import networkx as nx
import plotly.graph_objs as go

# 读取所有parquet文件
directory_path = './artifacts'
nodes = pd.DataFrame()
edges = pd.DataFrame()

for filename in os.listdir(directory_path):
    if filename.endswith(".parquet"):
        filepath = os.path.join(directory_path, filename)
        data = pq.read_table(filepath).to_pandas()
        if 'source' in data.columns and 'target' in data.columns:
            edges = pd.concat([edges, data], ignore_index=True)
        else:
            nodes = pd.concat([nodes, data], ignore_index=True)

# 构建NetworkX图形
G = nx.Graph()

# 添加节点
for _, row in nodes.iterrows():
    G.add_node(row['id'], **row.to_dict())

# 添加边
for _, row in edges.iterrows():
    G.add_edge(row['source'], row['target'], **row.to_dict())

# 使用Plotly进行可视化
pos = nx.spring_layout(G)

# 创建边的可视化
edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_trace['x'] += (x0, x1, None)
    edge_trace['y'] += (y0, y1, None)

# 创建节点的可视化
node_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers+text',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        colorscale='YlGnBu',
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line=dict(width=2)))

for node in G.nodes():
    x, y = pos[node]
    node_trace['x'] += (x,)
    node_trace['y'] += (y,)
    node_trace['text'] += (str(node),)

fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Knowledge Graph',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="",
                        showarrow=False,
                        xref="paper", yref="paper"
                    )],
                    xaxis=dict(showgrid=False, zeroline=False),
                    yaxis=dict(showgrid=False, zeroline=False))
                )

fig.show()
