# Framework mô phỏng thuật toán tìm đường và ra quyết định AI

Đồ án cuối kỳ môn Trí tuệ nhân tạo. Chương trình mô phỏng nhiều nhóm thuật toán AI trong môi trường lưới bằng Python và Pygame.

## Cấu trúc project

```text
AI/
├── main.py
├── README.md
├── requirements.txt
├── core/
│   ├── ai_solvers.py
│   ├── constants.py
│   └── env_states.py
├── ui/
│   ├── components.py
│   └── render_engine.py
└── tests/
    └── test_algorithms.py
```

## Nhóm thuật toán

- Tìm kiếm mù: BFS, DFS, UCS
- Tìm kiếm có thông tin: Greedy BFS, A*, IDA*
- Tìm kiếm cục bộ: Hill Climbing, Simulated Annealing, Local Beam Search
- Môi trường không chắc chắn: Belief State Search, AND-OR Search, Luyện thép
- Bài toán thỏa mãn ràng buộc: Backtracking, Forward Checking, Min-Conflicts
- Tìm kiếm đối kháng: Minimax, Alpha-Beta Pruning, Expectimax

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy chương trình

```bash
python main.py
```
