# ui/components.py
import pygame
from core.constants import *

class UIButton:
    def __init__(self, rect, text, font, is_algo=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.is_algo = is_algo # Flag định dạng riêng cho nút thuật toán

    def draw(self, screen, is_active=False, is_hover=False):
        # Làm nền nút thuật toán đậm hơn hẳn để phân biệt khu vực
        base_color = (15, 22, 33) if self.is_algo else BTN_COLOR
        color = BTN_ACTIVE_COLOR if is_active or is_hover else base_color
        
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        
        # Thêm viền nổi bật (stroke) bao quanh cho nút thuật toán
        if self.is_algo:
            border_color = BTN_ACTIVE_COLOR if is_active else GRID_COLOR
            pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=6)
            
        txt_surf = self.font.render(self.text, True, TEXT_COLOR)
        screen.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))

    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)

class UIRulesModal:
    """Cửa sổ Modal bật lên hiển thị luật chơi từng màn"""
    def __init__(self, width, height, font_title, font_body):
        self.w, self.h = width, height
        self.font_title = font_title
        self.font_body = font_body
        self.btn_rect = pygame.Rect(0, 0, 200, 45)

    def draw(self, screen, stage_num, screen_w, screen_h):
        modal_x = (screen_w - self.w) // 2
        modal_y = (screen_h - self.h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, self.w, self.h)
        
        pygame.draw.rect(screen, PANEL_COLOR, modal_rect, border_radius=12)
        pygame.draw.rect(screen, PLAYER_COLOR, modal_rect, 2, border_radius=12)
        
        rules_dict = {
            1: ["STAGE 1: FOG OF WAR (SƯƠNG MÙ BÁN KÍNH 1)", "- Agent bị mất tầm nhìn diện rộng.", "- Sử dụng phím điều hướng hoặc bấm kích hoạt hệ thống AI.", "- Thuật toán áp dụng: BFS / DFS / UCS."],
            2: ["STAGE 2: ENERGY SURVIVAL (SINH TỒN)", "- Chạy đua với năng lượng và Quái vật AI.", "- Nhặt Pin (Vàng) để hồi năng lượng.", "- Thuật toán áp dụng: Greedy BFS / A* / IDA*."],
            3: ["STAGE 3: NEBULA PATHFINDING (DÒ TÌM TINH VÂN)", "- Tìm lõi năng lượng cao nhất (Global Maxima).", "- Tránh Hố đen tàng hình.", "- Thuật toán áp dụng: Hill Climbing / Simulated Annealing / Local Beam."],
            4: ["STAGE 4: BELIEF STATE SEARCH (ẢO ẢNH)", "- Mê cung thay đổi cấu trúc sau mỗi 3 bước.", "- Thuật toán Belief State tính toán xác suất an toàn."],
            5: ["STAGE 5: SATELLITE CSP (RÀNG BUỘC KHÔNG GIAN)", "- Đặt các Vệ tinh phòng thủ sao cho không chiếu lẫn nhau.", "- Click chuột để thủ công thao tác thiết lập vị trí.", "- Thuật toán áp dụng: Backtracking + Forward Checking."],
            6: ["STAGE 6: ADVERSARIAL GAME (TRẬN CHIẾN ĐỐI KHÁNG)", "- Đối đầu trực diện 1vs1 với Quái vật di động.", "- Mỗi lượt Agent đi một ô, Quái vật sẽ tự động săn đuổi.", "- Thuật toán áp dụng: Alpha-Beta Pruning / Minimax."]
        }
        
        lines = rules_dict.get(stage_num, ["STAGE: CHƯA CẬP NHẬT", "- Nội dung đang được cập nhật."])
        
        title_surf = self.font_title.render(lines[0], True, PLAYER_COLOR)
        screen.blit(title_surf, (modal_x + self.w//2 - title_surf.get_width()//2, modal_y + 25))
        
        for idx, text in enumerate(lines[1:]):
            txt_surf = self.font_body.render(text, True, TEXT_COLOR)
            screen.blit(txt_surf, (modal_x + 40, modal_y + 80 + idx * 30))
            
        self.btn_rect.center = (modal_x + self.w//2, modal_y + self.h - 50)
        mouse_pos = pygame.mouse.get_pos()
        btn_hover = self.btn_rect.collidepoint(mouse_pos)
        
        pygame.draw.rect(screen, BTN_ACTIVE_COLOR if btn_hover else BTN_COLOR, self.btn_rect, border_radius=8)
        btn_txt = self.font_title.render("BẮT ĐẦU", True, TEXT_COLOR)
        screen.blit(btn_txt, btn_txt.get_rect(center=self.btn_rect.center))
        
        return self.btn_rect