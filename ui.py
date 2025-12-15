def __clear():
    """
    Clears the screen
    """
    print('\n' * 15)

def display_grid(grid):
    """
    Displays the game grid including column numbers and coins.
    Appends an empty line.

    :grid: The grid as two-dimensional array of columns and per-column row values,
        from left to right and bottom to top. None indicates empty fields, True coins
        of player A and False coins of player B.
    """
    cols, rows = len(grid), len(grid[0])
    print('   ', ''.join([f'{i:2d}  ' for i in range(1, cols + 1)]), sep='')
    for row in range(rows):
        row_values = [grid[col][rows - row - 1] for col in range(cols)] 
        row_symbols = ['X' if v else 'O' if v == False else ' ' for v in row_values]
        # Adjust spacing for row numbers
        if row < 9: 
            print(row+1, ' ', '|', ''.join([f' {s} |' for s in row_symbols]), sep='')
        else: 
            print(row+1, '|', ''.join([f' {s} |' for s in row_symbols]), sep='')
    print('')

def display_headline(headline):
    """
    Displays a headline in uppercase. Clears the screen first and append an empty line.

    :headline: Headline string to display.
    """
    __clear()
    print(headline.upper(), '\n', sep='')

def display_menu(items):
    """
    Displays a menu item list.

    :items: Ordered list of menu items (strings).
    """
    display_message('\n'.join([f'{i + 1}. {item}' for i, item in enumerate(items)]))

def display_message(message):
    """
    Displays a message.

    :message: The message string to display.
    """
    print(message, '\n', sep='')

def display_scoreboard(scoreboard):
    """
    Displays the scoreboard in descending order.

    :scoreboard: The scoreboard as dictionary of player names and their scores as integers.
    """
    if len(scoreboard) == 0:
        display_message('no scores available')
    else:
        # Descendingly sorted list of bi-tuple (name, score)
        highscore = sorted(scoreboard.items(), key=lambda x:x[1], reverse=True)
        display_message('\n'.join([f'{i + 1}. {name} ({score})' for i, (name, score) in enumerate(highscore)]))

def display_turn_start(player_name, is_player_a):
    """
    Display that a new turn starts with the name and stone color of the player who's turn it is.
    Clears the screen first.

    :player_name: Name of the player.
    :is_player_a: Boolean that is true if the player is player A.
    """
    display_headline('gomoku')
    display_message(f"{player_name}, it is your turn! Your stone color is {'X' if is_player_a else 'O'}.")

def prompt(message):
    """
    Displays a prompt with the provided message and waits for a line of user input on STDIN.

    :message: Message to show first.
    :return: String read from STDIN without tailing \n linefeed character.
    """
    return input(f'{message}: ').rstrip('\n')