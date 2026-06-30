# core/constants.py

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
GRID_SIZE, TILE_SIZE = 15, 42

# ĐÃ SỬA LỖI UI: Căn lề Trái bằng đúng lề Trên/Dưới (45px) để bao quanh ma trận đều tăm tắp
GRID_OFFSET_X, GRID_OFFSET_Y = 45, 45

# Hệ thống màu sắc hằng số toàn cục (UI Dark Mode)
BG_COLOR = (13, 20, 32)
PANEL_COLOR = (22, 33, 50)
GRID_COLOR = (38, 53, 75)
TEXT_COLOR = (240, 244, 248)
BTN_COLOR = (44, 62, 80)
BTN_ACTIVE_COLOR = (0, 184, 148)

# Định dạng các ô thực thể trên Grid Map
WALL_COLOR = (74, 85, 104)
SWAMP_COLOR = (46, 64, 47)
PLAYER_COLOR = (0, 255, 163)
GOAL_COLOR = (255, 75, 75)
DOT_COLOR = (255, 50, 50)
FOG_COLOR = (5, 8, 15)

# Màu sắc đặc trưng các màn cơ chế nâng cao
ENERGY_COLOR = (241, 196, 15)
VIRUS_COLOR = (231, 76, 60)
RADAR_COLOR = (46, 204, 113)
ILLUSION_WALL_COLOR = (127, 140, 141)
GHOST_COLOR = (155, 89, 182)