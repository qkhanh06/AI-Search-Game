# core/env_states.py
import random
import math
from core.constants import GRID_SIZE

class BaseStageState:
    def __init__(self, base_map):
        self.base_map = base_map
        self.grid_map = []
        self.player_pos = [0, 0]
        self.goal_pos = (14, 14)
        
    def reset(self, new_map=True):
        self.player_pos = [0, 0]
        self.grid_map = [row[:] for row in self.base_map]
        
        # Xóa đích cũ (số 2) trên bản đồ nếu có
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid_map[r][c] == 2:
                    self.grid_map[r][c] = 0
                    
        # Thiết lập đích ngẫu nhiên trong 1/4 góc dưới bên phải
        if new_map:
            while True:
                # GRID_SIZE là 15. 1/4 góc dưới phải là tọa độ từ 8 đến 14
                rx = random.randint(GRID_SIZE // 2, GRID_SIZE - 1)
                ry = random.randint(GRID_SIZE // 2, GRID_SIZE - 1)
                
                # Kiểm tra nếu ô đó không phải là tường (1)
                if self.grid_map[ry][rx] == 0:
                    self.goal_pos = (rx, ry)
                    break
        
        # Đặt đích mới vào bản đồ
        self.grid_map[self.goal_pos[1]][self.goal_pos[0]] = 2

class Stage1State(BaseStageState):
    def __init__(self):
        base = [
            [0,0,0,0,0, 0,0,0,1,0, 0,0,0,0,0],
            [1,1,0,1,1, 1,0,0,1,0, 1,1,1,1,0],
            [0,0,0,0,0, 1,0,1,1,0, 0,0,0,1,0],
            [0,1,1,1,0, 0,0,0,0,0, 1,1,0,0,0],
            [0,3,3,3,3, 0,1,1,1,1, 1,0,0,1,1],
            [0,1,1,1,1, 0,0,0,0,3, 1,0,0,0,0],
            [0,0,0,0,1, 1,1,1,0,3, 1,1,1,1,0],
            [1,1,1,0,0, 0,0,1,0,0, 0,0,0,1,0],
            [0,0,1,0,1, 1,0,1,1,1, 1,1,0,1,0],
            [0,1,1,0,0, 0,0,0,0,0, 0,0,0,0,0],
            [0,0,0,0,1, 1,1,1,1,1, 1,0,1,1,0],
            [1,1,1,0,1, 0,0,0,0,0, 1,0,1,0,0],
            [0,0,0,0,1, 0,1,1,1,0, 1,0,1,0,1],
            [0,1,1,1,1, 0,1,0,0,0, 0,0,0,0,0],
            [0,0,0,0,0, 0,1,0,1,1, 1,0,1,1,2]
        ]
        super().__init__(base)
        self.explored_map = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.reset()

    def reset(self, new_map=True):
        super().reset(new_map)
        self.explored_map = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.update_fog()

    def update_fog(self):
        px, py = self.player_pos
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = px + dx, py + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    self.explored_map[ny][nx] = True

class Stage2State(BaseStageState):
    def __init__(self):
        base = [
            [0,0,0,1,0, 0,0,0,0,0, 1,0,0,0,0],
            [0,1,0,1,0, 1,1,1,1,0, 1,0,1,1,0],
            [0,1,0,0,0, 0,0,4,1,0, 0,0,0,1,0],
            [0,1,1,1,1, 1,1,0,1,1, 1,1,0,0,0],
            [0,0,0,0,4, 1,0,0,0,0, 0,1,1,1,0],
            [1,1,0,1,0, 1,0,1,1,1, 0,0,0,0,0],
            [0,0,0,1,0, 0,0,1,4,1, 1,1,1,1,0],
            [0,1,0,1,1, 1,0,0,0,1, 0,0,0,0,0],
            [0,1,0,0,0, 0,0,1,0,0, 0,1,1,1,1],
            [0,1,1,1,0, 1,1,1,0,1, 0,0,4,0,0], 
            [0,0,0,0,0, 0,0,4,0,1, 0,1,0,1,0],
            [1,1,1,0,1, 1,1,1,0,1, 0,1,0,0,0],
            [0,0,0,0,0, 0,0,1,0,0, 0,0,0,1,0],
            [0,1,1,1,1, 1,0,1,0,1, 1,1,0,1,0],
            [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,2]
        ]
        super().__init__(base)
        self.virus_pos = [14, 0]
        self.energy = 100
        self.max_energy = 100
        self.reset()

    def reset(self, new_map=True):
        super().reset(new_map)
        self.virus_pos = [14, 0]
        self.energy = 100

        # Tạo vùng chi phí cao để phân biệt Greedy BFS và A*/IDA*
        # Greedy thường đi gần đích theo heuristic nên dễ lao qua vùng này.
        # A* và IDA* sau khi sửa cost sẽ có xu hướng né để giảm tổng chi phí.
        danger_cells = [
            (8, 8), (9, 8), (10, 8),
            (8, 9), (10, 9),
            (8, 10), (9, 10), (10, 10),
            (11, 10), (12, 10),
            (12, 11), (12, 12)
        ]

        for x, y in danger_cells:
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                if self.grid_map[y][x] == 0:
                    self.grid_map[y][x] = 3 #ô 3 đã được chương trình tính là ô chi phí cao trong get_path_cost(), nên khi A* xét đúng cost thì nó sẽ có lý do để né vùng này. Trong main.py, hàm tính cost hiện đã cộng cost cao hơn cho ô có giá trị 3.

class Stage3State(BaseStageState):
    def __init__(self):
        super().__init__([[0.0]*GRID_SIZE for _ in range(GRID_SIZE)])
        self.black_holes = []
        self.max_oxygen = 100
        self.oxygen = self.max_oxygen
        self.global_max_val = 0
        self.explored_map = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.reset()

    def reset(self, new_map=True):
        self.player_pos = [0, 0]
        self.oxygen = self.max_oxygen
        self.explored_map = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
        
        if new_map:
            self.grid_map = [[0.0]*GRID_SIZE for _ in range(GRID_SIZE)]
            self.black_holes = []
            
            # Khởi tạo 1 đỉnh duy nhất cực lớn để AI chắc chắn leo tới đích
            px, py = random.randint(5, GRID_SIZE-1), random.randint(5, GRID_SIZE-1)
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    dist = math.sqrt((r-py)**2 + (c-px)**2)
                    self.grid_map[r][c] = 100 * math.exp(-dist/4.0)
            
            self.global_max_val = max([max(row) for row in self.grid_map])
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.grid_map[r][c] == self.global_max_val:
                        self.goal_pos = (c, r)
                    if self.grid_map[r][c] < 30 and len(self.black_holes) < 6:
                        if random.random() < 0.05 and (c, r) != (0, 0):
                            self.black_holes.append((c, r))
        self.update_fog()

    def update_fog(self):
        px, py = self.player_pos
        self.explored_map = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = px + dx, py + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    self.explored_map[ny][nx] = True

class Stage4State(BaseStageState):
    def __init__(self):
        base = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if r < 2 and c < 2: continue
                if r > 12 and c > 12: continue
                if random.random() < 0.25:
                    base[r][c] = 1
        base[14][14] = 2 # Set cố định đích cho BaseState
        super().__init__(base)
        self.step_count = 0
        self.radar_mapped = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.reset()

    def reset(self, new_map=True):
        super().reset(new_map)
        self.step_count = 0
        self.radar_mapped = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.trigger_radar()

    def trigger_radar(self):
        px, py = self.player_pos
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                nx, ny = px + dx, py + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    self.radar_mapped[ny][nx] = True

    def shuffle_walls(self):
        wall_count = sum(row.count(1) for row in self.grid_map)
        
        # Lấy toạ độ đích thực sự hiện tại thay vì gắn cứng (14, 14)
        gx, gy = self.goal_pos 
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE): 
                if (c, r) != (gx, gy): 
                    self.grid_map[r][c] = 0
                else: 
                    self.grid_map[r][c] = 2 
        
        placed = 0
        px, py = self.player_pos
        while placed < wall_count:
            r, c = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            
            # Không đặt tường đè lên khu vực của người chơi
            if abs(c - px) <= 1 and abs(r - py) <= 1: continue
            # Không đặt tường đè lên đích
            if (c, r) == (gx, gy): continue
            
            if self.grid_map[r][c] == 0:
                self.grid_map[r][c] = 1
                placed += 1
                
        self.radar_mapped = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.trigger_radar()

class Stage5State(BaseStageState):
    def __init__(self):
        super().__init__([[0]*GRID_SIZE for _ in range(GRID_SIZE)])
        self.reset()

    def reset(self, new_map=True):
        self.player_pos = [0, 0]
        self.grid_map = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]

    def click_cell(self, x, y):
        if self.grid_map[y][x] == 1:
            self.grid_map[y][x] = 0
        else:
            self.grid_map[y][x] = 1
            
    def check_conflict(self):
        sats = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid_map[r][c] == 1:
                    sats.append((r, c))
        for i in range(len(sats)):
            for j in range(i+1, len(sats)):
                r1, c1 = sats[i]
                r2, c2 = sats[j]
                if r1 == r2 or c1 == c2 or abs(r1-r2) == abs(c1-c2):
                    return True 
        return False

class Stage6State(BaseStageState):
    def __init__(self):
        base = [
            [0,1,0,0,0, 0,0,0,0,0, 0,0,0,1,0],
            [0,1,0,1,1, 1,1,1,1,1, 1,1,0,1,0],
            [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
            [0,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1],
            [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
            [0,1,1,1,1, 1,1,1,1,1, 1,1,1,1,0],
            [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
            [0,1,1,1,1, 1,1,1,1,1, 1,1,1,1,0],
            [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
            [0,1,1,1,1, 1,1,1,1,1, 1,1,1,1,0],
            [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
            [1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,0],
            [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
            [0,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1],
            [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,2]
        ]
        super().__init__(base)
        self.ghost_pos = [14, 0]
        self.reset()

    def reset(self, new_map=True):
        super().reset(new_map)
        self.ghost_pos = [14, 0]