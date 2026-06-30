# main.py
import pygame
import sys
import random
import time

from core.constants import *
from core.env_states import Stage1State, Stage2State, Stage3State, Stage4State, Stage5State, Stage6State
from core.ai_solvers import AIEngine
from ui.render_engine import RenderEngine
from ui.components import UIButton, UIRulesModal

class MainApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.virtual_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI Pathfinding Simulation")
        self.clock = pygame.time.Clock()
        
        self.ui_renderer = RenderEngine(self.virtual_surface)
        self.stages = {
            1: Stage1State(), 2: Stage2State(), 3: Stage3State(),
            4: Stage4State(), 5: Stage5State(), 6: Stage6State()
        }
        self.current_stage = 1
        self.selected_algo = 0 
        
        self.stage_btns = {i: UIButton((750 + ((i-1)%3)*120, 100 + ((i-1)//3)*45, 100, 35), f"Màn {i}", self.ui_renderer.font_text) for i in range(1, 7)}
        self.algo_btns = [UIButton((750, 220 + i*55, 320, 42), "", self.ui_renderer.font_text, is_algo=True) for i in range(3)]
        
        self.btn_run_ai = UIButton((1090, 220, 150, 42), "KÍCH HOẠT", self.ui_renderer.font_title)
        self.btn_replay = UIButton((1090, 275, 150, 42), "REPLAY", self.ui_renderer.font_title)
        self.btn_new = UIButton((1090, 330, 150, 42), "NEW MAP", self.ui_renderer.font_title)
        
        self.algo_names = {
            1: ["BFS (Mù - O(V+E))", "DFS (Mù - Dò sâu)", "UCS (Chi phí đồng đều)"],
            2: ["Greedy BFS (Heuristic)", "A* (Tối ưu)", "IDA* (O(bd) Tiết kiệm RAM)"],
            3: ["Hill Climbing", "Simulated Annealing", "Local Beam Search"],
            4: ["Belief State Search", "And Or", "Luyện thép"],
            5: ["Backtracking", "Forward Checking", "Min-Conflicts"],
            6: ["Minimax", "Alpha Beta", "Expectimax"]
        }
        
        self.rules_modal = UIRulesModal(750, 450, self.ui_renderer.font_title, self.ui_renderer.font_text)
        self.show_rules = True
        
        self.calculated_path = []
        self.visited_history = []
        self.manual_visited_path = []
        self.game_over_reason = None
        self.manual_start_time = None 
        self.is_animating = False
        self.anim_spread_step = 0 
        self.anim_path_step = 0   
        self.last_move_time = 0
        self.csp_nodes = 0
        self.ghost_path = []
        
        self.stats = {"Nodes Duyệt": 0, "Chi phí": 0, "Độ Dài": 0, "Thời Gian": "0.0 s", "Trạng thái": "Sẵn sàng"}
        self.history_stats = {i: [] for i in range(1, 7)}

    def reset_ui_state(self):
        self.calculated_path = []
        self.visited_history = []
        self.ghost_path = []
        self.manual_visited_path = []
        self.game_over_reason = None
        self.is_animating = False
        self.manual_start_time = None
        self.csp_nodes = 0
        self.ghost_path = []
        self.stats = {"Nodes Duyệt": 0, "Chi phí": 0, "Độ Dài": 0, "Thời Gian": "0.0 s", "Trạng thái": "Sẵn sàng"}

    def get_path_cost(self, path, grid_map):
        if not path or self.current_stage == 5: return 0
        cost = 0
        for i in range(1, len(path)):
            x, y = path[i]
            cost += 12 if isinstance(grid_map[y][x], int) and grid_map[y][x] == 3 else 1
        return cost

    def choose_ghost_move_stage6(self, ghost_pos, player_pos, grid_map, algo_idx, goal_pos):
        neighbors = AIEngine.get_neighbors(ghost_pos, grid_map, GRID_SIZE)
        if not neighbors:
            return ghost_pos

        # Minimax và Alpha-Beta giả định ma chơi đối kháng: chọn nước đi làm điểm của người chơi thấp nhất.
        if algo_idx in (0, 1):
            return min(
                neighbors,
                key=lambda g: AIEngine.eval_game_state(player_pos, g, goal_pos)
            )

        # Expectimax giả định ma có yếu tố ngẫu nhiên. Đường đi ma được lưu lại để replay không bị lệch.
        return random.choice(neighbors)

    def trigger_ai_solver(self):
        if self.game_over_reason: return
        state = self.stages[self.current_stage]
        
        if hasattr(state, 'explored_map'):
            state.explored_map = [[True]*GRID_SIZE for _ in range(GRID_SIZE)]
            
        start_time = time.perf_counter()
        exec_time = 0.0
        path, visited = [], []
        self.csp_nodes = 0
        
        if self.current_stage == 1:
            if self.selected_algo == 0: path, visited = AIEngine.solve_bfs(tuple(state.player_pos), state.goal_pos, state.grid_map, GRID_SIZE)
            elif self.selected_algo == 1: path, visited = AIEngine.solve_dfs(tuple(state.player_pos), state.goal_pos, state.grid_map, GRID_SIZE)
            elif self.selected_algo == 2: path, visited = AIEngine.solve_ucs(tuple(state.player_pos), state.goal_pos, state.grid_map, GRID_SIZE)
            
        elif self.current_stage == 2:
            if self.selected_algo == 0: path, visited = AIEngine.solve_greedy_bfs(tuple(state.player_pos), state.goal_pos, state.grid_map, GRID_SIZE)
            elif self.selected_algo == 1: path, visited = AIEngine.solve_a_star(tuple(state.player_pos), state.goal_pos, state.grid_map, GRID_SIZE)
            elif self.selected_algo == 2: path, visited = AIEngine.solve_ida_star(tuple(state.player_pos), state.goal_pos, state.grid_map, GRID_SIZE)
            
        elif self.current_stage == 3:
            if self.selected_algo == 0: path, visited = AIEngine.solve_hill_climbing(tuple(state.player_pos), state.grid_map, GRID_SIZE)
            elif self.selected_algo == 1: path, visited = AIEngine.solve_simulated_annealing(tuple(state.player_pos), state.grid_map, GRID_SIZE)
            elif self.selected_algo == 2: path, visited = AIEngine.solve_local_beam_search(tuple(state.player_pos), state.grid_map, GRID_SIZE)
            
        elif self.current_stage == 4:
            if self.selected_algo == 0: path, visited = AIEngine.solve_belief_state(tuple(state.player_pos), state.goal_pos, state.grid_map, GRID_SIZE)
            elif self.selected_algo == 1: path, visited = AIEngine.solve_and_or_search(tuple(state.player_pos), state.goal_pos, state.grid_map, GRID_SIZE)
            elif self.selected_algo == 2: path, visited = AIEngine.solve_luyen_thep(tuple(state.player_pos), state.goal_pos, state.grid_map, GRID_SIZE)
            
        elif self.current_stage == 5:
            if self.selected_algo == 0:
                history, nodes, v_nodes = AIEngine.solve_csp_backtracking(GRID_SIZE)
            elif self.selected_algo == 1:
                history, nodes, v_nodes = AIEngine.solve_csp_forward_checking(GRID_SIZE)
            elif self.selected_algo == 2:
                history, nodes, v_nodes = AIEngine.solve_min_conflicts(GRID_SIZE)

            exec_time = (time.perf_counter() - start_time) * 1000

            if not history:
                self.stats["Nodes Duyệt"] = nodes
                self.stats["Chi phí"] = 0
                self.stats["Độ Dài"] = 0
                exec_time = (time.perf_counter() - start_time) * 1000
                self.stats["Thời Gian"] = f"{exec_time:.4f} ms"
                self.stats["Trạng thái"] = "KHÔNG TÌM THẤY CẤU HÌNH!"
                return

            # CSP có thể tạo hàng nghìn trạng thái trung gian. Nếu vẽ từng trạng thái
            # với delay animation, Backtracking/Forward Checking sẽ trông như bị treo.
            # Vì vậy chỉ lấy mẫu một số frame để demo, còn nodes/time vẫn giữ số liệu thật.
            max_csp_frames = 120
            if len(history) > max_csp_frames:
                step = max(1, len(history) // max_csp_frames)
                display_history = history[::step]
                if display_history[-1] != history[-1]:
                    display_history.append(history[-1])
            else:
                display_history = history

            self.calculated_path = display_history
            self.visited_history = []
            self.csp_nodes = nodes
            self.is_animating = True
            self.anim_spread_step = 0
            self.anim_path_step = 0
            self.last_move_time = pygame.time.get_ticks()

            final_board = history[-1]
            count_satellites = sum(row.count(1) for row in final_board)

            self.stats["Nodes Duyệt"] = nodes
            self.stats["Chi phí"] = 0
            self.stats["Độ Dài"] = count_satellites
            self.stats["Thời Gian"] = f"{exec_time:.4f} ms"
            self.stats["Trạng thái"] = "ĐANG ĐẶT VỆ TINH..."

            algo_name = self.algo_names.get(self.current_stage, ["", "", ""])[self.selected_algo]
            self.history_stats[self.current_stage].append({
                "Tên": algo_name.split("(")[0].strip(),
                "Nodes": nodes,
                "Cost": 0,
                "Độ dài": count_satellites,
                "Time": f"{exec_time:.1f}"
            })

            if len(self.history_stats[self.current_stage]) > 3:
                self.history_stats[self.current_stage].pop(0)

            return

        elif self.current_stage == 6:
            sim_p = tuple(state.player_pos)
            sim_g = tuple(state.ghost_pos)

            path = [sim_p]
            ghost_path = [sim_g]
            visited_sim = [sim_p]
            nodes_count = 0
            reached_goal = False

            max_turns = 120

            for _ in range(max_turns):
                if sim_p == state.goal_pos:
                    reached_goal = True
                    break

                if sim_p == sim_g:
                    break

                if self.selected_algo == 0:
                    next_m, n = AIEngine.solve_minimax(
                        sim_p, sim_g, state.grid_map, GRID_SIZE,
                        depth=3, history=visited_sim, goal_pos=state.goal_pos
                    )
                elif self.selected_algo == 1:
                    next_m, n = AIEngine.solve_alpha_beta(
                        sim_p, sim_g, state.grid_map, GRID_SIZE,
                        depth=3, history=visited_sim, goal_pos=state.goal_pos
                    )
                elif self.selected_algo == 2:
                    next_m, n = AIEngine.solve_expectimax(
                        sim_p, sim_g, state.grid_map, GRID_SIZE,
                        depth=3, history=visited_sim, goal_pos=state.goal_pos
                    )

                nodes_count += n

                if not next_m:
                    break

                # Thuật toán hiện trả về dạng [(x, y)]
                next_pos = next_m[0]

                if next_pos is None or next_pos == sim_p:
                    break

                # Chống lặp: nếu quay lại các ô vừa đi gần đây thì chọn nước thay thế
                if next_pos in visited_sim[-8:]:
                    alternatives = AIEngine.get_neighbors(sim_p, state.grid_map, GRID_SIZE)

                    safe_alternatives = []
                    for p in alternatives:
                        ghost_dist = abs(p[0] - sim_g[0]) + abs(p[1] - sim_g[1])
                        if p not in visited_sim[-10:] and ghost_dist > 1:
                            safe_alternatives.append(p)

                    if safe_alternatives:
                        next_pos = min(
                            safe_alternatives,
                            key=lambda p: abs(p[0] - state.goal_pos[0]) + abs(p[1] - state.goal_pos[1])
                        )
                    else:
                        break

                sim_p = next_pos
                path.append(sim_p)
                visited_sim.append(sim_p)

                if sim_p == state.goal_pos:
                    reached_goal = True
                    break

                # Ghost di chuyển 1 bước về phía player
                ghost_neighbors = AIEngine.get_neighbors(sim_g, state.grid_map, GRID_SIZE)
                if ghost_neighbors:
                    sim_g = min(
                        ghost_neighbors,
                        key=lambda p: abs(p[0] - sim_p[0]) + abs(p[1] - sim_p[1])
                    )

                ghost_path.append(sim_g)

                if sim_p == sim_g:
                    break

            self.ghost_path = ghost_path
            visited = nodes_count

            if not reached_goal:
                exec_time = (time.perf_counter() - start_time) * 1000

                self.calculated_path = []
                self.visited_history = []
                self.ghost_path = []
                self.is_animating = False

                self.stats["Nodes Duyệt"] = nodes_count
                self.stats["Chi phí"] = max(0, len(path) - 1)
                self.stats["Độ Dài"] = len(path)
                self.stats["Thời Gian"] = f"{exec_time:.4f} ms"
                self.stats["Trạng thái"] = "KẸT/LẶP - KHÔNG TỚI ĐÍCH"

                algo_name = self.algo_names.get(self.current_stage, ["", "", ""])[self.selected_algo]
                self.history_stats[self.current_stage].append({
                    "Tên": algo_name.split("(")[0].strip(),
                    "Nodes": nodes_count,
                    "Cost": max(0, len(path) - 1),
                    "Độ dài": len(path),
                    "Time": f"{exec_time:.1f}"
                })

                if len(self.history_stats[self.current_stage]) > 3:
                    self.history_stats[self.current_stage].pop(0)

                return
        exec_time = (time.perf_counter() - start_time) * 1000
        if path:
            self.calculated_path = path
            
            if isinstance(visited, list):
                self.visited_history = visited 
                nodes_count = len(visited) if self.current_stage != 5 else self.csp_nodes
            else:
                self.visited_history = []
                nodes_count = visited if self.current_stage != 5 else self.csp_nodes
                
            self.anim_spread_step = 0
            self.anim_path_step = 0
            self.is_animating = True
            self.last_move_time = pygame.time.get_ticks()
            
            path_cost = self.get_path_cost(path, state.grid_map)
            path_len = len(path) if self.current_stage != 5 else GRID_SIZE
            
            self.stats["Nodes Duyệt"] = nodes_count
            self.stats["Chi phí"] = path_cost
            self.stats["Độ Dài"] = path_len
            self.stats["Thời Gian"] = f"{exec_time:.4f} ms"
            self.stats["Trạng thái"] = "ĐANG TÌM ĐƯỜNG..."

            algo_name = self.algo_names.get(self.current_stage, ["", "", ""])[self.selected_algo]
            short_name = algo_name.split("(")[0].strip() 
            
            self.history_stats[self.current_stage].append({
                "Tên": short_name,
                "Nodes": nodes_count,
                "Cost": path_cost,
                "Độ dài": path_len,
                "Time": f"{exec_time:.1f}"
            })

            if len(self.history_stats[self.current_stage]) > 3:
                self.history_stats[self.current_stage].pop(0)
        else:
            self.stats["Trạng thái"] = "KHÔNG CÓ ĐƯỜNG!"

    def run(self):
        while True:
            win_w, win_h = self.screen.get_size()
            scale_x, scale_y = SCREEN_WIDTH / win_w, SCREEN_HEIGHT / win_h
            raw_mx, raw_my = pygame.mouse.get_pos()
            virtual_mouse_pos = (int(raw_mx * scale_x), int(raw_my * scale_y))

            if self.manual_start_time and not self.game_over_reason and not self.is_animating:
                elapsed = time.perf_counter() - self.manual_start_time
                self.stats["Thời Gian"] = f"{elapsed:.2f} s"
                
            for i, btn in enumerate(self.algo_btns):
                btn.text = self.algo_names.get(self.current_stage, ["", "", ""])[i]
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                        
                evt_pos = virtual_mouse_pos
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(event, 'pos'):
                        evt_pos = (int(event.pos[0] * scale_x), int(event.pos[1] * scale_y))
                    
                    if not self.show_rules and self.current_stage == 5:
                        if GRID_OFFSET_X <= evt_pos[0] < GRID_OFFSET_X + GRID_SIZE * TILE_SIZE and \
                           GRID_OFFSET_Y <= evt_pos[1] < GRID_OFFSET_Y + GRID_SIZE * TILE_SIZE:
                            cx = (evt_pos[0] - GRID_OFFSET_X) // TILE_SIZE
                            cy = (evt_pos[1] - GRID_OFFSET_Y) // TILE_SIZE
                            self.stages[self.current_stage].click_cell(cx, cy)
                            
                            if self.stages[self.current_stage].check_conflict():
                                self.game_over_reason = "VỆ TINH ĐỤNG NHAU"
                                self.stats["Trạng thái"] = "THẤT BẠI!"
                            continue 
                        
                if self.show_rules:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        btn_start = self.rules_modal.draw(self.virtual_surface, self.current_stage, SCREEN_WIDTH, SCREEN_HEIGHT)
                        if btn_start.collidepoint(evt_pos): self.show_rules = False
                    continue
                
                if event.type == pygame.KEYDOWN and not self.is_animating and not self.game_over_reason:
                    state = self.stages[self.current_stage]
                    dx, dy = 0, 0
                    if event.key in [pygame.K_LEFT, pygame.K_a]: dx = -1
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]: dx = 1
                    elif event.key in [pygame.K_UP, pygame.K_w]: dy = -1
                    elif event.key in [pygame.K_DOWN, pygame.K_s]: dy = 1
                    
                    if dx != 0 or dy != 0:
                        nx, ny = state.player_pos[0] + dx, state.player_pos[1] + dy
                        
                        is_valid_move = False
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                            if self.current_stage == 4 or state.grid_map[ny][nx] != 1:
                                is_valid_move = True
                                
                        if is_valid_move:
                            if self.manual_start_time is None:
                                self.manual_start_time = time.perf_counter()
                               
                            if tuple(state.player_pos) not in self.manual_visited_path:
                                self.manual_visited_path.append(tuple(state.player_pos))
                                
                            step_cost = 12 if isinstance(state.grid_map[ny][nx], int) and state.grid_map[ny][nx] == 3 else 1
                            self.stats["Chi phí"] += step_cost
                            self.stats["Độ Dài"] += 1
                            self.stats["Nodes Duyệt"] += 1

                            if self.current_stage == 2:
                                state.energy -= 4
                                if state.grid_map[ny][nx] == 4:
                                    state.energy = min(state.max_energy, state.energy + 30)
                                    state.grid_map[ny][nx] = 0
                                if state.energy <= 0:
                                    self.game_over_reason = "HẾT NĂNG LƯỢNG"
                                    self.stats["Trạng thái"] = "THẤT BẠI!"

                            elif self.current_stage == 3:
                                cost = 1 + int(state.grid_map[ny][nx] / 20)
                                state.oxygen -= cost
                                if state.oxygen <= 0:
                                    state.oxygen = 0
                                    self.game_over_reason = "HẾT OXY"
                                    self.stats["Trạng thái"] = "THẤT BẠI!"

                            elif self.current_stage == 4:
                                state.step_count += 1
                                if state.step_count % 3 == 0:
                                    state.shuffle_walls()
                                if state.grid_map[ny][nx] == 1:
                                    self.stats["Chi phí"] += 20
                                    state.grid_map[ny][nx] = 0
                            
                            state.player_pos = [nx, ny]
                            if self.current_stage == 1 or self.current_stage == 3: 
                                state.update_fog()

                            if self.current_stage == 6:
                                gx, gy = state.ghost_pos
                                px, py = state.player_pos[0], state.player_pos[1]
                                
                                # --- 1. KIỂM TRA TẦM NHÌN (LINE OF SIGHT) ---
                                can_see_player = False
                                if gx == px: # Cùng cột, kiểm tra xem có tường chắn giữa không
                                    can_see_player = all(state.grid_map[y][gx] != 1 for y in range(min(gy, py), max(gy, py) + 1))
                                elif gy == py: # Cùng hàng, kiểm tra tường chắn
                                    can_see_player = all(state.grid_map[gy][x] != 1 for x in range(min(gx, px), max(gx, px) + 1))
                                    
                                # --- 2. DI CHUYỂN DỰA TRÊN TRẠNG THÁI ---
                                if can_see_player:
                                    # TRẠNG THÁI ĐUỔI BẮT (Dí sát)
                                    if gx < px and state.grid_map[gy][gx+1] != 1: gx += 1
                                    elif gx > px and state.grid_map[gy][gx-1] != 1: gx -= 1
                                    elif gy < py and state.grid_map[gy+1][gx] != 1: gy += 1
                                    elif gy > py and state.grid_map[gy-1][gx] != 1: gy -= 1
                                else:
                                    # TRẠNG THÁI ĐI TUẦN (Di chuyển ngẫu nhiên tới ô trống)
                                    neighbors = AIEngine.get_neighbors((gx, gy), state.grid_map, GRID_SIZE)
                                    if neighbors:
                                        gx, gy = random.choice(neighbors)
                                        
                                state.ghost_pos = [gx, gy]
                                
                                # Kiểm tra va chạm
                                if tuple(state.ghost_pos) == tuple(state.player_pos):
                                    self.game_over_reason = "BỊ QUÁI VẬT BẮT"
                                    self.stats["Trạng thái"] = "THẤT BẠI!"
                                    self.is_animating = False
                            
                            if tuple(state.player_pos) == getattr(state, 'goal_pos', (GRID_SIZE-1, GRID_SIZE-1)):
                                if not self.game_over_reason: 
                                    self.game_over_reason = "WIN"
                                    self.stats["Trạng thái"] = "CHIẾN THẮNG!"

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.btn_run_ai.collidepoint(evt_pos):
                        self.trigger_ai_solver()
                    elif self.btn_replay.collidepoint(evt_pos):
                        self.stages[self.current_stage].reset(new_map=False)
                        self.reset_ui_state()
                    elif self.btn_new.collidepoint(evt_pos):
                        self.stages[self.current_stage].reset(new_map=True)
                        self.reset_ui_state()
                        
                    for i, btn in self.stage_btns.items():
                        if btn.collidepoint(evt_pos) and self.current_stage != i:
                            self.current_stage = i
                            self.selected_algo = 0
                            self.show_rules = True
                            self.reset_ui_state()
                            
                    for i, btn in enumerate(self.algo_btns):
                        if btn.collidepoint(evt_pos) and btn.text != "N/A":
                            self.selected_algo = i

            # ANIMATION
            if self.is_animating:
                state = self.stages[self.current_stage]
                if self.anim_spread_step < len(self.visited_history):
                    self.anim_spread_step += 1  
                    if self.anim_spread_step > len(self.visited_history):
                        self.anim_spread_step = len(self.visited_history)
                else:
                    self.stats["Trạng thái"] = "ĐANG DI CHUYỂN..."
                    current_time = pygame.time.get_ticks()
                    if self.current_stage == 5 : 
                             anim_delay = 20 
                    elif self.current_stage == 6:
                             anim_delay = 180
                    else:
                             anim_delay = 80
                    if current_time - self.last_move_time > anim_delay: 
                        if self.anim_path_step < len(self.calculated_path):
                            if self.current_stage == 5:
                                state.grid_map = self.calculated_path[self.anim_path_step]
                            else:
                                state.player_pos = list(self.calculated_path[self.anim_path_step])
                                
                            self.anim_path_step += 1
                            self.last_move_time = current_time
                            
                            if self.current_stage == 2:
                                px, py = state.player_pos
                                state.energy -= 4
                                if state.grid_map[py][px] == 4:
                                    state.energy = min(state.max_energy, state.energy + 30)
                                    state.grid_map[py][px] = 0
                                if state.energy <= 0:
                                    state.energy = 0
                                    self.game_over_reason = "HẾT NĂNG LƯỢNG"
                                    self.stats["Trạng thái"] = "THẤT BẠI!"
                                    self.is_animating = False

                            elif self.current_stage == 3:
                                px, py = state.player_pos
                                cost = 1 + int(state.grid_map[py][px] / 20)
                                state.oxygen -= cost
                                state.update_fog()
                                if state.oxygen <= 0:
                                    state.oxygen = 0
                                    self.game_over_reason = "HẾT OXY"
                                    self.stats["Trạng thái"] = "THẤT BẠI!"
                                    self.is_animating = False

                            elif self.current_stage == 4:
                                state.step_count += 1
                                if state.step_count % 3 == 0: state.shuffle_walls()
                                px, py = state.player_pos
                                if state.grid_map[py][px] == 1:
                                    self.stats["Chi phí"] += 20
                                    state.grid_map[py][px] = 0
                                    
                            elif self.current_stage == 6:
                                if self.ghost_path:
                                    ghost_idx = min(self.anim_path_step - 1, len(self.ghost_path) - 1)
                                    state.ghost_pos = list(self.ghost_path[ghost_idx])

                                if tuple(state.ghost_pos) == tuple(state.player_pos):
                                    self.game_over_reason = "BỊ QUÁI VẬT BẮT"
                                    self.stats["Trạng thái"] = "THẤT BẠI!"
                                    self.is_animating = False
                                    
                        else:
                            self.is_animating = False
                            if self.current_stage == 5 or tuple(state.player_pos) == getattr(state, 'goal_pos', (GRID_SIZE-1, GRID_SIZE-1)):
                                if not self.game_over_reason:
                                    self.game_over_reason = "WIN"
                                    self.stats["Trạng thái"] = "HOÀN THÀNH!"

            # --- RENDER ---
            self.ui_renderer.draw_background()
            
            if not self.show_rules:
                state = self.stages[self.current_stage]
                explored = getattr(state, 'explored_map', None)
                self.ui_renderer.draw_grid_map(state.grid_map, explored, getattr(state, 'goal_pos', None), self.current_stage)
                
                if self.manual_visited_path and self.current_stage != 5:
                    self.ui_renderer.draw_manual_path(self.manual_visited_path)
                
                if self.current_stage != 5 and (self.calculated_path or self.visited_history):
                    path_to_draw = self.calculated_path[:self.anim_path_step] if self.is_animating else self.calculated_path
                    self.ui_renderer.draw_ai_exploration(self.visited_history, path_to_draw, self.anim_spread_step)
                
                if self.current_stage != 5:
                    self.ui_renderer.draw_agent(state.player_pos, PLAYER_COLOR)
                if self.current_stage == 6:
                    self.ui_renderer.draw_agent(state.ghost_pos, GHOST_COLOR)
                    
                if self.game_over_reason:
                    self.ui_renderer.draw_game_over(self.game_over_reason)
                
                ctrl = state 
                dash = self  
                    
                special_stats = {}
                if dash.current_stage == 2:
                    special_stats = {"Năng lượng": f"{max(0, ctrl.energy)}/{ctrl.max_energy}"}
                elif dash.current_stage == 3:
                    special_stats = {"Oxy còn lại": f"{max(0, ctrl.oxygen)}/{ctrl.max_oxygen}"}

                stage_names = {
                    1: "Màn 1: Sương Mù", 2: "Màn 2: Sinh Tồn", 3: "Màn 3: Tinh Vân",
                    4: "Màn 4: Ảo Ảnh", 5: "Màn 5: Lưới Laser", 6: "Màn 6: Đối Kháng"
                }

                self.ui_renderer.draw_control_panel(
                    self.stats, 
                    self.history_stats[self.current_stage], 
                    special_stats=special_stats,
                    stage_name=stage_names[self.current_stage]
                )
                
                self.btn_run_ai.draw(self.virtual_surface, is_hover=self.btn_run_ai.collidepoint(virtual_mouse_pos))
                self.btn_replay.draw(self.virtual_surface, is_hover=self.btn_replay.collidepoint(virtual_mouse_pos))
                self.btn_new.draw(self.virtual_surface, is_hover=self.btn_new.collidepoint(virtual_mouse_pos))
                
                for i, btn in self.stage_btns.items():
                    btn.draw(self.virtual_surface, is_active=(self.current_stage == i))
                    
                self.ui_renderer.virtual_surface = self.virtual_surface
                self.virtual_surface.blit(self.ui_renderer.font_text.render("Chọn Thuật Toán:", True, TEXT_COLOR), (750, 190))
                self.virtual_surface.blit(self.ui_renderer.font_text.render("Hành động:", True, TEXT_COLOR), (1090, 190))
                
                for i, btn in enumerate(self.algo_btns):
                    if btn.text != "N/A":
                        btn.draw(self.virtual_surface, is_active=(self.selected_algo == i))
            else:
                self.rules_modal.draw(self.virtual_surface, self.current_stage, SCREEN_WIDTH, SCREEN_HEIGHT)

            scaled_surf = pygame.transform.smoothscale(self.virtual_surface, (win_w, win_h))
            self.screen.blit(scaled_surf, (0, 0))
            pygame.display.flip()
            self.clock.tick(60) 

if __name__ == "__main__":
    app = MainApp()
    app.run()