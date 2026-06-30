import heapq
import math
import random
from collections import deque

class AIEngine:
    @staticmethod
    def get_neighbors(pos, grid_map, grid_size, allow_diagonals=False):
        x, y = pos
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if allow_diagonals:
            directions += [(-1, -1), (1, 1), (-1, 1), (1, -1)]
            
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                if grid_map[ny][nx] != 1:  
                    neighbors.append((nx, ny))
        return neighbors

    # ================== MÀN 1 ==================
    @staticmethod
    def solve_bfs(start, goal, grid_map, grid_size):
        queue = deque([start])
        parent = {start: None}
        visited = set([start])
        visited_order = []
        while queue:
            curr = queue.popleft()
            visited_order.append(curr)
            if curr == goal:
                path = []
                while curr is not None:
                    path.append(curr)
                    curr = parent[curr]
                return path[::-1], visited_order
            for neighbor in AIEngine.get_neighbors(curr, grid_map, grid_size):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = curr
                    queue.append(neighbor)
        return [], visited_order

    @staticmethod
    def solve_dfs(start, goal, grid_map, grid_size):
        stack = [start]
        parent = {start: None}
        visited = set([start])
        visited_order = []
        while stack:
            curr = stack.pop()
            visited_order.append(curr)
            if curr == goal:
                path = []
                while curr is not None:
                    path.append(curr)
                    curr = parent[curr]
                return path[::-1], visited_order
            for neighbor in AIEngine.get_neighbors(curr, grid_map, grid_size):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = curr
                    stack.append(neighbor)
        return [], visited_order

    @staticmethod
    def solve_ucs(start, goal, grid_map, grid_size):
        open_set = []
        heapq.heappush(open_set, (0, start))
        parent = {start: None}
        g_score = {start: 0}
        visited_order = []
        while open_set:
            current_cost, current = heapq.heappop(open_set)
            if current not in visited_order:
                visited_order.append(current)
            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = parent[current]
                return path[::-1], visited_order
            for neighbor in AIEngine.get_neighbors(current, grid_map, grid_size):
                step_cost = 12 if grid_map[neighbor[1]][neighbor[0]] == 3 else 1
                tentative_g = current_cost + step_cost
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    parent[neighbor] = current
                    heapq.heappush(open_set, (tentative_g, neighbor))
        return [], visited_order

    # ================== MÀN 2 ==================
    @staticmethod
    def heuristic(pos1, pos2):
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return (dx + dy) * 1.001 
    @staticmethod
    def terrain_cost(cell):
        if cell == 3:
            return 12
        return 1

    @staticmethod
    def solve_greedy_bfs(start, goal, grid_map, grid_size):
        open_set = []
        heapq.heappush(open_set, (AIEngine.heuristic(start, goal), start))
        parent = {start: None}
        visited = set([start])
        visited_order = []
        while open_set:
            _, current = heapq.heappop(open_set)
            visited_order.append(current)
            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = parent[current]
                return path[::-1], visited_order
            for neighbor in AIEngine.get_neighbors(current, grid_map, grid_size):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    heapq.heappush(open_set, (AIEngine.heuristic(neighbor, goal), neighbor))
        return [], visited_order

    @staticmethod
    def solve_a_star(start, goal, grid_map, grid_size):
        open_set = []
        heapq.heappush(open_set, (AIEngine.heuristic(start, goal), 0, start))
        parent = {start: None}
        g_score = {start: 0}
        visited_order = [] 
        while open_set:
            _, current_g, current = heapq.heappop(open_set)
            if current not in visited_order:
                visited_order.append(current)
            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = parent[current]
                return path[::-1], visited_order
            for neighbor in AIEngine.get_neighbors(current, grid_map, grid_size):
                cell = grid_map[neighbor[1]][neighbor[0]]
                tentative_g = current_g + AIEngine.terrain_cost(cell)
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + AIEngine.heuristic(neighbor, goal)
                    parent[neighbor] = current
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))
        return [], visited_order

    @staticmethod
    def solve_ida_star(start, goal, grid_map, grid_size):
        nodes_counted = 0

        def search(path, g, bound):
            nonlocal nodes_counted
            node = path[-1]
            f = g + AIEngine.heuristic(node, goal)
            nodes_counted += 1

            if f > bound:
                return f

            if node == goal:
                return "FOUND"

            min_bound = float('inf')
            neighbors = AIEngine.get_neighbors(node, grid_map, grid_size)
            neighbors.sort(key=lambda n: AIEngine.heuristic(n, goal))

            for neighbor in neighbors:
                if neighbor not in path:
                    cell = grid_map[neighbor[1]][neighbor[0]]
                    step_cost = AIEngine.terrain_cost(cell)

                    path.append(neighbor)
                    t = search(path, g + step_cost, bound)

                    if t == "FOUND":
                        return "FOUND"

                    if t < min_bound:
                        min_bound = t

                    path.pop()

            return min_bound

        bound = AIEngine.heuristic(start, goal)
        path = [start]

        while True:
            t = search(path, 0, bound)

            if t == "FOUND":
                return path, nodes_counted

            if t == float('inf'):
                return [], nodes_counted

            bound = t

    # ================== MÀN 3 ==================
    @staticmethod
    def solve_hill_climbing(start, grid_map, grid_size):
        curr = start
        path = [curr]
        visited = [curr]
        while True:
            neighbors = AIEngine.get_neighbors(curr, grid_map, grid_size, allow_diagonals=True)
            if not neighbors: break
            best_n = None
            best_val = grid_map[curr[1]][curr[0]]
            for n in neighbors:
                val = grid_map[n[1]][n[0]]
                if val > best_val:
                    best_val = val
                    best_n = n
            if best_n:
                curr = best_n
                path.append(curr)
                visited.append(curr)
            else: break
        return path, visited

    @staticmethod
    def solve_simulated_annealing(start, grid_map, grid_size):
        curr = start
        path = [curr]
        visited = [curr]
        T = 100.0
        min_T = 0.01
        cooling_rate = 0.95
        while T > min_T:
            neighbors = AIEngine.get_neighbors(curr, grid_map, grid_size, allow_diagonals=True)
            if not neighbors: break
            next_node = random.choice(neighbors)
            delta = grid_map[next_node[1]][next_node[0]] - grid_map[curr[1]][curr[0]]
            if delta > 0 or random.random() < math.exp(delta / T):
                curr = next_node
                path.append(curr)
                visited.append(curr)
            else:
                best_n = max(neighbors, key=lambda x: grid_map[x[1]][x[0]])
                if grid_map[best_n[1]][best_n[0]] > grid_map[curr[1]][curr[0]]:
                    curr = best_n
                    path.append(curr)
                    visited.append(curr)
            T *= cooling_rate
        return path, visited

    @staticmethod
    def solve_local_beam_search(start, grid_map, grid_size, k=3):
        states = [start]
        path = [start]
        visited = [start]
        for _ in range(100):
            all_neighbors = []
            for s in states:
                all_neighbors.extend(AIEngine.get_neighbors(s, grid_map, grid_size, allow_diagonals=True))
            if not all_neighbors: break
            
            all_neighbors.sort(key=lambda n: grid_map[n[1]][n[0]], reverse=True)
            
            next_states = []
            for n in all_neighbors:
                if n not in next_states: next_states.append(n)
                if len(next_states) == k: break
                
            best_next = next_states[0]
            best_curr = states[0]
            
            if grid_map[best_next[1]][best_next[0]] <= grid_map[best_curr[1]][best_curr[0]]:
                break 
                
            states = next_states
            path.append(best_next)
            visited.extend(states)
        return path, visited

        # ================== MÀN 4 ==================
    @staticmethod
    def wall_risk(pos, grid_map, grid_size):
        x, y = pos
        risk = 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if not (0 <= nx < grid_size and 0 <= ny < grid_size):
                risk += 2
            elif grid_map[ny][nx] == 1:
                risk += 2

        return risk

    @staticmethod
    def free_degree(pos, grid_map, grid_size):
        return len(AIEngine.get_neighbors(pos, grid_map, grid_size))

    @staticmethod
    def reconstruct_path(parent, current):
        path = []
        while current is not None:
            path.append(current)
            current = parent[current]
        return path[::-1]

    @staticmethod
    def solve_belief_state(start, goal, grid_map, grid_size):
        """
        Mô phỏng Belief State Search bằng A* có xét rủi ro.
        Ý tưởng: trong môi trường không chắc chắn, tác nhân không chỉ đi gần đích,
        mà còn tránh các ô sát tường vì các ô này ít lựa chọn nếu bản đồ thay đổi.
        """
        open_set = []
        heapq.heappush(open_set, (AIEngine.heuristic(start, goal), 0, start))

        parent = {start: None}
        g_score = {start: 0}
        visited_order = []

        while open_set:
            _, current_g, current = heapq.heappop(open_set)

            if current not in visited_order:
                visited_order.append(current)

            if current == goal:
                return AIEngine.reconstruct_path(parent, current), visited_order

            for neighbor in AIEngine.get_neighbors(current, grid_map, grid_size):
                risk_penalty = AIEngine.wall_risk(neighbor, grid_map, grid_size) * 0.7
                tentative_g = current_g + 1 + risk_penalty

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    parent[neighbor] = current

                    f_score = tentative_g + AIEngine.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))

        return [], visited_order

    @staticmethod
    def solve_and_or_search(start, goal, grid_map, grid_size):
        """
        Mô phỏng AND-OR Search bằng tìm kiếm thận trọng.
        Ý tưởng: ưu tiên các ô có nhiều hướng đi tiếp theo để có phương án dự phòng
        khi môi trường thay đổi.
        """
        queue = deque([start])
        parent = {start: None}
        visited = {start}
        visited_order = []

        while queue:
            current = queue.popleft()
            visited_order.append(current)

            if current == goal:
                return AIEngine.reconstruct_path(parent, current), visited_order

            neighbors = AIEngine.get_neighbors(current, grid_map, grid_size)

            # Ưu tiên ô có nhiều đường thoát, sau đó mới xét gần đích.
            neighbors.sort(
                key=lambda p: (
                    -AIEngine.free_degree(p, grid_map, grid_size),
                    AIEngine.heuristic(p, goal)
                )
            )

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        return [], visited_order

    @staticmethod
    def solve_luyen_thep(start, goal, grid_map, grid_size):
        """
        Simulated Annealing cho môi trường ảo ảnh.
        Thuật toán có yếu tố ngẫu nhiên, đôi khi chấp nhận bước đi kém hơn
        để tránh bị kẹt. Nếu chưa tới đích, nối phần còn lại bằng A*
        để đảm bảo demo có thể hoàn thành.
        """
        current = start
        path = [current]
        visited_order = [current]

        T = 15.0
        min_T = 0.2
        cooling_rate = 0.96
        max_steps = grid_size * 4

        def energy(pos):
            repeat_penalty = 8 if pos in path[-6:] else 0
            risk_penalty = AIEngine.wall_risk(pos, grid_map, grid_size) * 0.4
            return AIEngine.heuristic(pos, goal) + repeat_penalty + risk_penalty

        for _ in range(max_steps):
            if current == goal:
                return path, visited_order

            neighbors = AIEngine.get_neighbors(current, grid_map, grid_size)
            if not neighbors:
                break

            next_node = random.choice(neighbors)

            delta = energy(next_node) - energy(current)

            if delta < 0 or random.random() < math.exp(-delta / max(T, 0.001)):
                current = next_node
                path.append(current)
                visited_order.append(current)

            T *= cooling_rate

            if T < min_T:
                break

        # Nối phần còn lại bằng A* để đảm bảo màn chơi có thể hoàn thành.
        tail_path, tail_visited = AIEngine.solve_a_star(current, goal, grid_map, grid_size)

        if tail_path:
            return path + tail_path[1:], visited_order + tail_visited

        return path, visited_order
    # ================== MÀN 5 ==================
    @staticmethod
    def solve_csp_backtracking(grid_size):
        board = [[0] * grid_size for _ in range(grid_size)]
        history = []
        visited_nodes = [] 
        nodes_counted = 0
        def is_safe(b, row, col):
            for i in range(col):
                if b[row][i] == 1: return False
            for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
                if b[i][j] == 1: return False
            for i, j in zip(range(row, grid_size, 1), range(col, -1, -1)):
                if b[i][j] == 1: return False
            return True
        def backtrack(col):
            nonlocal nodes_counted
            if col >= grid_size: return True
            for i in range(grid_size):
                nodes_counted += 1
                visited_nodes.append((col, i)) 
                if is_safe(board, i, col):
                    board[i][col] = 1
                    history.append([row[:] for row in board])
                    if backtrack(col + 1): return True
                    board[i][col] = 0
                    history.append([row[:] for row in board])
            return False
        backtrack(0)
        return history, nodes_counted, visited_nodes

    @staticmethod
    def solve_csp_forward_checking(grid_size):
        board = [[0] * grid_size for _ in range(grid_size)]
        history = []
        visited_nodes = []
        nodes_counted = 0
        def is_safe(b, row, col):
            for i in range(col):
                if b[row][i] == 1: return False
            for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
                if b[i][j] == 1: return False
            for i, j in zip(range(row, grid_size, 1), range(col, -1, -1)):
                if b[i][j] == 1: return False
            return True
        def forward_check_predict(b, col):
            for c in range(col + 1, grid_size):
                has_safe_row = False
                for r in range(grid_size):
                    if is_safe(b, r, c):
                        has_safe_row = True
                        break
                if not has_safe_row: return False
            return True
        # Định nghĩa hàm backtrack dành riêng cho Forward Checking
        def backtrack_fc(col):
            nonlocal nodes_counted
            if col >= grid_size: return True
            for r in range(grid_size):
                nodes_counted += 1
                visited_nodes.append((col, r))
                if is_safe(board, r, col):
                    board[r][col] = 1
                    history.append([row[:] for row in board])
                    
                    # Gọi trực tiếp predict tại đây, không cần biến cờ
                    if forward_check_predict(board, col): 
                        if backtrack_fc(col + 1): return True
                        
                    board[r][col] = 0
                    history.append([row[:] for row in board])
            return False

        found = backtrack_fc(0)
        return history if found else [], nodes_counted, visited_nodes

    @staticmethod
    def solve_min_conflicts(grid_size, max_steps=2000, restarts=20):
        """Min-Conflicts cho N-Queens.

        Khác với bản cũ:
        - Không tự động fallback sang Forward Checking, vì fallback làm kết quả dễ giống thuật toán 2.
        - Có nhiều lần restart để tăng xác suất tìm nghiệm.
        - nodes_counted đếm cả bước kiểm tra conflict và bước thử hàng mới.
        """
        best_history = []
        best_visited_nodes = []
        nodes_counted = 0

        for _restart in range(restarts):
            state = [random.randint(0, grid_size - 1) for _ in range(grid_size)]
            history = []
            visited_nodes = []

            def make_board():
                b = [[0] * grid_size for _ in range(grid_size)]
                for c in range(grid_size):
                    b[state[c]][c] = 1
                return b

            def conflicts_for(col, row):
                count = 0
                for other_col in range(grid_size):
                    if other_col == col:
                        continue
                    other_row = state[other_col]
                    if row == other_row or abs(row - other_row) == abs(col - other_col):
                        count += 1
                return count

            for _step in range(max_steps):
                history.append(make_board())

                conflicted_cols = []
                for c in range(grid_size):
                    nodes_counted += 1
                    visited_nodes.append((c, state[c]))
                    if conflicts_for(c, state[c]) > 0:
                        conflicted_cols.append(c)

                if not conflicted_cols:
                    return history, nodes_counted, visited_nodes

                col = random.choice(conflicted_cols)

                scores = []
                for r in range(grid_size):
                    nodes_counted += 1
                    scores.append((conflicts_for(col, r), r))

                min_score = min(score for score, _r in scores)
                best_rows = [r for score, r in scores if score == min_score]
                state[col] = random.choice(best_rows)

            if len(history) > len(best_history):
                best_history = history
                best_visited_nodes = visited_nodes

        return [], nodes_counted, best_visited_nodes

    # ================== MÀN 6 ==================
    @staticmethod
    def build_distance_map(goal_pos, grid_map, grid_size):
        """BFS từ đích để tạo khoảng cách thật có xét tường."""
        INF = 10**9
        dist = [[INF] * grid_size for _ in range(grid_size)]
        q = deque([goal_pos])
        gx, gy = goal_pos
        dist[gy][gx] = 0

        while q:
            x, y = q.popleft()
            for nx, ny in AIEngine.get_neighbors((x, y), grid_map, grid_size):
                if dist[ny][nx] == INF:
                    dist[ny][nx] = dist[y][x] + 1
                    q.append((nx, ny))
        return dist

    @staticmethod
    def eval_game_state(player_pos, ghost_pos, goal_pos, grid_map=None, grid_size=15, history_penalty=None, mode="adversarial"):
     dist_to_goal = abs(player_pos[0] - goal_pos[0]) + abs(player_pos[1] - goal_pos[1])
     dist_to_ghost = abs(player_pos[0] - ghost_pos[0]) + abs(player_pos[1] - ghost_pos[1])

     if player_pos == ghost_pos:
        return -999999

     if player_pos == goal_pos:
        return 999999

     score = -dist_to_goal * 100

     if mode == "adversarial":
        # Minimax / Alpha-Beta: phòng thủ mạnh
        if dist_to_ghost <= 1:
            score -= 10000
        elif dist_to_ghost == 2:
            score -= 3000
        elif dist_to_ghost == 3:
            score -= 800

     elif mode == "expectimax":
        # Expectimax: chấp nhận rủi ro hơn để đi ngắn hơn
        if dist_to_ghost <= 1:
            score -= 8000
        elif dist_to_ghost == 2:
            score -= 1200
        elif dist_to_ghost == 3:
            score -= 200

     if history_penalty and player_pos in history_penalty[-8:]:
        score -= 500

     return score

    @staticmethod
    def ordered_player_moves(player_pos, grid_map, grid_size, dist_map):
        moves = AIEngine.get_neighbors(player_pos, grid_map, grid_size)
        moves.sort(key=lambda p: dist_map[p[1]][p[0]])
        return moves

    @staticmethod
    def ordered_ghost_moves(ghost_pos, player_pos, grid_map, grid_size):
        moves = AIEngine.get_neighbors(ghost_pos, grid_map, grid_size)
        moves.sort(key=lambda g: abs(g[0] - player_pos[0]) + abs(g[1] - player_pos[1]))
        return moves

    @staticmethod
    def solve_minimax(player_pos, ghost_pos, grid_map, grid_size, depth=3, history=None, goal_pos=(14, 14)):
        nodes_counted = 0
        dist_map = AIEngine.build_distance_map(goal_pos, grid_map, grid_size)

        def min_value(p_pos, g_pos, d):
            nonlocal nodes_counted
            nodes_counted += 1
            if d == 0 or p_pos == goal_pos or p_pos == g_pos:
                return AIEngine.eval_game_state(p_pos, g_pos, goal_pos, history, dist_map)

            v = float('inf')
            for move in AIEngine.ordered_ghost_moves(g_pos, p_pos, grid_map, grid_size):
                v = min(v, max_value(p_pos, move, d - 1))
            return v

        def max_value(p_pos, g_pos, d):
            nonlocal nodes_counted
            nodes_counted += 1
            if d == 0 or p_pos == goal_pos or p_pos == g_pos:
                return AIEngine.eval_game_state(p_pos, g_pos, goal_pos, history, dist_map)

            v = -float('inf')
            for move in AIEngine.ordered_player_moves(p_pos, grid_map, grid_size, dist_map):
                v = max(v, min_value(move, g_pos, d - 1))
            return v

        best_move = None
        best_val = -float('inf')
        for move in AIEngine.ordered_player_moves(player_pos, grid_map, grid_size, dist_map):
            val = min_value(move, ghost_pos, depth - 1)
            if val > best_val:
                best_val = val
                best_move = move

        return [best_move] if best_move else [player_pos], nodes_counted

    @staticmethod
    def solve_alpha_beta(player_pos, ghost_pos, grid_map, grid_size, depth=5, history=None, goal_pos=(14, 14)):
        nodes_counted = 0
        dist_map = AIEngine.build_distance_map(goal_pos, grid_map, grid_size)

        def min_value(p_pos, g_pos, d, alpha, beta):
            nonlocal nodes_counted
            nodes_counted += 1
            if d == 0 or p_pos == goal_pos or p_pos == g_pos:
                return AIEngine.eval_game_state(p_pos, g_pos, goal_pos, history, dist_map)

            v = float('inf')
            for move in AIEngine.ordered_ghost_moves(g_pos, p_pos, grid_map, grid_size):
                v = min(v, max_value(p_pos, move, d - 1, alpha, beta))
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v

        def max_value(p_pos, g_pos, d, alpha, beta):
            nonlocal nodes_counted
            nodes_counted += 1
            if d == 0 or p_pos == goal_pos or p_pos == g_pos:
                return AIEngine.eval_game_state(p_pos, g_pos, goal_pos, history, dist_map)

            v = -float('inf')
            for move in AIEngine.ordered_player_moves(p_pos, grid_map, grid_size, dist_map):
                v = max(v, min_value(move, g_pos, d - 1, alpha, beta))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            return v

        best_move = None
        best_val = -float('inf')
        alpha, beta = -float('inf'), float('inf')

        for move in AIEngine.ordered_player_moves(player_pos, grid_map, grid_size, dist_map):
            val = min_value(move, ghost_pos, depth - 1, alpha, beta)
            if val > best_val:
                best_val = val
                best_move = move
            alpha = max(alpha, val)

        return [best_move] if best_move else [player_pos], nodes_counted

    @staticmethod
    def solve_expectimax(player_pos, ghost_pos, grid_map, grid_size, depth=4, history=None, goal_pos=(14, 14)):
        nodes_counted = 0
        dist_map = AIEngine.build_distance_map(goal_pos, grid_map, grid_size)

        def exp_value(p_pos, g_pos, d):
            nonlocal nodes_counted
            nodes_counted += 1
            if d == 0 or p_pos == goal_pos or p_pos == g_pos:
                return AIEngine.eval_game_state(p_pos, g_pos, goal_pos, history, dist_map)

            neighbors = AIEngine.get_neighbors(g_pos, grid_map, grid_size)
            if not neighbors:
                return AIEngine.eval_game_state(p_pos, g_pos, goal_pos, history, dist_map)

            prob = 1.0 / len(neighbors)
            v = 0
            for move in neighbors:
                v += prob * max_value(p_pos, move, d - 1)
            return v

        def max_value(p_pos, g_pos, d):
            nonlocal nodes_counted
            nodes_counted += 1
            if d == 0 or p_pos == goal_pos or p_pos == g_pos:
                return AIEngine.eval_game_state(p_pos, g_pos, goal_pos, history, dist_map)

            v = -float('inf')
            for move in AIEngine.ordered_player_moves(p_pos, grid_map, grid_size, dist_map):
                v = max(v, exp_value(move, g_pos, d - 1))
            return v

        best_move = None
        best_val = -float('inf')
        for move in AIEngine.ordered_player_moves(player_pos, grid_map, grid_size, dist_map):
            val = exp_value(move, ghost_pos, depth - 1)
            if val > best_val:
                best_val = val
                best_move = move

        return [best_move] if best_move else [player_pos], nodes_counted
