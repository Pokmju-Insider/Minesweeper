# Nhập các thư viện cần thiết
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import numpy as np
import time

# Khởi tạo trình duyệt edge
driver = webdriver.Edge()
# Mở trang web minesweeper
driver.get("https://minesweeper.online/start/3")
# Chờ cho trang web tải xong
time.sleep(5)
# Tìm nút play và nhấn vào
play_button = driver.find_element_by_xpath("//div[@class='c-group f-align-items-center f-justify-content-center']/button")
play_button.click()
# Chờ cho game bắt đầu
time.sleep(5)
# Tìm bảng game và lấy kích thước của nó
game_board = driver.find_element_by_xpath("//div[@class='gameBoard']")
board_width = int(game_board.get_attribute("data-width"))
board_height = int(game_board.get_attribute("data-height"))
# Tạo một ma trận numpy để lưu trạng thái của các ô
# Giá trị 0: ô chưa mở
# Giá trị -1: ô có mìn
# Giá trị 1-8: ô đã mở và có số mìn xung quanh tương ứng
board_state = np.zeros((board_height, board_width), dtype=int)
# Tạo một hàm để lấy giá trị của một ô từ bảng game
def get_cell_value(row, col):
    # Tìm phần tử div tương ứng với ô (row, col)
    cell = game_board.find_element_by_xpath(f".//div[@data-row='{row}'][@data-col='{col}']")
    # Lấy class của phần tử div
    cell_class = cell.get_attribute("class")
    # Nếu class chứa "blank", tức là ô chưa mở, trả về 0
    if "blank" in cell_class:
        return 0
    # Nếu class chứa "bombflagged", tức là ô có mìn, trả về -1
    elif "bombflagged" in cell_class:
        return -1
    # Nếu class chứa "open", tức là ô đã mở, lấy số mìn xung quanh từ thuộc tính data-mine-count và trả về giá trị tương ứng
    elif "open" in cell_class:
        mine_count = int(cell.get_attribute("data-mine-count"))
        return mine_count
    # Nếu không thuộc các trường hợp trên, trả về None
    else:
        return None

# Tạo một hàm để nhấn vào một ô trên bảng game
def click_cell(row, col):
    # Tìm phần tử div tương ứng với ô (row, col)
    cell = game_board.find_element_by_xpath(f".//div[@data-row='{row}'][@data-col='{col}']")
    # Nhấn vào phần tử div
    cell.click()

# Tạo một hàm để cập nhật ma trận board_state từ bảng game
def update_board_state():
    # Duyệt qua từng ô trong ma trận board_state
    for i in range(board_height):
        for j in range(board_width):
            # Lấy giá trị của ô từ bảng game
            cell_value = get_cell_value(i, j)
            # Nếu giá trị khác None, cập nhật vào ma trận board_state
            if cell_value is not None:
                board_state[i][j] = cell_value

# Tạo một hàm để kiểm tra xem game đã kết thúc hay chưa
def is_game_over():
    # Tìm phần tử div có id là "face"
    face = driver.find_element_by_id("face")
    # Lấy class của phần tử div
    face_class = face.get_attribute("class")
    # Nếu class chứa "facedead" hoặc "facewin", tức là game đã kết thúc, trả về True
    if "facedead" in face_class or "facewin" in face_class:
        return True
    # Nếu không, trả về False
    else:
        return False

# Tạo một hàm để tìm các ô an toàn và các ô có mìn dựa trên ma trận board_state
def find_safe_and_mine_cells():
    # Tạo hai tập hợp để lưu các ô an toàn và các ô có mìn
    safe_cells = set()
    mine_cells = set()
    # Duyệt qua từng ô trong ma trận board_state
    for i in range(board_height):
        for j in range(board_width):
            # Nếu ô có giá trị từ 1 đến 8, tức là ô đã mở và có số mìn xung quanh
            if board_state[i][j] in range(1, 9):
                # Đếm số ô chưa mở xung quanh ô hiện tại
                unknown_count = 0
                # Đếm số ô có mìn xung quanh ô hiện tại
                mine_count = 0
                # Tạo một danh sách để lưu các ô chưa mở xung quanh ô hiện tại
                unknown_cells = []
                # Duyệt qua các ô lân cận của ô hiện tại
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        # Bỏ qua nếu là ô hiện tại hoặc ngoài phạm vi của bảng game
                        if di == 0 and dj == 0:
                            continue
                        if i + di < 0 or i + di >= board_height:
                            continue
                        if j + dj < 0 or j + dj >= board_width:
                            continue
                        # Nếu ô lân cận có giá trị là 0, tức là chưa mở, tăng biến unknown_count và thêm vào danh sách unknown_cells
                        if board_state[i + di][j + dj] == 0:
                            unknown_count += 1
                            unknown_cells.append((i + di, j + dj))
                        # Nếu ô lân cận có giá trị là -1, tức là có mìn, tăng biến mine_count
                        elif board_state[i + di][j + dj] == -1:
                            mine_count += 1
                # Nếu số ô chưa mở bằng số mìn còn lại xung quanh ô hiện tại, tức là tất cả các ô chưa mở đều có mìn, thêm vào tập hợp mine_cells
                if unknown_count == board_state[i][j] - mine_count:
                    for cell in unknown_cells:
                        mine_cells.add(cell)
                # Nếu số mìn còn lại xung quanh ô hiện tại bằng 0, tức là tất cả các ô chưa mở đều an toàn, thêm vào tập hợp safe_cells
                elif board_state[i][j] - mine_count == 0:
                    for cell in unknown_cells:
                        safe_cells.add(cell)
    # Trả về hai tập hợp safe_cells và mine_cells
    return safe_cells, mine_cells

# Tạo một hàm để chơi game
def play_game():
    # Cập nhật ma trận board_state từ bảng game
    update_board_state()
    # Lặp cho đến khi game kết thúc
    while not is_game_over():
        # Tìm các ô an toàn và các ô có mìn từ ma trận board_state
        safe_cells, mine_cells = find_safe_and_mine_cells()
        # Nếu có ô an toàn, nhấn vào một ô an toàn ngẫu nhiên
        if safe_cells:
            safe_cell = safe_cells.pop()
            click_cell(*safe_cell)
        # Nếu không có ô an toàn nhưng có ô có mìn, đánh dấu tất cả các ô có mìn
        elif mine_cells:
            for mine_cell in mine_cells:
                click_cell(*mine_cell)
        # Nếu không có ô an toàn và không có ô có mìn, nhấn vào một ô chưa mở ngẫu nhiên
        else:
            unknown_cells = np.argwhere(board_state == 0)
            random_cell = unknown_cells[np.random.choice(len(unknown_cells))]
            click_cell(*random_cell)
        # Cập nhật ma trận board_state từ bảng game
        update_board_state()
    # In kết quả game
    if is_game_over():
        face = driver.find_element_by_id("face")
        face_class = face.get_attribute("class")
        if "facedead" in face_class:
            print("Bạn đã thua!")
        elif "facewin" in face_class:
            print("Bạn đã thắng!")

# Gọi hàm chơi game
play_game()
