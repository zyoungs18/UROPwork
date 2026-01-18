import pygame
import networkx as nx
import os
import math

# Updated constants for new left tab width
NEW_LEFT_TAB_WIDTH = 350  # New width for the left tab
DEFAULT_WIDTH, DEFAULT_HEIGHT = 1200, 800
RIGHT_TAB_WIDTH = 200
MARGIN = 20  # Margin for better spacing
DARK_GREEN = (0, 128, 0)

# New grid toggle state
show_grid = False


# Function to find the longest path in a tree
def find_longest_path(g):
    def bfs_longest_path_length(start):
        visited = {start}
        queue = [(start, [start])]
        max_path = []
        while queue:
            node, path = queue.pop(0)
            for neighbor in g.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path))
                    if len(new_path) > len(max_path):
                        max_path = new_path
        return max_path

    longest_path = []
    for node in g.nodes():
        path = bfs_longest_path_length(node)
        if len(path) > len(longest_path):
            longest_path = path
    return longest_path


# Function to arrange nodes along the longest path and branch out leaves
def arrange_tree(tree, pos, start_x, start_y, x_spacing=50, y_spacing=50):
    longest_path = find_longest_path(tree)
    x = start_x
    y = start_y

    # Arrange nodes along the longest path
    for i, node in enumerate(longest_path):
        pos[node] = (x, y)
        x += x_spacing

    # Arrange other nodes branching out from the longest path
    for i, node in enumerate(longest_path):
        leaf_y = y + y_spacing
        for neighbor in tree.neighbors(node):
            if neighbor not in pos:
                pos[neighbor] = (pos[node][0], leaf_y)
                leaf_y += y_spacing

    # Arrange any remaining nodes that might not be connected
    remaining_nodes = set(tree.nodes()) - set(pos.keys())
    for node in remaining_nodes:
        pos[node] = (x, y)
        y += y_spacing

    return pos


# Function to draw the graph with labels
def draw_graph(mod, screen, G, pos, show_vertex_labels, show_vertex_sublabels, show_edge_labels, show_edge_sublabels,
               vertex_scale):
    for edge in G.edges():
        pygame.draw.line(screen, (200, 200, 200), pos[edge[0]], pos[edge[1]], int(2 * vertex_scale))  # GRAY
        # Calculate edge label
        x, y = edge
        l_e = "∞" if x == math.inf or y == math.inf else min(abs(x - y), mod - abs(x - y))
        if x == math.inf:
            l_mod_7 = y % 7
        elif y == math.inf:
            l_mod_7 = x % 7
        else:
            l_mod_7 = (x + y) % 7

        mid_x = (pos[edge[0]][0] + pos[edge[1]][0]) / 2
        mid_y = (pos[edge[0]][1] + pos[edge[1]][1]) / 2
        angle = math.atan2(pos[edge[1]][1] - pos[edge[0]][1], pos[edge[0]][0] - pos[edge[1]][0])
        angle_deg = math.degrees(angle)

        if angle_deg < -90 or angle_deg > 90:
            angle_deg += 180
            angle_deg %= 360

        font = pygame.font.SysFont('Arial', int(12 * vertex_scale))
        sub_font = pygame.font.SysFont('Arial', int(10 * vertex_scale))

        if show_edge_labels:
            text = font.render(str(l_e), True, DARK_GREEN)  # DARK_GREEN
            text = pygame.transform.rotate(text, -angle_deg)
            text_rect = text.get_rect(center=(mid_x, mid_y))
            screen.blit(text, text_rect.topleft)

        if show_edge_sublabels:
            sub_text = sub_font.render(str(l_mod_7), True, (255, 0, 0))  # RED
            sub_text = pygame.transform.rotate(sub_text, -angle_deg)
            sub_text_rect = sub_text.get_rect(center=(mid_x, mid_y))
            if show_edge_labels:
                screen.blit(sub_text, (text_rect.right - 5, text_rect.bottom - 5))
            else:
                screen.blit(sub_text, sub_text_rect.topleft)

    for node in G.nodes():
        pygame.draw.circle(screen, (0, 0, 255), (int(pos[node][0]), int(pos[node][1])), int(5 * vertex_scale))  # BLUE
        # Draw custom node labels with subscript
        node_label = "∞" if node == math.inf else str(node % mod)
        sub_label = "" if node == math.inf else str(node % 7)
        font = pygame.font.SysFont('Arial', int(12 * vertex_scale))
        sub_font = pygame.font.SysFont('Arial', int(10 * vertex_scale))

        if show_vertex_labels:
            text = font.render(node_label, True, (0, 0, 0))  # BLACK
            text_rect = text.get_rect()
            screen.blit(text, (pos[node][0] + 8, pos[node][1] - 5))  # Moved the label beside the node

        if show_vertex_sublabels and sub_label:
            sub_text = sub_font.render(sub_label, True, (255, 0, 0))  # RED
            if show_vertex_labels:
                screen.blit(sub_text, (pos[node][0] + 8 + text_rect.width - 2, pos[node][1] - 5 + text_rect.height - 2))
            else:
                screen.blit(sub_text, (pos[node][0] + 8, pos[node][1] - 5))


def draw_boxes_and_charts(screen, all_graph_data, scale_factor):
    edge_font = pygame.font.SysFont('Arial', int(24 * scale_factor))
    l_mod_7_font = pygame.font.SysFont('Arial', int(20 * scale_factor))
    cell_size = int(50 * scale_factor)
    horizontal_margin = 5  # Adjust margin as needed; controls size of margin between box and charts on left tab
    total_width = NEW_LEFT_TAB_WIDTH - 2 * horizontal_margin
    grid_width = total_width // 2 - horizontal_margin
    chart_width = total_width // 2 - horizontal_margin
    start_y = MARGIN

    for graph_data in all_graph_data:
        start_x = horizontal_margin

        # Draw edge lengths grid
        pygame.draw.rect(screen, (0, 0, 0), (start_x, start_y, grid_width, cell_size * 3), 2)
        box_start_y = start_y + 10

        T = graph_data['T']
        distinct_lengths = sorted(set(T), key=lambda x: float('inf') if x == '∞' else x)
        # print(distinct_lengths)
        sorted_lengths = sorted(T, key=lambda x: float('inf') if x == '∞' else x)
        grid = [""] * 9

        if len(distinct_lengths) > 4:
            positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1)]
        else:
            positions = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2), (2, 1)]

        for i, length in enumerate(sorted_lengths):
            if i < 6:
                row, col = positions[i]
                grid[row * 3 + col] = length
            elif i == 6:
                grid[7] = length

        for i in range(3):
            for j in range(3):
                text = edge_font.render(str(grid[i * 3 + j]), True, DARK_GREEN)
                text_rect = text.get_rect(
                    center=(start_x + j * cell_size + cell_size // 2, box_start_y + i * cell_size + cell_size // 2))
                screen.blit(text, text_rect.topleft)

        # Draw l_mod_7 chart
        chart_start_x = start_x + grid_width + horizontal_margin
        chart_start_y = start_y
        max_rows = 0

        # simply sets the headers to each distinct length in chart if there are <= 4 distinct lengths
        if len(distinct_lengths) > 4:

            headers = distinct_lengths  # sets headers of the chart next to the box; sets headers to distinct lengths
            max_rows = max(len(graph_data['l_mod_7_values'].get(key, [])) for key in headers)
            lmin = headers[0]
            lmax = headers[len(headers) - 1]
            interval_text = l_mod_7_font.render(f"[{lmin},{lmax}]", True, DARK_GREEN)
            screen.blit(interval_text,
                        (chart_start_x + chart_width // 2 - interval_text.get_width() // 2, chart_start_y))
            pygame.draw.line(screen, (0, 0, 0), (chart_start_x, chart_start_y + 30),
                             (chart_start_x + chart_width, chart_start_y + 30), 2)
        else:
            headers = distinct_lengths  # sets headers of the chart next to the box; sets headers to distinct lengths

            for i, header in enumerate(headers):
                text = l_mod_7_font.render(str(header), True, DARK_GREEN)
                screen.blit(text, (chart_start_x + i * (chart_width // len(headers)) + 10, chart_start_y))
            line_end_x = chart_start_x + chart_width
            pygame.draw.line(screen, (0, 0, 0), (chart_start_x, chart_start_y + 30), (line_end_x, chart_start_y + 30),
                             2)

            l_mod_7_values = graph_data['l_mod_7_values']
            for i, header in enumerate(headers):
                values = sorted(l_mod_7_values.get(header, []))
                for j, value in enumerate(values):
                    text = l_mod_7_font.render(str(value), True, (255, 0, 0))
                    screen.blit(text, (chart_start_x + i * (chart_width // len(headers)) + 10,
                                       chart_start_y + 40 + j * int(30 * scale_factor)))

        start_y = max(chart_start_y + 40 + max_rows * int(30 * scale_factor) + 10, start_y + cell_size * 3 + 10)


# Function to draw the grid
def draw_grid(screen, width, height, spacing_x, spacing_y):
    for x in range(0, width, spacing_x):
        pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, height))
    for y in range(0, height, spacing_y):
        pygame.draw.line(screen, (200, 200, 200), (0, y), (width, y))


# Function to draw the slider
def draw_slider(screen, slider_rect, scale_factor):
    pygame.draw.rect(screen, (200, 200, 200), slider_rect)  # Slider background
    handle_rect = pygame.Rect(slider_rect.x, slider_rect.y + int((1 - scale_factor) * slider_rect.height),
                              slider_rect.width, 10)
    pygame.draw.rect(screen, (0, 128, 0), handle_rect)  # Slider handle (DARK_GREEN)


# Function to draw the vertical slider for vertex and label size
def draw_vertical_slider(screen, slider_rect, vertex_scale):
    pygame.draw.rect(screen, (200, 200, 200), slider_rect)  # Slider background
    handle_rect = pygame.Rect(slider_rect.x, slider_rect.y + int((1 - vertex_scale) * slider_rect.height),
                              slider_rect.width, 10)
    pygame.draw.rect(screen, (0, 128, 0), handle_rect)  # Slider handle (DARK_GREEN)


# Function to generate LaTeX code and save to specified location
def generate_latex(mod, pos_list, graphs, location, name, show_vertex_labels, show_vertex_sublabels, show_edge_labels,
                   show_edge_sublabels):
    output_dir = os.path.join(location if location != "default" else os.path.dirname(os.path.abspath(__file__)), name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    latex_code = "\\documentclass{standalone}\n\\usepackage{tikz}\n\\begin{document}\n"
    latex_code += "\\begin{tikzpicture}[every node/.style={draw, circle, fill=black, minimum size=2pt, inner sep=0pt}]\n"

    for idx, (pos, G) in enumerate(zip(pos_list, graphs)):
        graph_label = f"G{idx + 1}"
        for node, (x, y) in pos.items():
            node_label = "\\infty" if node == math.inf else str(node % mod)
            sub_label = "" if node == math.inf else str(node % 7)
            y = DEFAULT_HEIGHT - y  # Reflect y-coordinate for LaTeX
            node_id = f"{graph_label}N{node}"
            if show_vertex_labels and show_vertex_sublabels and sub_label:
                latex_code += f"\\node[fill=black, label=below:{{\\color{{black}}${node_label}_{{\\textcolor{{red}}{sub_label}}}$}}] ({node_id}) at ({x / 100:.2f},{y / 100:.2f}) {{}};\n"
            elif show_vertex_labels:
                latex_code += f"\\node[fill=black, label=below:{{\\color{{black}}${node_label}$}}] ({node_id}) at ({x / 100:.2f},{y / 100:.2f}) {{}};\n"
            elif show_vertex_sublabels and sub_label:
                latex_code += f"\\node[fill=black, label=below:{{\\color{{black}}$_{{\\textcolor{{red}}{sub_label}}}$}}] ({node_id}) at ({x / 100:.2f},{y / 100:.2f}) {{}};\n"
            else:
                latex_code += f"\\node[fill=black] ({node_id}) at ({x / 100:.2f},{y / 100:.2f}) {{}};\n"

        for edge in G.edges():
            x, y = edge
            l_e = "$\\infty$" if x == math.inf or y == math.inf else min(abs(x - y), mod - abs(x - y))
            if x == math.inf:
                l_mod_7 = y % 7
            elif y == math.inf:
                l_mod_7 = x % 7
            else:
                l_mod_7 = (x + y) % 7

            if show_edge_labels and show_edge_sublabels:
                latex_code += f"\\draw ({graph_label}N{x}) -- node[midway, sloped, above, draw=none, fill=none] {{\\textcolor{{green}}{{{l_e}}}$_{{\\textcolor{{red}}{{{l_mod_7}}}}}$}} ({graph_label}N{y});\n"
            elif show_edge_labels:
                latex_code += f"\\draw ({graph_label}N{x}) -- node[midway, sloped, above, draw=none, fill=none] {{\\textcolor{{green}}{{{l_e}}}}} ({graph_label}N{y});\n"
            elif show_edge_sublabels:
                latex_code += f"\\draw ({graph_label}N{x}) -- node[midway, sloped, above, draw=none, fill=none] {{$_{{\\textcolor{{red}}{{{l_mod_7}}}}}$}} ({graph_label}N{y});\n"
            else:
                latex_code += f"\\draw ({graph_label}N{x}) -- ({graph_label}N{y});\n"

    latex_code += "\\end{tikzpicture}\n"
    latex_code += "\\end{document}\n"

    with open(os.path.join(output_dir, f"{name}.tex"), "w") as f:
        f.write(latex_code)

    print(f"LaTeX code saved to {os.path.join(output_dir, f'{name}.tex')}")


def visualize(mod, graphs, name, location="default"):
    global show_grid  # Declare the variable as global
    pygame.init()
    WIDTH, HEIGHT = DEFAULT_WIDTH, DEFAULT_HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Interactive Draggable Graphs")

    num_graphs = len(graphs)
    section_height = HEIGHT // num_graphs

    pos_list = []
    x_spacing, y_spacing = 50, 50  # Default node spacing
    component_spacing = 50  # Increased spacing between components
    vertical_spacing = 75  # Spacing between rows of components

    for i, G in enumerate(graphs):
        # Debug information
        print(f"Graph {i}: Type {type(G)}, Value {G}")

        if not isinstance(G, nx.Graph):
            print(f"Error: Expected a networkx graph but got {type(G)}")
            continue

        pos = {}
        start_y = i * section_height + MARGIN
        components = list(nx.connected_components(G))
        component_start_x = NEW_LEFT_TAB_WIDTH + MARGIN

        for j, component in enumerate(components):
            if j > 0 and j % 3 == 0:  # Move to next row after every 3 components
                component_start_x = NEW_LEFT_TAB_WIDTH + MARGIN
                start_y += vertical_spacing
            subgraph = G.subgraph(component)
            arrange_tree(subgraph, pos, component_start_x, start_y, x_spacing, y_spacing)
            max_x = max(pos[node][0] for node in component)
            component_start_x = max_x + component_spacing  # Add spacing for next component

        pos_list.append(pos)

    left_tab_open = True
    right_tab_open = True
    scale_factor = 1.0
    vertex_scale = 1.0  # Default size set to 1.0

    slider_rect = pygame.Rect(NEW_LEFT_TAB_WIDTH - 20, HEIGHT - 180, 20, 160)
    vertical_slider_rect = pygame.Rect(WIDTH - RIGHT_TAB_WIDTH + MARGIN + 160, HEIGHT - 180, 20, 160)
    show_vertex_labels = True
    show_vertex_sublabels = True
    show_edge_labels = True
    show_edge_sublabels = True

    all_graph_data = []
    for G, pos in zip(graphs, pos_list):
        edge_lengths = []
        l_mod_7_values = {8: [], 9: [], 10: [], '∞': []}

        for edge in G.edges():
            x, y = edge
            l_e = "∞" if x == math.inf or y == math.inf else min(abs(x - y), mod - abs(x - y))

            if x == math.inf:
                l_mod_7 = y % 7
            elif y == math.inf:
                l_mod_7 = x % 7
            else:
                l_mod_7 = (x + y) % 7
            edge_lengths.append(l_e)
            if l_e in l_mod_7_values:
                l_mod_7_values[l_e].append(l_mod_7)
            else:
                l_mod_7_values[l_e] = [l_mod_7]
        T = edge_lengths
        all_graph_data.append({'T': T, 'l_mod_7_values': l_mod_7_values})
        # print(l_mod_7_values)

    running = True
    selected_node = None
    selected_pos = None
    dragging_slider = False
    dragging_vertical_slider = False
    dragging_slider_offset = 0
    dragging_vertical_slider_offset = 0

    # Variables for graph dragging
    dragging_graph = False
    initial_click_position = (0, 0)

    # Button for toggling the grid
    grid_button = {"label": "Toggle Grid", "state": False, "pos": (WIDTH - RIGHT_TAB_WIDTH + MARGIN, 450)}

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if event.button == 1:  # Left click
                    if left_tab_open and NEW_LEFT_TAB_WIDTH - 20 < mouse_x < NEW_LEFT_TAB_WIDTH and HEIGHT - 180 < mouse_y < HEIGHT - 20:
                        dragging_slider = True
                        dragging_slider_offset = mouse_y - slider_rect.y
                    elif right_tab_open and WIDTH - RIGHT_TAB_WIDTH + MARGIN + 160 < mouse_x < WIDTH - RIGHT_TAB_WIDTH + MARGIN + 180 and HEIGHT - 180 < mouse_y < HEIGHT - 20:
                        dragging_vertical_slider = True
                        dragging_vertical_slider_offset = mouse_y - vertical_slider_rect.y
                    elif left_tab_open and NEW_LEFT_TAB_WIDTH - 20 <= mouse_x <= NEW_LEFT_TAB_WIDTH and HEIGHT // 2 - 20 <= mouse_y <= HEIGHT // 2 + 20:
                        left_tab_open = not left_tab_open
                    elif not left_tab_open and 0 <= mouse_x <= 20 and HEIGHT // 2 - 20 <= mouse_y <= HEIGHT // 2 + 20:
                        left_tab_open = not left_tab_open
                    elif right_tab_open and WIDTH - RIGHT_TAB_WIDTH <= mouse_x <= WIDTH - RIGHT_TAB_WIDTH + 20 and HEIGHT // 2 - 20 <= mouse_y <= HEIGHT // 2 + 20:
                        right_tab_open = not right_tab_open
                    elif not right_tab_open and WIDTH - 20 <= mouse_x <= WIDTH and HEIGHT // 2 - 20 <= mouse_y <= HEIGHT // 2 + 20:
                        right_tab_open = not right_tab_open
                    elif right_tab_open and WIDTH - RIGHT_TAB_WIDTH + MARGIN <= mouse_x <= WIDTH - RIGHT_TAB_WIDTH + MARGIN + 140 and 450 <= mouse_y <= 510:
                        show_grid = not show_grid
                        grid_button["state"] = show_grid
                    else:
                        for pos in pos_list:
                            for node in pos:
                                node_x, node_y = pos[node]
                                if (node_x - mouse_x) ** 2 + (node_y - mouse_y) ** 2 < 10 ** 2:
                                    selected_node = node
                                    selected_pos = pos
                                    break
                        if right_tab_open:
                            if WIDTH - RIGHT_TAB_WIDTH + MARGIN <= mouse_x <= WIDTH - RIGHT_TAB_WIDTH + MARGIN + 140 and 50 <= mouse_y <= 110:
                                generate_latex(mod, pos_list, graphs, location, name, show_vertex_labels,
                                               show_vertex_sublabels, show_edge_labels, show_edge_sublabels)
                            for button in buttons:
                                button_rect = pygame.Rect(button["pos"][0], button["pos"][1], 140, 60)
                                if button_rect.collidepoint(event.pos):
                                    button["state"] = not button["state"]
                                    if button["label"] == "vertex labels":
                                        show_vertex_labels = button["state"]
                                    elif button["label"] == "vertex subscript labels":
                                        show_vertex_sublabels = button["state"]
                                    elif button["label"] == "edge labels":
                                        show_edge_labels = button["state"]
                                    elif button["label"] == "edge subscript labels":
                                        show_edge_sublabels = button["state"]
                elif event.button == 3:  # Right click
                    for pos in pos_list:
                        for node in pos:
                            node_x, node_y = pos[node]
                            if (node_x - mouse_x) ** 2 + (node_y - mouse_y) ** 2 < 10 ** 2:
                                dragging_graph = True
                                selected_pos = pos
                                initial_click_position = (mouse_x, mouse_y)
                                break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    selected_node = None
                    dragging_slider = False
                    dragging_vertical_slider = False
                elif event.button == 3:
                    dragging_graph = False
            elif event.type == pygame.MOUSEMOTION:
                if selected_node is not None:
                    selected_pos[selected_node] = event.pos
                if dragging_slider:
                    mouse_y = event.pos[1]
                    new_y = mouse_y - dragging_slider_offset
                    slider_rect.y = max(min(new_y, HEIGHT - 20), HEIGHT - 180)
                    scale_factor = 1 - ((slider_rect.y - (HEIGHT - 180)) / 160)
                if dragging_vertical_slider:
                    mouse_y = event.pos[1]
                    new_y = mouse_y - dragging_vertical_slider_offset
                    vertical_slider_rect.y = max(min(new_y, HEIGHT - 20), HEIGHT - 250)
                    vertex_scale = 1 - ((vertical_slider_rect.y - (HEIGHT - 180)) / 160)
                if dragging_graph:
                    mouse_x, mouse_y = event.pos
                    dx = mouse_x - initial_click_position[0]
                    dy = mouse_y - initial_click_position[1]
                    for node in selected_pos:
                        selected_pos[node] = (selected_pos[node][0] + dx, selected_pos[node][1] + dy)
                    initial_click_position = (mouse_x, mouse_y)

        screen.fill((255, 255, 255))  # Clear the screen

        if show_grid:
            draw_grid(screen, WIDTH, HEIGHT, x_spacing, y_spacing)

        for G, pos in zip(graphs, pos_list):
            draw_graph(mod, screen, G, pos, show_vertex_labels, show_vertex_sublabels, show_edge_labels,
                       show_edge_sublabels, vertex_scale=1.0)

        if left_tab_open:
            pygame.draw.rect(screen, (200, 200, 200),
                             (0, 0, NEW_LEFT_TAB_WIDTH, HEIGHT))  # Shaded gray background for left tab
            draw_boxes_and_charts(screen, all_graph_data, scale_factor)
            draw_slider(screen, slider_rect, scale_factor)

        if right_tab_open:
            pygame.draw.rect(screen, (200, 200, 200), (WIDTH - RIGHT_TAB_WIDTH, 0, RIGHT_TAB_WIDTH, HEIGHT))
            pygame.draw.rect(screen, (0, 128, 0), (WIDTH - RIGHT_TAB_WIDTH + MARGIN, 50, 140, 60))
            save_text = pygame.font.SysFont('Arial', 18).render("Save", True, (0, 0, 0))
            screen.blit(save_text, (
            WIDTH - RIGHT_TAB_WIDTH + MARGIN + 70 - save_text.get_width() // 2, 80 - save_text.get_height() // 2))

            buttons = [
                {"label": "vertex labels", "state": show_vertex_labels, "pos": (WIDTH - RIGHT_TAB_WIDTH + MARGIN, 130)},
                {"label": "vertex subscript labels", "state": show_vertex_sublabels,
                 "pos": (WIDTH - RIGHT_TAB_WIDTH + MARGIN, 210)},
                {"label": "edge labels", "state": show_edge_labels, "pos": (WIDTH - RIGHT_TAB_WIDTH + MARGIN, 290)},
                {"label": "edge subscript labels", "state": show_edge_sublabels,
                 "pos": (WIDTH - RIGHT_TAB_WIDTH + MARGIN, 370)},
            ]

            for button in buttons:
                color = (0, 128, 0) if button["state"] else (255, 0, 0)
                text = f"{button['label']} {'on' if button['state'] else 'off'}"
                button_font_size = 18
                button_font = pygame.font.SysFont('Arial', button_font_size)
                button_text = button_font.render(text, True, (0, 0, 0))

                while button_text.get_width() > 140 - MARGIN * 2 and button_font_size > 10:
                    button_font_size -= 1
                    button_font = pygame.font.SysFont('Arial', button_font_size)
                    button_text = button_font.render(text, True, (0, 0, 0))

                pygame.draw.rect(screen, color, (*button["pos"], 140, 60))
                screen.blit(button_text, (button["pos"][0] + 70 - button_text.get_width() // 2,
                                          button["pos"][1] + 30 - button_text.get_height() // 2))

            # Draw grid toggle button
            grid_button_color = (0, 128, 0) if grid_button["state"] else (255, 0, 0)
            pygame.draw.rect(screen, grid_button_color, (*grid_button["pos"], 140, 60))
            grid_button_text = pygame.font.SysFont('Arial', 18).render(grid_button["label"], True, (0, 0, 0))
            screen.blit(grid_button_text, (grid_button["pos"][0] + 70 - grid_button_text.get_width() // 2,
                                           grid_button["pos"][1] + 30 - grid_button_text.get_height() // 2))

            draw_vertical_slider(screen, vertical_slider_rect, vertex_scale)

        tab_button_font = pygame.font.SysFont('Arial', 14)
        if left_tab_open:
            pygame.draw.rect(screen, (150, 150, 150), (NEW_LEFT_TAB_WIDTH - 20, HEIGHT // 2 - 20, 20, 40))
            tab_text = tab_button_font.render("<", True, (0, 0, 0))
            screen.blit(tab_text, (NEW_LEFT_TAB_WIDTH - 20 + 10 - tab_text.get_width() // 2,
                                   HEIGHT // 2 - 20 + 20 - tab_text.get_height() // 2))
        else:
            pygame.draw.rect(screen, (150, 150, 150), (0, HEIGHT // 2 - 20, 20, 40))
            tab_text = tab_button_font.render(">", True, (0, 0, 0))
            screen.blit(tab_text, (10 - tab_text.get_width() // 2, HEIGHT // 2 - 20 + 20 - tab_text.get_height() // 2))

        if right_tab_open:
            pygame.draw.rect(screen, (150, 150, 150), (WIDTH - RIGHT_TAB_WIDTH, HEIGHT // 2 - 20, 20, 40))
            tab_text = tab_button_font.render(">", True, (0, 0, 0))
            screen.blit(tab_text, (WIDTH - RIGHT_TAB_WIDTH + 10 - tab_text.get_width() // 2,
                                   HEIGHT // 2 - 20 + 20 - tab_text.get_height() // 2))
        else:
            pygame.draw.rect(screen, (150, 150, 150), (WIDTH - 20, HEIGHT // 2 - 20, 20, 40))
            tab_text = tab_button_font.render("<", True, (0, 0, 0))
            screen.blit(tab_text,
                        (WIDTH - 10 - tab_text.get_width() // 2, HEIGHT // 2 - 20 + 20 - tab_text.get_height() // 2))

        pygame.display.flip()

    pygame.quit()
