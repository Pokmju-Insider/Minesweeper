# Import các thư viện cần thiết
import random
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Khởi tạo trình duyệt Microsoft edge và điều hướng đến website minesweeper
driver = webdriver.Edge()
driver.get("https://minesweeper.online/start/3")

# Tìm phần tử HTML chứa bảng minesweeper và lấy kích thước của nó
board = driver.find_element(By.ID, "game")
rows = int(board.get_attribute("data-rows"))
cols = int(board.get_attribute("data-cols"))

# Khởi tạo một ma trận để lưu trạng thái của các ô trong bảng minesweeper
# 0: ô chưa được mở, 1: ô đã được mở, -1: ô có cờ đánh dấu là bom
state = [[0 for j in range(cols)] for i in range(rows)]

# Hàm để lấy số bom xung quanh một ô đã được mở
def get_bombs(i,j):
  cell = board.find_element_by_xpath(f"//div[@id='game']/div[{i+1}]/div[{j+1}]")
  if cell.get_attribute("class") == "open0":
    return 0
  else:
    return int(cell.text)

# Hàm để kiểm tra xem một ô có phải là bom hay không
def is_bomb(i,j):
  cell = board.find_element_by_xpath(f"//div[@id='game']/div[{i+1}]/div[{j+1}]")
  return cell.get_attribute("class") == "bombflagged"

# Hàm để kiểm tra xem một ô có phải là biên của bảng hay không
def is_edge(i,j):
  return i == 0 or i == rows-1 or j == 0 or j == cols-1

# Hàm để kiểm tra xem game đã kết thúc hay chưa
def is_game_over():
  face = driver.find_element_by_id("face")
  return face.get_attribute("class") != "facesmile"

# Hàm để click vào một ô trong bảng minesweeper với chuột trái hoặc chuột phải
def click_cell(i,j,right=False):
  cell = board.find_element_by_xpath(f"//div[@id='game']/div[{i+1}]/div[{j+1}]")
  if right:
    # Click chuột phải để đánh dấu cờ cho ô có bom
    cell.click()
    state[i][j] = -1 # Cập nhật trạng thái của ô là -1 (có cờ)
    print(f"Marked bomb at ({i},{j})")
  else:
    # Click chuột trái để mở ô không có bom 
    cell.click()
    state[i][j] = 1 # Cập nhật trạng thái của ô là 1 (đã mở)
    print(f"Opened cell at ({i},{j})")

# Hàm để áp dụng các luật logic để giải quyết bài toán minesweeper 
def solve():
  
  # Biến để lưu số lượng các nước đi hợp lý được tìm ra trong mỗi vòng lặp 
  moves = 0

  # Duyệt qua từng ô trong bảng minesweeper 
  for i in range(rows):
    for j in range(cols):

      # Nếu ô đã được mở và có số bom xung quanh khác 0
      if state[i][j] == 1 and get_bombs(i,j) > 0:

        # Đếm số lượng các ô chưa được mở xung quanh ô đó
        unknown = 0
        for di in [-1,0,1]:
          for dj in [-1,0,1]:
            if di == 0 and dj == 0:
              continue
            ni = i + di
            nj = j + dj
            if ni >= 0 and ni < rows and nj >= 0 and nj < cols and state[ni][nj] == 0:
              unknown += 1
        
        # Nếu số lượng các ô chưa được mở bằng số bom xung quanh ô đó
        if unknown == get_bombs(i,j):

          # Đánh dấu cờ cho tất cả các ô chưa được mở xung quanh ô đó 
          for di in [-1,0,1]:
            for dj in [-1,0,1]:
              if di == 0 and dj == 0:
                continue
              ni = i + di
              nj = j + dj
              if ni >= 0 and ni < rows and nj >= 0 and nj < cols and state[ni][nj] == 0:
                click_cell(ni,nj,right=True)
                moves += 1

      # Nếu ô đã được mở và có số bom xung quanh khác 0 
      elif state[i][j] == -1:

        # Đếm số lượng các ô có cờ xung quanh ô đó 
        flags = 0
        for di in [-1,0,1]:
          for dj in [-1,0,1]:
            if di == 0 and dj == 0:
              continue
            ni = i + di
            nj = j + dj
            if ni >= 0 and ni < rows and nj >= 0 and nj < cols and is_bomb(ni,nj):
              flags += 1
        
        # Nếu số lượng các ô có cờ bằng số bom xung quanh ô đó 
        if flags == get_bombs(i,j):

          # Mở tất cả các ô không có cờ xung quanh ô đó 
          for di in [-1,0,1]:
            for dj in [-1,0,1]:
              if di == 0 and dj == 0:
                continue
              ni = i + di
              nj = j + dj
              if ni >= 0 and ni < rows and nj >= 0 and nj < cols and state[ni][nj] != -1:
                click_cell(ni,nj)
                moves += 1

  # Trả về số lượng các nước đi hợp lý được tìm ra trong mỗi vòng lặp 
  return moves

# Hàm để chọn một ô ngẫu nhiên để bắt đầu game hoặc khi không có nước đi hợp lý nào 
def random_move():
  i = random.randint(0,rows-1)
  j = random.randint(0,cols-1)
  while state[i][j] != 0:
    i = random.randint(0,rows-1)
    j = random.randint(0,cols-1)
  click_cell(i,j)

# Bắt đầu game bằng cách click vào một ô ngẫu nhiên 
random_move()

# Lặp lại cho đến khi game kết thúc 
while not is_game_over():
  
  # Áp dụng các luật logic để giải quyết bài toán minesweeper 
  moves = solve()

  # Nếu không có nước đi hợp lý nào được tìm ra 
  if moves == 0:

    # Chọn một ô ngẫu nhiên để tiếp tục game 
    random_move()
  
  # Đợi một giây trước khi thực hiện nước đi tiếp theo 
  time.sleep(1)

# In kết quả của game 
if is_game_over():
  face = driver.find_element_by_id("face")
  if face.get_attribute("class") == "facedead":
    print("Game over. You lose.")
  elif face.get_attribute("class") == "facewin":
    print("Game over. You win.")
