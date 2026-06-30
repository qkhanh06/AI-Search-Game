# ui/render_engine.py
import pygame
from core.constants import *

class RenderEngine:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.font_text = pygame.font.SysFont("Segoe UI", 16)
        self.font_small = pygame.font.SysFont("Segoe UI", 14)

    def draw_background(self):
        self.screen.fill(BG_COLOR)

    def draw_grid_map(self, grid_map, explored_map=None, goal_pos=None, stage_num=1):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(GRID_OFFSET_X + c*TILE_SIZE, GRID_OFFSET_Y + r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                is_visible = explored_map[r][c] if explored_map else True
                
                # 1. Vẽ nền ô lưới
                if is_visible:
                    # Logic cho Màn 5: Luôn vẽ Vệ tinh (nếu val == 1) đè lên tất cả
                    val = grid_map[r][c]
                    
                    if stage_num == 5 and val == 1:
                        # Vệ tinh (Màu xanh lơ)
                        pygame.draw.rect(self.screen, (0, 255, 255), rect)
                        pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)
                        # Vẽ thêm dấu X hoặc chấm nhỏ để nhận diện vệ tinh
                        pygame.draw.circle(self.screen, (255, 255, 255), rect.center, 5)
                        continue

                    # Logic các màn còn lại
                    if isinstance(val, float): 
                        intensity = min(255, int((val / 100) * 200))
                        pygame.draw.rect(self.screen, (intensity, 0, intensity), rect) 
                    else:
                        if val == 1: pygame.draw.rect(self.screen, WALL_COLOR, rect)
                        elif val == 2: pygame.draw.rect(self.screen, GOAL_COLOR, rect)
                        elif val == 3: pygame.draw.rect(self.screen, SWAMP_COLOR, rect)
                        elif val == 4: pygame.draw.rect(self.screen, ENERGY_COLOR, rect)
                        else: pygame.draw.rect(self.screen, GRID_COLOR, rect, 1) # Ô trống
                else:
                    pygame.draw.rect(self.screen, FOG_COLOR, rect)
                
                # Vẽ viền ô
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

    def draw_ai_exploration(self, visited_history, path, anim_step):
        # Vẽ các node đã duyệt (loang màu)
        for i in range(min(anim_step, len(visited_history))):
            node = visited_history[i]
            # Nếu là Màn 5, node có dạng (col, row)
            nx, ny = node[0], node[1] 
            
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            s.fill((52, 152, 219, 60)) # Màu xanh loang
            self.screen.blit(s, (GRID_OFFSET_X + nx * TILE_SIZE, GRID_OFFSET_Y + ny * TILE_SIZE))
            
            # Highlight node hiện tại đang thử
            if i == min(anim_step, len(visited_history)) - 1:
                rect = pygame.Rect(GRID_OFFSET_X + nx*TILE_SIZE, GRID_OFFSET_Y + ny*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (241, 196, 15), rect, 2)

        if anim_step >= len(visited_history) and path:
            for node in path:
                cx = GRID_OFFSET_X + node[0]*TILE_SIZE + TILE_SIZE//2
                cy = GRID_OFFSET_Y + node[1]*TILE_SIZE + TILE_SIZE//2
                pygame.draw.circle(self.screen, DOT_COLOR, (cx, cy), 6)

    def draw_manual_path(self, path):
        for node in path:
            cx = GRID_OFFSET_X + node[0]*TILE_SIZE + TILE_SIZE//2
            cy = GRID_OFFSET_Y + node[1]*TILE_SIZE + TILE_SIZE//2
            pygame.draw.circle(self.screen, DOT_COLOR, (cx, cy), 6)

    def draw_agent(self, pos, color, radius_ratio=3):
        cx = GRID_OFFSET_X + pos[0]*TILE_SIZE + TILE_SIZE//2
        cy = GRID_OFFSET_Y + pos[1]*TILE_SIZE + TILE_SIZE//2
        pygame.draw.circle(self.screen, color, (cx, cy), TILE_SIZE//radius_ratio)

    def draw_game_over(self, reason):
        overlay = pygame.Surface((GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE), pygame.SRCALPHA)
        if reason == "WIN":
            overlay.fill((0, 184, 148, 200)) 
            msg_text = "STAGE CLEAR! (CHIẾN THẮNG)"
        else:
            overlay.fill((231, 76, 60, 200)) 
            msg_text = f"GAME OVER: {reason}"
            
        self.screen.blit(overlay, (GRID_OFFSET_X, GRID_OFFSET_Y))
        font_over = pygame.font.SysFont("Segoe UI", 28, bold=True)
        text_surf = font_over.render(msg_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(GRID_OFFSET_X + (GRID_SIZE * TILE_SIZE) // 2, GRID_OFFSET_Y + (GRID_SIZE * TILE_SIZE) // 2))
        self.screen.blit(text_surf, text_rect)

    def draw_control_panel(self, stats, history_stats=[], special_stats={}, stage_name=""):
        pygame.draw.rect(self.screen, PANEL_COLOR, pygame.Rect(720, 0, 560, SCREEN_HEIGHT))
        
        title_surf = self.font_title.render(stage_name, True, PLAYER_COLOR)
        self.screen.blit(title_surf, (750, 40))
        
        if special_stats:
            y_spec = 410
            for k, v in special_stats.items():
                if k == "Năng lượng" or k == "Oxy còn lại":
                    self.screen.blit(self.font_small.render(k, True, (170, 185, 200)), (750, y_spec))
                    if '/' in v:
                        val_cur, val_max = map(int, v.split('/'))
                        ratio = val_cur / val_max
                    else:
                        val_cur = int(v)
                        ratio = val_cur / 100
                        
                    pygame.draw.rect(self.screen, (100, 100, 100), (840, y_spec, 300, 15), border_radius=8)
                    if val_cur > 0:
                        color = (46, 204, 113) if ratio > 0.3 else (231, 76, 60)
                        pygame.draw.rect(self.screen, color, (840, y_spec, int(ratio*300), 15), border_radius=8)
                    self.screen.blit(self.font_small.render(v, True, (255, 255, 255)), (1150, y_spec))

        y_pos = 480 
        results = [
            ("Nodes", stats.get("Nodes Duyệt", 0), 750),
            ("Cost", stats.get("Chi phí", 0), 830),
            ("Độ dài", stats.get("Độ Dài", 0), 920),
            ("Time", stats.get("Thời Gian", "0.0s"), 1020),
            ("Trạng thái", stats.get("Trạng thái", "Sẵn sàng"), 1120)
        ]

        for label, val, x_pos in results:
            self.screen.blit(self.font_small.render(label, True, (170, 185, 200)), (x_pos, y_pos))
            self.screen.blit(self.font_text.render(str(val), True, TEXT_COLOR), (x_pos, y_pos + 20))

        self.screen.blit(self.font_title.render("BẢNG LỊCH SỬ SO SÁNH", True, ENERGY_COLOR), (750, 550))
        col_x = [750, 890, 970, 1040, 1120]
        headers = ["Tên", "Nodes", "Cost", "Độ dài", "Time"]
        for i, h in enumerate(headers):
            self.screen.blit(self.font_small.render(h, True, (170, 185, 200)), (col_x[i], 580))
        
        hy = 610
        for row in history_stats:
            if isinstance(row, dict):
                self.screen.blit(self.font_small.render(f"{row.get('Tên', 'N/A'):<8}", True, TEXT_COLOR), (col_x[0], hy))
                self.screen.blit(self.font_small.render(str(row.get("Nodes", 0)), True, TEXT_COLOR), (col_x[1], hy))
                self.screen.blit(self.font_small.render(str(row.get("Cost", 0)), True, TEXT_COLOR), (col_x[2], hy))
                self.screen.blit(self.font_small.render(str(row.get("Độ dài", 0)), True, TEXT_COLOR), (col_x[3], hy))
                self.screen.blit(self.font_small.render(str(row.get("Time", 0)), True, TEXT_COLOR), (col_x[4], hy))
                hy += 25