from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import threading
from time import *
from socket import *
import winsound

# Глобальные переменные
team_pieces = [[], []]  # Фигуры, доступные для размещения (команда 1 и команда 2)
current_team = 0  # 0 - команда 1, 1 - команда 2

# Параметры первой доски
left_desk1 = 50
bottom_desk1 = 450
cell_size = 50
desk_size = 8 * cell_size
flg_vid1 = 0  # 0 - белые внизу, 1 - черные внизу

# Параметры второй доски
left_desk2 = 1000
bottom_desk2 = 450
flg_vid2 = 1  # Вид второй доски (0 - белые внизу, 1 - черные внизу)

# Цвета и оформление
rect_colors = ["#8D89AF", "#EFEF8E"]
root_color = "thistle"
sel_color = "red"
box_color = "pink"
col_names = "ABCDEFGH"
row_names = "12345678"

# Списки фигур для обеих досок
whitefig_tags = ["wll", "whl", "wsb", "wfr", "wkr", "wsw", "whr", "wlr"]
blackfig_tags = ["bll", "bhl", "bsw", "bfr", "bkr", "bsb", "bhr", "blr"]

# Фигуры для первой доски
white_figs1 = []
black_figs1 = []
white_deleted1 = []
black_deleted1 = []

# Фигуры для второй доски
white_figs2 = []
black_figs2 = []
white_deleted2 = []
black_deleted2 = []

# Общие настройки
btn_width = 14
photo_images = []
sound_mode = "off"

# Выбранные фигуры для обеих досок
sel_adr1 = ""
sel_fignum1 = -1
sel_figlist1 = []

sel_adr2 = ""
sel_fignum2 = -1
sel_figlist2 = []

# Сетевые настройки
server_address = ('', 5400)
ip_partn = ""
net_mode = "local"
main_tau = 20
lst_in = []
busy_in = 0


# Функции для работы с координатами и адресами
def adr2rowcol1(adr):
    if len(adr) == 2:
        col = col_names.find(adr[0])
        row = row_names.find(adr[1])
        if flg_vid1 == 1:
            col = 7 - col
            row = 7 - row
    else:
        row = col_names.find(adr[1])
        col = int(adr[2]) + 8
        if col > 12:
            col -= 4
        col += 5
    return row, col


def adr2rowcol2(adr):
    if len(adr) == 2:
        col = col_names.find(adr[0])
        row = row_names.find(adr[1])
        if flg_vid2 == 1:
            col = 7 - col
            row = 7 - row
    else:
        row = col_names.find(adr[1])
        col = int(adr[2]) + 9
        if col > 12:
            col -= 4
        col = col - 20
    return row, col


def rowcol2adr1(row, col):
    if row < 0 or row > 7:
        return ""

    if 0 <= col < 8:
        if flg_vid1 == 1:
            col = 7 - col
            row = 7 - row
        adr = col_names[col] + row_names[row]
    elif 10 <= col < 12:
        adr = "d" + col_names[row] + str(col - 9)
    elif 12 <= col < 14:
        adr = "d" + col_names[row] + str(col - 5)
    else:
        adr = ""
    return adr


def rowcol2adr2(row, col):
    if row < 0 or row > 7:
        return ""

    if 0 <= col < 8:
        if flg_vid2 == 1:
            col = 7 - col
            row = 7 - row
        adr = col_names[col] + row_names[row]
    elif 10 <= col < 12:
        adr = "d" + col_names[row] + str(col - 9)
    elif 12 <= col < 14:
        adr = "d" + col_names[row] + str(col - 5)
    else:
        adr = ""
    return adr


def event2adr(event):
    # Определяем, на какую доску кликнули
    if left_desk1 <= event.x <= left_desk1 + desk_size:
        # Первая доска
        row = (bottom_desk1 - event.y) // cell_size
        col = (event.x - left_desk1) // cell_size
        return rowcol2adr1(row, col), 1
    elif left_desk2 <= event.x <= left_desk2 + desk_size:
        # Вторая доска
        row = (bottom_desk2 - event.y) // cell_size
        col = (event.x - left_desk2) // cell_size
        return rowcol2adr2(row, col), 2
    return "", 0


def adr2imagecoord1(adr):
    row, col = adr2rowcol1(adr)
    image_x = left_desk1 + (col + 0.5) * cell_size
    image_y = bottom_desk1 - (row + 0.5) * cell_size
    return image_x, image_y


def adr2imagecoord2(adr):
    row, col = adr2rowcol2(adr)
    image_x = left_desk2 + (col + 0.5) * cell_size
    image_y = bottom_desk2 - (row + 0.5) * cell_size
    return image_x, image_y


# Функции для работы с фигурами
def set_rectcolor(adr, color, desk_num):
    if adr == "": return
    if desk_num == 1:
        row, col = adr2rowcol1(adr)
    else:
        row, col = adr2rowcol2(adr)

    if len(adr) == 2:
        tag = f"r{desk_num}_{row}{col}"
    else:
        tag = f"dr{desk_num}_{row}{col}"
    canv.itemconfig(tag, fill=color)


def set_rectbright(adr, desk_num):
    set_rectcolor(adr, sel_color, desk_num)


def set_rectfon(adr, desk_num):
    if len(adr) == 3:
        color = box_color
    elif len(adr) == 2:
        if desk_num == 1:
            row, col = adr2rowcol1(adr)
        else:
            row, col = adr2rowcol2(adr)
        color = rect_colors[(row + col) % 2]
    set_rectcolor(adr, color, desk_num)


def init_adr(fig_name):
    if fig_name in whitefig_tags:
        fig_index = whitefig_tags.index(fig_name)
        adr = col_names[fig_index] + "1"
    elif fig_name[:2] == "wp":
        fig_index = int(fig_name[2])
        adr = col_names[fig_index] + "2"
    elif fig_name in blackfig_tags:
        fig_index = blackfig_tags.index(fig_name)
        adr = col_names[fig_index] + "8"
    elif fig_name[:2] == "bp":
        fig_index = int(fig_name[2])
        adr = col_names[fig_index] + "7"
    else:
        adr = ""
    return adr


def move_fig(fig, adr, desk_num):
    global team_pieces, current_team

    fig_name, fig_img, fig_adr = fig
    old_adr = fig_adr

    # Проверяем, было ли взятие фигуры
    target_num, target_list = get_fignumlist(adr, desk_num)
    if target_num >= 0 and target_list[target_num][0][0] != fig_name[0]:
        captured_fig = target_list[target_num]

        # Добавляем взятую фигуру в пул команды
        team_pieces[current_team].append(captured_fig[0][:2])  # Сохраняем только тип фигуры (без номера)

        # Удаляем взятую фигуру с доски
        target_list.remove(captured_fig)
        canv.delete(captured_fig[1])

    # Перемещаем фигуру
    set_figpos(fig, adr, desk_num)

    # Отправляем информацию о ходе по сети
    if net_mode == "connect":
        send_mess(f"move|{fig_name}|{old_adr}|{adr}|{desk_num}")


def place_captured_piece(fig_type, adr, desk_num):
    global team_pieces, current_team

    # Проверяем, есть ли такая фигура в пуле команды
    if fig_type not in team_pieces[current_team]:
        return False

    # Проверяем, что клетка пустая
    fig_num, _ = get_fignumlist(adr, desk_num)
    if fig_num >= 0:
        return False

    # Для пешек проверяем, что не ставим на первую/последнюю горизонталь
    if fig_type[1] == 'p':
        row, _ = adr2rowcol1(adr) if desk_num == 1 else adr2rowcol2(adr)
        if row == 0 or row == 7:
            return False

    # Удаляем фигуру из пула
    team_pieces[current_team].remove(fig_type)

    # Размещаем фигуру на доске
    fig = load_fig(fig_type, adr, desk_num)
    if desk_num == 1:
        if fig_type[0] == 'w':
            white_figs1.append(fig)
        else:
            black_figs1.append(fig)
    else:
        if fig_type[0] == 'w':
            white_figs2.append(fig)
        else:
            black_figs2.append(fig)

    return True


def get_fignumlist(adr, desk_num):
    if desk_num == 1:
        fig_lists = [white_figs1, black_figs1] if len(adr) == 2 else [white_deleted1, black_deleted1]
    else:
        fig_lists = [white_figs2, black_figs2] if len(adr) == 2 else [white_deleted2, black_deleted2]

    for fig_list in fig_lists:
        for num in range(len(fig_list)):
            fig = fig_list[num]
            if fig[2] == adr:
                return num, fig_list
    return (-1, [])


def select_fig(event):
    adr, desk_num = event2adr(event)
    if adr == "":
        return ("", -1, [], 0)

    fig_num, fig_list = get_fignumlist(adr, desk_num)
    return (adr, fig_num, fig_list, desk_num)


def load_fig(fig_name, adr, desk_num):
    global photo_images

    file_name = ".\\png\\" + fig_name[:2] + ".png"

    if desk_num == 1:
        image_x, image_y = adr2imagecoord1(adr)
    else:
        image_x, image_y = adr2imagecoord2(adr)

    try:
        photo_image = PhotoImage(file=file_name)
        photo_images.append(photo_image)
        image = canv.create_image(image_x, image_y, image=photo_image)
        return [fig_name, image, adr]
    except:
        print("path error:", file_name)
        return []


def set_figpos(fig, adr, desk_num):
    fig[2] = adr
    if desk_num == 1:
        image_x, image_y = adr2imagecoord1(adr)
    else:
        image_x, image_y = adr2imagecoord2(adr)
    canv.coords(fig[1], image_x, image_y)


# Функции для работы с досками
def clear_sound():
    winsound.PlaySound("clear.wav", winsound.SND_FILENAME)


def clear_desk(desk_num):
    if desk_num == 1:
        for fig_num in range(len(white_figs1) - 1, -1, -1):
            fig = white_figs1[fig_num]
            move_fig(fig, "dA1", 1)
        for fig_num in range(len(black_figs1) - 1, -1, -1):
            fig = black_figs1[fig_num]
            move_fig(fig, "dA1", 1)
    else:
        for fig_num in range(len(white_figs2) - 1, -1, -1):
            fig = white_figs2[fig_num]
            move_fig(fig, "dA1", 2)
        for fig_num in range(len(black_figs2) - 1, -1, -1):
            fig = black_figs2[fig_num]
            move_fig(fig, "dA1", 2)

    if sound_mode == "on":
        canv.after(10, clear_sound)


def init_desk(desk_num):
    clear_desk(desk_num)
    if desk_num == 1:
        for fig_num in range(len(white_deleted1) - 1, -1, -1):
            fig = white_deleted1[fig_num]
            adr = fig[2][1:]
            move_fig(fig, adr, 1)
        for fig_num in range(len(black_deleted1) - 1, -1, -1):
            fig = black_deleted1[fig_num]
            adr = fig[2][1:]
            move_fig(fig, adr, 1)
    else:
        for fig_num in range(len(white_deleted2) - 1, -1, -1):
            fig = white_deleted2[fig_num]
            adr = fig[2][1:]
            move_fig(fig, adr, 2)
        for fig_num in range(len(black_deleted2) - 1, -1, -1):
            fig = black_deleted2[fig_num]
            adr = fig[2][1:]
            move_fig(fig, adr, 2)


def redraw_edge():
    canv.delete("let")
    # Нумерация строк и колонок для первой доски
    for row in range(8):
        x1 = left_desk1 - 15
        y1 = bottom_desk1 - (row + 0.5) * cell_size
        edge_text = str(row + 1) if flg_vid1 == 0 else str(8 - row)
        canv.create_text(x1, y1, text=edge_text, font=dFont, tag="let")

        x2 = left_desk1 + desk_size + 15
        canv.create_text(x2, y1, text=edge_text, font=dFont, tag="let")

    for col in range(8):
        x1 = left_desk1 + (col + 0.5) * cell_size
        y1 = bottom_desk1 + 15
        edge_text = col_names[col] if flg_vid1 == 0 else col_names[7 - col]
        canv.create_text(x1, y1, text=edge_text, font=dFont, tag="let")

        y2 = bottom_desk1 - desk_size - 15
        canv.create_text(x1, y2, text=edge_text, font=dFont, tag="let")

    # Нумерация строк и колонок для второй доски
    for row in range(8):
        x1 = left_desk2 - 15
        y1 = bottom_desk2 - (row + 0.5) * cell_size
        edge_text = str(row + 1) if flg_vid2 == 0 else str(8 - row)
        canv.create_text(x1, y1, text=edge_text, font=dFont, tag="let")

        x2 = left_desk2 + desk_size + 15
        canv.create_text(x2, y1, text=edge_text, font=dFont, tag="let")

    for col in range(8):
        x1 = left_desk2 + (col + 0.5) * cell_size
        y1 = bottom_desk2 + 15
        edge_text = col_names[col] if flg_vid2 == 0 else col_names[7 - col]
        canv.create_text(x1, y1, text=edge_text, font=dFont, tag="let")

        y2 = bottom_desk2 - desk_size - 15
        canv.create_text(x1, y2, text=edge_text, font=dFont, tag="let")


def redraw_desk(desk_num):
    redraw_edge()
    if desk_num == 1:
        for num in range(len(white_figs1)):
            fig = white_figs1[num]
            adr = fig[2]
            move_fig(fig, adr, 1)
        for num in range(len(black_figs1)):
            fig = black_figs1[num]
            adr = fig[2]
            move_fig(fig, adr, 1)
    else:
        for num in range(len(white_figs2)):
            fig = white_figs2[num]
            adr = fig[2]
            move_fig(fig, adr, 2)
        for num in range(len(black_figs2)):
            fig = black_figs2[num]
            adr = fig[2]
            move_fig(fig, adr, 2)


def draw_desk():
    # Первая доска
    for row in range(8):
        for col in range(8):
            x1 = left_desk1 + col * cell_size
            y1 = bottom_desk1 - row * cell_size
            x2 = x1 + cell_size
            y2 = y1 - cell_size
            rect_color = rect_colors[(row + col) % 2]
            canv.create_rectangle(x1, y1, x2, y2, fill=rect_color,
                                  tag=f"r1_{row}{col}")

    # Вторая доска
    for row in range(8):
        for col in range(8):
            x1 = left_desk2 + col * cell_size
            y1 = bottom_desk2 - row * cell_size
            x2 = x1 + cell_size
            y2 = y1 - cell_size
            rect_color = rect_colors[(row + col) % 2]
            canv.create_rectangle(x1, y1, x2, y2, fill=rect_color,
                                  tag=f"r2_{row}{col}")

    redraw_edge()
    # Внешние края досок
    canv.create_rectangle(left_desk1 - 30, bottom_desk1 + 30,
                          left_desk1 + 430, bottom_desk1 - 430)
    canv.create_rectangle(left_desk2 - 30, bottom_desk2 + 30,
                          left_desk2 + 430, bottom_desk2 - 430)


def draw_figbox(desk_num):
    left = left_desk1 + 450 if desk_num == 1 else left_desk2 - 250
    bottom = bottom_desk1 if desk_num == 1 else bottom_desk2

    for row in range(8):
        for col in range(4):
            x1 = left + col * cell_size
            y1 = bottom - row * cell_size
            x2 = x1 + cell_size
            y2 = y1 - cell_size
            canv.create_rectangle(x1, y1, x2, y2, fill="pink",
                                  tag=f"dr{desk_num}_{row}{col + 10}")


def load_allfigs(desk_num):
    for col in range(8):
        white_adr = col_names[col] + "1"
        fig_name = whitefig_tags[col]
        fig = load_fig(fig_name, white_adr, desk_num)
        if desk_num == 1:
            white_figs1.append(fig)
        else:
            white_figs2.append(fig)

        black_adr = col_names[col] + "8"
        fig_name = blackfig_tags[col]
        fig = load_fig(fig_name, black_adr, desk_num)
        if desk_num == 1:
            black_figs1.append(fig)
        else:
            black_figs2.append(fig)

    for col in range(8):
        white_adr = col_names[col] + "2"
        fig_name = "wp" + str(col)
        fig = load_fig(fig_name, white_adr, desk_num)
        if desk_num == 1:
            white_figs1.append(fig)
        else:
            white_figs2.append(fig)

        black_adr = col_names[col] + "7"
        fig_name = "bp" + str(col)
        fig = load_fig(fig_name, black_adr, desk_num)
        if desk_num == 1:
            black_figs1.append(fig)
        else:
            black_figs2.append(fig)


# Логика ходов и проверок
def step_sound():
    winsound.PlaySound("step.wav", winsound.SND_FILENAME)


def is_capture_valid(fig, target_fig, from_adr, to_adr, desk_num):
    if fig[0][0] == target_fig[0][0]:
        return False

    # Для шведских шахмат все взятия допустимы
    return True


def is_move_valid(fig, from_adr, to_adr, desk_num):
    fig_type = fig[0][1]
    if desk_num == 1:
        from_row, from_col = adr2rowcol1(from_adr)
        to_row, to_col = adr2rowcol1(to_adr)
    else:
        from_row, from_col = adr2rowcol2(from_adr)
        to_row, to_col = adr2rowcol2(to_adr)

    delta_row = abs(to_row - from_row)
    delta_col = abs(to_col - from_col)

    if fig_type == 'p':  # Пешка
        return is_pawn_move_valid(fig, from_row, from_col, to_row, to_col, desk_num)
    elif fig_type == 'l':  # Ладья
        return is_rook_move_valid(from_row, from_col, to_row, to_col)
    elif fig_type == 'h':  # Конь
        return is_knight_move_valid(delta_row, delta_col)
    elif fig_type == 's':  # Слон
        return is_bishop_move_valid(delta_row, delta_col)
    elif fig_type == 'f':  # Ферзь
        return is_queen_move_valid(delta_row, delta_col)
    elif fig_type == 'k':  # Король
        return is_king_move_valid(delta_row, delta_col)
    else:
        return False


def is_pawn_move_valid(fig, from_row, from_col, to_row, to_col, desk_num):
    color = fig[0][0]  # 'w' (белые) или 'b' (черные)
    if desk_num == 1:
        direction = 1 if color == 'w' else -1  # Направление движения
    else:
        direction = -1 if color == 'w' else 1

    delta_row = to_row - from_row
    delta_col = abs(to_col - from_col)

    # Обычный ход на 1 клетку вперед
    if delta_col == 0 and delta_row == direction:
        return True

    # Первый ход на 2 клетки (только со стартовой позиции)
    if desk_num == 1:
        start_row = 1 if color == 'w' else 6
    else:
        start_row = 6 if color == 'w' else 1
    if (from_row == start_row and delta_col == 0
            and delta_row == 2 * direction):
        return True

    # Взятие по диагонали (на 1 клетку)
    if delta_col == 1 and delta_row == direction:
        if desk_num == 1:
            to_adr = rowcol2adr1(to_row, to_col)
        else:
            to_adr = rowcol2adr2(to_row, to_col)

        fig_num, fig_list = get_fignumlist(to_adr, desk_num)
        if fig_num >= 0 and fig_list[fig_num][0][0] != color:
            return True

    return False


def is_rook_move_valid(from_row, from_col, to_row, to_col):
    return (from_row == to_row) or (from_col == to_col)


def is_knight_move_valid(delta_row, delta_col):
    return (delta_row == 2 and delta_col == 1) or (delta_row == 1 and delta_col == 2)


def is_bishop_move_valid(delta_row, delta_col):
    return delta_row == delta_col


def is_queen_move_valid(delta_row, delta_col):
    return (delta_row == delta_col) or (delta_row == 0 or delta_col == 0)


def is_king_move_valid(delta_row, delta_col):
    return delta_row <= 1 and delta_col <= 1


def is_path_clear(from_adr, to_adr, desk_num):
    if desk_num == 1:
        from_row, from_col = adr2rowcol1(from_adr)
        to_row, to_col = adr2rowcol1(to_adr)
    else:
        from_row, from_col = adr2rowcol2(from_adr)
        to_row, to_col = adr2rowcol2(to_adr)

    step_row = 1 if to_row > from_row else (-1 if to_row < from_row else 0)
    step_col = 1 if to_col > from_col else (-1 if to_col < from_col else 0)

    current_row, current_col = from_row + step_row, from_col + step_col

    while (current_row != to_row) or (current_col != to_col):
        if desk_num == 1:
            current_adr = rowcol2adr1(current_row, current_col)
        else:
            current_adr = rowcol2adr2(current_row, current_col)

        if get_fignumlist(current_adr, desk_num)[0] >= 0:
            return False
        current_row += step_row
        current_col += step_col

    return True


# Основная функция обработки ходов
def sel_field(event):
    global sel_adr1, sel_fignum1, sel_figlist1, sel_adr2, sel_fignum2, sel_figlist2, current_team

    adr, desk_num = event2adr(event)
    if adr == "":
        return

    # Если выбрана фигура для размещения (код фигуры хранится в sel_adr)
    if (desk_num == 1 and len(sel_adr1) == 3) or (desk_num == 2 and len(sel_adr2) == 3):
        fig_type = sel_adr1 if desk_num == 1 else sel_adr2
        if place_captured_piece(fig_type, adr, desk_num):
            # Меняем команду после размещения фигуры
            current_team = 1 - current_team
            var_next.set(f"Команда {current_team + 1}")

            if sound_mode == "on":
                canv.after(10, step_sound)
        else:
            messagebox.showinfo("Ошибка", "Невозможно разместить эту фигуру!")
        return

    # Получаем информацию о выбранной фигуре
    fig_num, fig_list = get_fignumlist(adr, desk_num)

    # Обработка для первой доски
    if desk_num == 1:
        # Если выбрана фигура и кликнули на пустую клетку
        if len(sel_adr1) != 0 and fig_num < 0:
            fig = sel_figlist1[sel_fignum1]

            # Проверка допустимости хода
            if not is_move_valid(fig, sel_adr1, adr, 1):
                messagebox.showinfo("Ошибка", "Недопустимый ход!")
                return

            move_fig(fig, adr, 1)

            set_rectfon(sel_adr1, 1)
            sel_adr1 = ""
            sel_fignum1 = -1
            sel_figlist1 = []

            # Меняем команду после хода
            current_team = 1 - current_team
            var_next.set(f"Команда {current_team + 1}")

            if sound_mode == "on":
                canv.after(10, step_sound)
            return

        # Если выбрана фигура и кликнули на другую фигуру
        elif len(sel_adr1) != 0 and fig_num >= 0:
            # Если это фигура противника - попытаться съесть
            if sel_figlist1 != fig_list:
                fig = sel_figlist1[sel_fignum1]
                target_fig = fig_list[fig_num]

                if is_capture_valid(fig, target_fig, sel_adr1, adr, 1):
                    move_fig(target_fig, "dA1", 1)
                    move_fig(fig, adr, 1)

                    set_rectfon(sel_adr1, 1)
                    sel_adr1 = ""
                    sel_fignum1 = -1
                    sel_figlist1 = []

                    # Меняем команду после взятия
                    current_team = 1 - current_team
                    var_next.set(f"Команда {current_team + 1}")

                    if sound_mode == "on":
                        canv.after(10, step_sound)
                    return
                else:
                    messagebox.showinfo("Ошибка", "Невозможно съесть эту фигуру!")
                    return

        # Если не выбрана фигура и кликнули на фигуру - выбрать ее
        elif len(sel_adr1) == 0 and fig_num >= 0:
            # Проверяем, что фигура принадлежит текущей команде
            fig_color = fig_list[fig_num][0][0]
            if (current_team == 0 and fig_color == 'w') or (current_team == 1 and fig_color == 'b'):
                sel_adr1 = adr
                sel_fignum1 = fig_num
                sel_figlist1 = fig_list
                set_rectbright(sel_adr1, 1)
            else:
                messagebox.showinfo("Ошибка", "Сейчас ход другой команды!")
            return

    # Обработка для второй доски
    elif desk_num == 2:
        # Если выбрана фигура и кликнули на пустую клетку
        if len(sel_adr2) != 0 and fig_num < 0:
            fig = sel_figlist2[sel_fignum2]

            # Проверка допустимости хода
            if not is_move_valid(fig, sel_adr2, adr, 2):
                messagebox.showinfo("Ошибка", "Недопустимый ход!")
                return

            move_fig(fig, adr, 2)

            set_rectfon(sel_adr2, 2)
            sel_adr2 = ""
            sel_fignum2 = -1
            sel_figlist2 = []

            # Меняем команду после хода
            current_team = 1 - current_team
            var_next.set(f"Команда {current_team + 1}")

            if sound_mode == "on":
                canv.after(10, step_sound)
            return

        # Если выбрана фигура и кликнули на другую фигуру
        elif len(sel_adr2) != 0 and fig_num >= 0:
            # Если это фигура противника - попытаться съесть
            if sel_figlist2 != fig_list:
                fig = sel_figlist2[sel_fignum2]
                target_fig = fig_list[fig_num]

                if is_capture_valid(fig, target_fig, sel_adr2, adr, 2):
                    move_fig(target_fig, "dA1", 2)
                    move_fig(fig, adr, 2)

                    set_rectfon(sel_adr2, 2)
                    sel_adr2 = ""
                    sel_fignum2 = -1
                    sel_figlist2 = []

                    # Меняем команду после взятия
                    current_team = 1 - current_team
                    var_next.set(f"Команда {current_team + 1}")

                    if sound_mode == "on":
                        canv.after(10, step_sound)
                    return
                else:
                    messagebox.showinfo("Ошибка", "Невозможно съесть эту фигуру!")
                    return

        # Если не выбрана фигура и кликнули на фигуру - выбрать ее
        elif len(sel_adr2) == 0 and fig_num >= 0:
            # Проверяем, что фигура принадлежит текущей команде
            fig_color = fig_list[fig_num][0][0]
            if (current_team == 0 and fig_color == 'w') or (current_team == 1 and fig_color == 'b'):
                sel_adr2 = adr
                sel_fignum2 = fig_num
                sel_figlist2 = fig_list
                set_rectbright(sel_adr2, 2)
            else:
                messagebox.showinfo("Ошибка", "Сейчас ход другой команды!")
            return


def create_piece_panel():
    piece_frame = Frame(root)
    piece_frame.grid(row=13, column=0, columnspan=6, pady=10)

    Label(piece_frame, text="Доступные фигуры:").grid(row=0, column=0, columnspan=12)

    # Кнопки для всех типов фигур
    pieces = ["wp", "bp", "wl", "bl", "wh", "bh", "ws", "bs", "wf", "bf", "wk", "bk"]
    for i, piece in enumerate(pieces):
        btn = Button(piece_frame, text=piece, width=3,
                     command=lambda p=piece: select_piece_for_placement(p))
        btn.grid(row=1, column=i, padx=2)


def select_piece_for_placement(piece):
    global sel_adr1, sel_adr2

    # Проверяем, какая доска активна
    if len(sel_adr1) == 2:  # Если на первой доске выбрана клетка
        sel_adr1 = piece
    elif len(sel_adr2) == 2:  # Если на второй доске выбрана клетка
        sel_adr2 = piece
    else:
        messagebox.showinfo("Подсказка", "Сначала выберите клетку на доске, затем фигуру для размещения")


def disp_rowcol(event):
    global sel_adr1, sel_fignum1, sel_figlist1, sel_adr2, sel_fignum2, sel_figlist2

    # Отмена выбора для первой доски
    if len(sel_adr1) > 0:
        set_rectfon(sel_adr1, 1)
        sel_adr1 = ""
        sel_fignum1 = -1
        sel_figlist1 = []

    # Отмена выбора для второй доски
    if len(sel_adr2) > 0:
        set_rectfon(sel_adr2, 2)
        sel_adr2 = ""
        sel_fignum2 = -1
        sel_figlist2 = []


# Сетевые функции
def disp_mess(mess):
    print(mess)


def send_mess(mess):
    client = socket(AF_INET, SOCK_STREAM)
    bin_mess = bytes(mess, 'UTF-8')
    try:
        client.connect(server_address)
        client.sendall(bin_mess)
        res = " "
    except:
        res = "СЕРВЕР ВЫКЛЮЧЕН :("
    finally:
        client.close()
    return res


def put_mess(mess):
    global lst_in, busy_in
    while busy_in:
        sleep(0.001)
    busy_in = 1
    lst_in.append(mess)
    busy_in = 0


def work_in():
    global lst_in, busy_in
    locserv_addr = ('0.0.0.0', 5400)
    loc_sock = socket(AF_INET, SOCK_STREAM)
    loc_sock.bind(locserv_addr)
    loc_sock.listen(5)

    while True:
        connection, address = loc_sock.accept()
        bin_data = connection.recv(1024)
        str_data = bin_data.decode("utf-8")
        connection.close()

        put_mess(address[0] + "|" + str_data)
        sleep(0.001)


def hndl_invite(lst_mess):
    global net_mode, ip_partn, flg_vid1, record_flag, partn, server_address
    partn = lst_mess[2]
    MsgBox = messagebox.askquestion('Вас приглашает ' + partn, 'Согласны сыграть?', icon='question')
    winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)

    nick = var_nick.get()
    if not nick:
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        nick = simpledialog.askstring("Замечание", "Введите Ваш Ник")
        var_nick.set(nick)

    if MsgBox == 'yes':
        net_mode = "connect"
        var_netmode.set("Сетевой")
        var_partn.set(partn)
        ip_partn = lst_mess[0]
        server_address = (ip_partn, 5400)
        init_desk(1)
        flg_vid1 = 1
        redraw_desk(1)
        record_flag = 1
        var_next.set("Команда 1")
        res = send_mess("agree|" + nick)
    else:
        res = send_mess("refuse|" + nick)


def hndl_agree(lst_mess):
    global net_mode, ip_partn, flg_vid1, record_flag, partn
    partn = lst_mess[2]
    var_partn.set(partn)
    ip_partn = lst_mess[0]

    MsgBox = messagebox.showinfo("Ответ:", partn + ' согласен, начинаем игру', icon='warning')
    net_mode = "connect"
    var_netmode.set("Сетевой")
    flg_vid1 = 0
    init_desk(1)
    record_flag = 1
    var_partn.set(partn)
    var_next.set("Команда 1")


def hndl_refuse(lst_mess):
    global net_mode, ip_partn, flg_vid1, record_flag, partn
    partn = lst_mess[2]
    var_partn.set(partn)
    ip_partn = lst_mess[0]
    MsgBox = messagebox.showinfo("Ответ:", partn + ' отказался от игры :(', icon='warning')
    net_mode = "local"
    var_netmode.set("Локальный")
    record_flag = 0
    ip_partn = ""
    partn = ""
    var_partn.set(partn)


def hndl_step(lst_mess):
    step_text = lst_mess[2]


def change_nextcolor():
    cur_color = var_next.get()
    if cur_color == "Белые":
        var_next.set("Черные")
    else:
        var_next.set("Белые")


def main():
    global lst_in, busy_in, current_team

    if len(lst_in) > 0:
        while busy_in:
            sleep(0.001)
        busy_in = 1
        str_in = lst_in.pop(0)
        busy_in = 0

        lst_mess = str_in.split("|")

        if lst_mess[1] == 'move':
            # Обработка хода партнера
            fig_name = lst_mess[2]
            from_adr = lst_mess[3]
            to_adr = lst_mess[4]
            desk_num = int(lst_mess[5])

            # Находим фигуру
            fig_num, fig_list = get_fignumlist(from_adr, desk_num)
            if fig_num >= 0:
                fig = fig_list[fig_num]
                move_fig(fig, to_adr, desk_num)

            # Меняем текущую команду
            current_team = 1 - current_team
            var_next.set(f"Команда {current_team + 1}")

    root.after(main_tau, main)


# Создание GUI
root = Tk()
root.resizable(width=False, height=False)
dFont = font.Font(family="helvetica", size=12)
stl = ttk.Style()

root.configure(background=root_color)
stl.configure('.', font=dFont, background=root_color, foreground="black")

# Элементы управления сетью
ttk.Label(root, text='Ваше имя:').grid(row=0, column=0, sticky=E, padx=5)

var_nick = StringVar()
var_nick.set("")
edt_nick = ttk.Entry(root, width=btn_width, textvariable=var_nick, font=dFont)
edt_nick.grid(row=0, column=1, padx=5, pady=5, sticky=W)

ttk.Label(root, text='Партнер:').grid(row=0, column=2, sticky=E, pady=5)

var_partn = StringVar()
var_partn.set("")
edt_partn = ttk.Entry(root, width=btn_width, textvariable=var_partn, font=dFont)
edt_partn.grid(row=0, column=3, padx=5, pady=5, sticky=W)

ttk.Label(root, text='Режим игры:').grid(row=0, column=4, sticky=E, pady=5)

var_netmode = StringVar()
var_netmode.set("Локальный")
edt_netmode = ttk.Entry(root, width=btn_width, textvariable=var_netmode, font=dFont)
edt_netmode.grid(row=0, column=5, padx=5, pady=5, sticky=W)

ttk.Label(root, text='Очередь хода:').grid(row=1, column=0, sticky=E, padx=5)

var_next = StringVar()
var_next.set("Команда 1")
edt_next = ttk.Entry(root, width=btn_width, textvariable=var_next, font=dFont)
edt_next.grid(row=1, column=1, padx=5, pady=5, sticky=W)


# Кнопки управления
def fnc_invite():
    global ip_partn, server_address, net_mode, flg_vid1, record_flag
    if net_mode == "connect": return

    nick = var_nick.get()
    ip_partn = simpledialog.askstring("Замечание", "Введите IP-адрес партнера", initialvalue=ip_partn)
    if not nick:
        nick = simpledialog.askstring("Замечание", "Введите Ваш Ник")
        var_nick.set(nick)

    server_address = (ip_partn, 5400)
    res = send_mess("invite|" + nick)
    if len(res) > 2:
        messagebox.showinfo("Ошибка связи :(", res)


ttk.Button(root, text="Пригласить", width=btn_width,
           command=fnc_invite).grid(row=1, column=3, sticky=W, pady=5, padx=5)


def fnc_refuse():
    global ip_partn, server_address, net_mode
    if net_mode == "local": return

    res = send_mess("refuse|nick")
    var_partn.set("")
    server_address = ("", 0000)
    net_mode = "local"
    var_netmode.set("Локальный")


ttk.Button(root, text="Отключиться", width=btn_width,
           command=fnc_refuse).grid(row=1, column=5, sticky=W, pady=5, padx=5)

# Панель с канвой
pnl_left = Frame(root)
pnl_left.grid(row=2, column=0, columnspan=6, rowspan=8, pady=10, padx=10)

canv = Canvas(pnl_left, width=2 * desk_size + 650, height=desk_size + 100)
canv.pack()

canv.bind("<Button-3>", disp_rowcol)
canv.bind("<Button-1>", sel_field)


def block_bynet():
    messagebox.showinfo("Блокировка:", "В сетевом режиме не работает :(", icon='warning')


def fnc_clear():
    if net_mode == "connect":
        block_bynet()
        return
    clear_desk(1)
    clear_desk(2)


row_for_buttons = 12  # Новая строка для всех кнопок
column_start = 0  # Начинаем с первого столбца

ttk.Button(root, text="Очистить доски", width=btn_width,
           command=fnc_clear).grid(row=row_for_buttons, column=column_start,
                                   padx=5, pady=5, sticky=W)
column_start += 1


def fnc_init():
    global team_pieces, current_team

    if net_mode == "connect":
        block_bynet()
        return

    team_pieces = [[], []]  # Очищаем пулы фигур
    current_team = 0  # Начинает команда 1
    var_next.set("Команда 1")

    init_desk(1)
    init_desk(2)


ttk.Button(root, text="Новая игра", width=btn_width,
           command=fnc_init).grid(row=row_for_buttons, column=column_start,
                                  padx=5, pady=5, sticky=W)
column_start += 1


def fnc_rotatedesk1():
    global flg_vid1
    if net_mode == "connect":
        block_bynet()
        return
    flg_vid1 = 1 if flg_vid1 == 0 else 0
    redraw_desk(1)


ttk.Button(root, text="Повернуть доску 1", width=btn_width,
           command=fnc_rotatedesk1).grid(row=row_for_buttons, column=column_start,
                                         padx=5, pady=5, sticky=W)
column_start += 1


def fnc_rotatedesk2():
    global flg_vid2
    flg_vid2 = 1 if flg_vid2 == 0 else 0
    redraw_desk(2)


ttk.Button(root, text="Повернуть доску 2", width=btn_width,
           command=fnc_rotatedesk2).grid(row=row_for_buttons, column=column_start,
                                         padx=5, pady=5, sticky=W)
column_start += 1


def fnc_soundonoff():
    global sound_mode
    if sound_mode == "on":
        btn_soundmode["text"] = "Включить звук"
        sound_mode = "off"
    else:
        sound_mode = "on"
        btn_soundmode["text"] = "Отключить звук"


btn_soundmode = ttk.Button(root, text="Включить звук", width=btn_width,
                           command=fnc_soundonoff)
btn_soundmode.grid(row=row_for_buttons, column=column_start,
                   padx=5, pady=5, sticky=W)

# Инициализация досок
draw_desk()
draw_figbox(1)
draw_figbox(2)
load_allfigs(1)
load_allfigs(2)

# Создаем панель для размещения фигур
create_piece_panel()

# Запуск сетевого потока и главного цикла
tr_in = threading.Thread(target=work_in)
tr_in.daemon = True
tr_in.start()

main()
root.mainloop()