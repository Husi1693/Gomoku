import ui
import pickle


def main():
    while True: 
        choice = menu()
        if choice == 1:
            play_standard_size_game()
        elif choice == 2:
            play_game()
        elif choice == 3:
            play_game_with_remove()
        elif choice == 4:
            scoreboard_data = load_scoreboard()
            ui.display_headline("scoreboard")
            ui.display_scoreboard(scoreboard_data)
            ui.prompt("Please press ENTER to return to the menu: ")

        elif choice == 5:
            break

    
def menu():
    
    ui.display_headline("GOMOKU")

    menu_titles = ["Play standard game", "Play game with adjustable size", "Play game with ajustable size and remove", "Scoreboard", "Exit"]
    ui.display_menu(menu_titles)  
       
    choice = ""
    while choice not in ["1", "2", "3", "4", "5"]:
        choice = (ui.prompt("Please enter its number to select an item"))

    return int(choice)


def save_scoreboard(scoreboard):
    with open("scoreboard.dat", "wb") as f: 
        pickle.dump(scoreboard, f)
    
    return None

def load_scoreboard():

    try: 
        with open("scoreboard.dat", "rb") as f:
            scoreboard = pickle.load(f)
    
    except:
        return{}
    
    scoreboard_filtered = {name: score for name, score in scoreboard.items() if score > 0}


    return scoreboard_filtered





def is_grid_full(grid):
    for row in grid:
        for col in row:
            if col is None:
                return False
    
    return True

def is_game_won(grid):
    cols, rows = len(grid), len(grid[0])
    directions = [
        (1,0),  # horizontal
        (0,1),  # vertical
        (1,1),  # diagonal down-right
        (1,-1)  # diagonal up-right
    ]
    # check for winner

    for r in range(rows):
        for c in range(cols):

            stone = grid[r][c]
            if stone is None or stone == " ":
                continue
            
            # jede Richtung prüfen
            for dr, dc in directions:
                count = 1

                # vier Steine weiter prüfen (5 in Reihe → gewonnen)
                for i in range(1, 5):
                    nr = r + dr * i
                    nc = c + dc * i

                    if not (0 <= nr < rows and 0 <= nc < cols):
                        break

                    if grid[nr][nc] != stone:
                        break

                    count += 1

                if count == 5:
                    return True

    return False

    


def play_turn(grid, player_name, is_player_a, can_remove):
    stone_color = "X" if is_player_a else "O"
    ui.display_headline("gomoku")
    ui.display_turn_start(player_name, is_player_a)
    ui.display_grid(grid)

    height = len(grid)
    width = len(grid[0])


    while True:
        input = ui.prompt("Please enter row and column (e.g., '8 10')")
    
        #Check if removal is requested
        if can_remove and input.strip() == "-1":
            return None
        
        #make sure the input is two integers
        splitted = input.split()

        if len(splitted) != 2:
            continue

        try: 
            #check if we have an input of two integers
            row, col = map(int, splitted)
            
            row = int(splitted[0])
            col = int(splitted[1])

            row_index = row - 1
            col_index = width - col

            #make sure the input is within the grid and free
            if 0 <= row_index < height and 0 <= col_index < width and grid[col_index][row_index] is None:
                grid[col_index][row_index] = "X" if is_player_a else "O"
                return (col_index, row_index)
        
        except ValueError:
            pass



def play_standard_size_game():
    # Input der Spielernamen
    ui.display_headline("configure names")
    name_a = ui.prompt("Please enter the name of player A")
    while len(name_a.strip()) == 0:
        name_a = ui.prompt("Please enter the name of player A")

    name_b = ui.prompt("Please enter the name of player B")
    while len(name_b.strip()) == 0 or name_b == name_a:
        name_b = ui.prompt("Please enter the name of player B")

    # 15x15 Grid
    grid = [[None for _ in range(15)] for _ in range(15)]
    is_player_a = True

    while is_grid_full != True or is_game_won != True:
        player_name = name_a if is_player_a else name_b


        # Turn ausführen (zeigt Grid, fragt nach Eingabe)
        play_turn(grid, player_name, is_player_a, can_remove=False)

        # Prüfen auf Sieg
        if is_game_won(grid):
            ui.display_headline("congratulations")
            ui.display_message(f"{player_name} won the game!")

            # Scoreboard speichern
            scoreboard = load_scoreboard()
            scoreboard[player_name] = scoreboard.get(player_name, 0) + 1
            save_scoreboard(scoreboard)

            ui.prompt("Please press ENTER to return to the menu:")
            return player_name

        # Prüfen auf Draw
        if is_grid_full(grid):
            ui.display_headline("oh no - a draw")
            ui.display_message("Unfortunately, nobody won the game :(")
            ui.prompt("Please press ENTER to return to the menu:")
            return None

        # Spieler wechseln
        is_player_a = not is_player_a



def play_game():

    ui.display_headline("Configure Grid")

    # Spalten abfragen
    while True:
        columns = int(ui.prompt("Please enter the number of columns (10..20): "))
        if 10 <= columns <= 20:
            break

    # Zeilen abfragen
    while True:
        rows = int(ui.prompt("Please enter the number of rows      (10..20): "))
        if 10 <= rows <= 20:
            break  # gültig → Schleife verlassen

    return columns, rows



def play_game_with_remove():
    return None

if __name__ == '__main__':
    main()