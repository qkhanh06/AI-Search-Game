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
        # Tăng chiều rộng và chiều cao để không gian thoáng hơn
        self.w, self.h = 750, 550 
        self.font_title = pygame.font.SysFont("Segoe UI", 20, bold=True) # Tăng size title
        self.font_body = pygame.font.SysFont("Segoe UI", 18)             # Tăng size body
        self.font_desc = pygame.font.SysFont("Segoe UI", 17, italic=True) # Tăng size desc
        self.btn_rect = pygame.Rect(0, 0, 200, 45)

    def draw_text_wrapped(self, surface, text, color, rect, font, line_spacing=5):
        """Hàm helper tự động xuống dòng khi text dài quá độ rộng của rect"""
        y = rect.top
        line_height = font.get_linesize() + line_spacing
        
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            # Kiểm tra xem nếu thêm chữ này vào thì có bị lố chiều rộng không
            if font.size(test_line)[0] < rect.width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        for line in lines:
            if line.strip():
                text_surface = font.render(line, True, color)
                surface.blit(text_surface, (rect.left, y))
                y += line_height
                
        return y # Trả về tọa độ Y mới sau khi vẽ xong đoạn text

    def draw(self, screen, stage_num, screen_w, screen_h):
        modal_x = (screen_w - self.w) // 2
        modal_y = (screen_h - self.h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, self.w, self.h)
        
        # Vẽ nền và viền
        pygame.draw.rect(screen, PANEL_COLOR, modal_rect, border_radius=12)
        pygame.draw.rect(screen, PLAYER_COLOR, modal_rect, 2, border_radius=12)
        
        rules_dict = {
            1: {
                "title": "STAGE 1: FOG OF WAR (SƯƠNG MÙ)",
                "desc": "Mô phỏng khả năng tìm đường cơ bản của AI trong môi trường thiếu thông tin. Agent (xanh) phải tìm đường đến Đích (đỏ) qua mê cung.",
                "rules": [
                    "• Môi trường: Sương mù che khuất, Agent chỉ nhìn thấy bán kính 1 ô xung quanh.",
                    "• Chướng ngại: Đầm lầy (xanh rêu) tốn nhiều Chi phí di chuyển hơn tường.",
                    "• Điều khiển: Dùng phím W,A,S,D / Mũi tên để tự đi hoặc kích hoạt AI.",
                    "• Thuật toán: BFS (loang đều), DFS (dò sâu), UCS (né đầm lầy)."
                ]
            },
            2: {
                "title": "STAGE 2: ENERGY SURVIVAL (SINH TỒN)",
                "desc": "Agent phải cân bằng giữa việc đi nhanh tới đích và duy trì năng lượng sống sót.",
                "rules": [
                    "• Năng lượng: Bắt đầu với 100%. Mỗi bước đi tiêu hao 4%.",
                    "• Sinh tồn: Nhặt Pin (Vàng) trên đường để hồi 30% năng lượng.",
                    "• Game Over: Hết năng lượng trước khi tới đích sẽ thất bại.",
                    "• Thuật toán: Greedy BFS (chọn bừa nhanh), A* (tối ưu nhất), IDA* (tiết kiệm RAM)."
                ]
            },
            # ... (Bên trong class UIRulesModal)
            3: {
                "title": "STAGE 3: NEBULA PATHFINDING (TÌM KIẾM ĐỈNH)",
                "desc": "Mô phỏng bài toán tối ưu hóa. Bản đồ là một bề mặt không đồng đều với các giá trị khác nhau. Mục tiêu là tìm đỉnh cao nhất.",
                "rules": [
                    "• Mục tiêu: Leo lên đỉnh (Global Maxima - Đích) trước khi hết Oxy.",
                    "• Nguy hiểm: Tránh bước nhầm vào Hố đen (sẽ bị hút mất nhiều Oxy).",
                    "• Thuật toán: Hill Climbing, Stochastic Hill Climbing (leo dốc ngẫu nhiên), Local Beam Search." # <-- Sửa ở đây
                ]
            },
            4: {
                "title": "STAGE 4: BELIEF STATE SEARCH (ẢO ẢNH)",
                "desc": "Môi trường không xác định, các bức tường sẽ liên tục thay đổi vị trí. Agent phải tự tin vào 'niềm tin' của mình.",
                "rules": [
                    "• Biến động: Cứ sau 3 bước di chuyển, toàn bộ mê cung sẽ xáo trộn.",
                    "• Tầm nhìn: Có hệ thống Radar quét xung quanh, nhưng thông tin sẽ nhanh chóng lỗi thời.",
                    "• Thuật toán: Belief State Search (tính rủi ro), AND-OR (dự phòng), Simulated Annealing (tôi luyện thép)." # <-- Sửa ở đây
                ]
            },
            5: {
                "title": "STAGE 5: SATELLITE CSP (RÀNG BUỘC KHÔNG GIAN)",
                "desc": "Đây không phải game di chuyển! Đây là bài toán Thỏa mãn Ràng buộc (Constraint Satisfaction Problem).",
                "rules": [
                    "• Nhiệm vụ: Đặt các Vệ tinh (xanh lơ) lên lưới sao cho chúng không nằm cùng Hàng, Cột, hoặc Đường chéo.",
                    "• Tương tác: Click chuột vào ô lưới để đặt vệ tinh thủ công và kiểm tra xung đột.",
                    "• Thuật toán: Backtracking (thử bừa), Forward Checking (cắt tỉa thông minh), Min-Conflicts."
                ]
            },
            6: {
                "title": "STAGE 6: ADVERSARIAL GAME (ĐỐI KHÁNG)",
                "desc": "Cuộc rượt đuổi nghẹt thở! Agent (xanh) phải chạy đua về đích trong khi bị Quái vật (tím) săn lùng.",
                "rules": [
                    "• Lối chơi: Turn-based. Agent đi 1 bước, Quái vật sẽ đi theo 1 bước.",
                    "• Quái vật: Có Tầm nhìn (Line of Sight). Gặp trực diện sẽ dí theo, khuất tầm nhìn sẽ đi tuần tra.",
                    "• Game Over: Chạm mặt quái vật sẽ Thất bại.",
                    "• Thuật toán: Minimax, Alpha-Beta Pruning, Expectimax (tính xác suất)."
                ]
            }
        }
        
        stage_data = rules_dict.get(stage_num, rules_dict[1])
        
        # 1. Vẽ Tiêu đề màn (Căn giữa)
        title_surf = self.font_title.render(stage_data["title"], True, PLAYER_COLOR)
        screen.blit(title_surf, (modal_x + self.w//2 - title_surf.get_width()//2, modal_y + 25))
        
        # 2. Vẽ Đoạn Mô tả chung (Auto wrap text)
        desc_rect = pygame.Rect(modal_x + 40, modal_y + 70, self.w - 80, 100)
        current_y = self.draw_text_wrapped(screen, stage_data["desc"], (200, 200, 200), desc_rect, self.font_desc)
        
        # Vẽ đường kẻ ngang cách điệu
        line_y = current_y + 15
        pygame.draw.line(screen, GRID_COLOR, (modal_x + 30, line_y), (modal_x + self.w - 30, line_y), 1)
        
        # 3. Vẽ Hướng dẫn chi tiết (Auto wrap text)
        current_y = line_y + 20
        for rule in stage_data["rules"]:
            rule_rect = pygame.Rect(modal_x + 40, current_y, self.w - 80, 100)
            current_y = self.draw_text_wrapped(screen, rule, TEXT_COLOR, rule_rect, self.font_body)
            current_y += 10 # Khoảng cách giữa các gạch đầu dòng
            
        # 4. Vẽ Nút BẮT ĐẦU
        self.btn_rect.center = (modal_x + self.w//2, modal_y + self.h - 40)
        mouse_pos = pygame.mouse.get_pos()
        btn_hover = self.btn_rect.collidepoint(mouse_pos)
        
        pygame.draw.rect(screen, BTN_ACTIVE_COLOR if btn_hover else BTN_COLOR, self.btn_rect, border_radius=8)
        btn_txt = self.font_title.render("BẮT ĐẦU", True, TEXT_COLOR)
        screen.blit(btn_txt, btn_txt.get_rect(center=self.btn_rect.center))
        
        return self.btn_rect