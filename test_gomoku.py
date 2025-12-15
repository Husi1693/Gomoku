import io, os, re
from unittest.mock import Mock
# Here import gomoku.py
from gomoku import *

SCOREBOARD_FILE = 'scoreboard.dat'

HEADLINE_MENU = 'gomoku'
HEADLINE_SCOREBOARD = 'gomoku scoreboard'
HEADLINE_SIZE = 'configure grid'
HEADLINE_NAMES = 'configure names'
HEADLINE_TURN = 'gomoku'
HEADLINE_DRAW = 'oh no - a draw'
HEADLINE_WIN = 'congratulations'

PROMPT_MENU = 'Please enter its number to select an item'
def prompt_size(is_columns):
    return 'Please enter the number of ' + ('columns' if is_columns else 'rows   ') + ' (10..20)'
def prompt_name(is_player_A):
    return 'Please enter the name of player ' + ('A' if is_player_A else 'B')
PROMPT_TURN = "Please enter row and column (e.g., '8 10')"
PROMPT_RETURN_MENU = 'Please press ENTER to return to the menu'

def message_turn(player_name, color):
    return f'{player_name}, it is your turn! Your stone color is {color}.'
def message_won(player_name):
    return f'{player_name} won the game!'
MESSAGE_DRAW = 'Unfortunately, nobody won the game :('

def remove_file(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

def empty_grid(cols, rows):
    return [[None] * rows for _ in range(cols)]

def full_grid(cols, rows):
    return [[(row // 2 + col) % 2 == 0 for row in range(rows)] for col in range(cols)]

def mock_ui_fn(monkeypatch, function, return_values = None):
    params = []
    def record_params(param):
        params.append(param.copy() if type(param) == dict else param)
        if return_values != None:
            if len(return_values) < len(params):
                raise RuntimeError(f'{function} called too many times')
            else:
                return return_values[len(params) - 1]
    monkeypatch.setattr(ui, function, record_params)
    return params


def mock_menu_end_with_exit(monkeypatch, menu_choices = []):
    menu_mock = Mock()
    menu_mock.side_effect = menu_choices + [5]
    monkeypatch.setattr('gomoku.menu', menu_mock)
    main()
    expected_menu_calls = len(menu_choices) + 1
    assert menu_mock.call_count == expected_menu_calls

########################## MAIN MENU TEST ##########################
def test_main_exit(monkeypatch):
    mock_menu_end_with_exit(monkeypatch)

def test_main_play_standard_game_exit(monkeypatch):
    play_standard_size_game_mock = Mock()
    play_standard_size_game_mock.return_value = None
    monkeypatch.setattr('gomoku.play_standard_size_game', play_standard_size_game_mock)
    mock_menu_end_with_exit(monkeypatch, [1])
    play_standard_size_game_mock.assert_called_once()

def test_main_play_game_with_adjustable_size_exit(monkeypatch):
    play_game_mock = Mock()
    play_game_mock.return_value = None
    monkeypatch.setattr('gomoku.play_game', play_game_mock)
    mock_menu_end_with_exit(monkeypatch, [2])
    play_game_mock.assert_called_once()

def test_main_play_game_with_adjustable_size_and_remove_exit(monkeypatch):
    play_game_with_remove_mock = Mock()
    play_game_with_remove_mock.return_value = None
    monkeypatch.setattr('gomoku.play_game_with_remove', play_game_with_remove_mock)
    mock_menu_end_with_exit(monkeypatch, [3])
    play_game_with_remove_mock.assert_called_once()

def test_main_scoreboard_exit(monkeypatch):
    stdin = io.StringIO('\n')
    monkeypatch.setattr('sys.stdin', stdin)
    mock_menu_end_with_exit(monkeypatch, [4])
    assert stdin.closed or stdin.read() == '' # Check that all input was read

def test_main_scoreboard_interaction_exit(monkeypatch):
    headlines = mock_ui_fn(monkeypatch, 'display_headline')
    scoreboards = mock_ui_fn(monkeypatch, 'display_scoreboard')
    prompts = mock_ui_fn(monkeypatch, 'prompt', [''])

    remove_file(SCOREBOARD_FILE)
    mock_menu_end_with_exit(monkeypatch, [4])

    assert [re.sub('[-–]', '', headline.lower()) for headline in headlines] == [HEADLINE_SCOREBOARD]
    assert scoreboards == [{}]
    assert prompts == [PROMPT_RETURN_MENU]



inputs_menu = ['0', '1', '2', '3', '4', 'test', '5']

def test_menu(monkeypatch):
    stdin = io.StringIO('\n'.join(inputs_menu))
    monkeypatch.setattr('sys.stdin', stdin)
    assert [menu() for _ in range(5)] == [i for i in range(1, 6)]
    assert stdin.read() == '' # Check that all input was read

def test_menu_interaction(monkeypatch):
    headlines = mock_ui_fn(monkeypatch, 'display_headline')
    menus = mock_ui_fn(monkeypatch, 'display_menu')
    prompts = mock_ui_fn(monkeypatch, 'prompt', inputs_menu)

    expected_selections = [i for i in range(1, 6)]
    assert [menu() for _ in range(5)] == expected_selections
    expected_headlines = [HEADLINE_MENU] * 5
    assert [re.sub('[-–]', '', headline.lower()) for headline in headlines] == expected_headlines
    assert len(menus) == 5 # 5 menu calls
    assert all([menu == menus[0] for menu in menus[1:]]) == True # Menus are identical
    assert all([len(menu) == 5 for menu in menus]) == True # Menus have 5 items
    expected_prompts = [PROMPT_MENU] * 7
    assert prompts == expected_prompts



def test_save_scoreboard_creates_file():
    remove_file(SCOREBOARD_FILE)
    save_scoreboard({})
    assert os.path.exists(SCOREBOARD_FILE) == True
    remove_file(SCOREBOARD_FILE)

def test_load_scoreboard_nonexisting():
    remove_file(SCOREBOARD_FILE)
    assert load_scoreboard() == {}

def test_load_scoreboard_invalid_file():
    with open(SCOREBOARD_FILE, 'w') as score_file:
        score_file.write('Non-empty file')
    assert load_scoreboard() == {}
    remove_file(SCOREBOARD_FILE)

def test_save_load_scoreboard():
    scoreboard = { 'Player A': 3, 'Player C': 4 }
    save_scoreboard(scoreboard)
    assert load_scoreboard() == scoreboard

def test_save_load_filter_scoreboard():
    save_scoreboard({ 'Player A': 3, 'Player B': 0, 'Player C': 4 })
    assert load_scoreboard() == { 'Player A': 3, 'Player C': 4 }

def test_save_delete_load_scoreboard():
    save_scoreboard({ 'Player A': 3, 'Player A': 4 })
    remove_file(SCOREBOARD_FILE)
    assert load_scoreboard() == {}

##########################  CORE GAME LOGIC TEST ##########################

def test_is_grid_full():
    assert is_grid_full(full_grid(7, 6)) == True

def test_is_grid_full_not():
    grid = full_grid(7, 6)
    grid[1][3] = None
    assert is_grid_full(grid) == False

def test_play_turn(monkeypatch):
    stdin = io.StringIO('-1\n4\n11 3\n')
    monkeypatch.setattr('sys.stdin', stdin)
    grid = empty_grid(15, 15)
    expected = (2, 4)
    assert play_turn(grid, 'Player A', is_player_a = True, can_remove = False) == expected
    assert stdin.read() == '' # Check that all input was read

def test_play_turn_remove(monkeypatch):
    stdin = io.StringIO('-1')
    monkeypatch.setattr('sys.stdin', stdin)
    grid = empty_grid(15, 15)
    assert play_turn(grid, 'Player A', is_player_a = True, can_remove = True) == None
    assert stdin.read() == '' # Check that all input was read

def test_play_turn_interaction(monkeypatch):
    display_turn_start_mock = Mock()
    monkeypatch.setattr(ui, 'display_turn_start', display_turn_start_mock)
    display_grid_mock = Mock()
    monkeypatch.setattr(ui, 'display_grid', display_grid_mock)
    prompts = mock_ui_fn(monkeypatch, 'prompt', ['-1', '4 3'])

    grid = empty_grid(15, 15)
    expected = (2, 11)
    assert play_turn(grid, 'Player A', is_player_a = True, can_remove = False) == expected
    
    display_turn_start_mock.assert_called_once_with('Player A', True)
    display_grid_mock.assert_called_once_with(grid)
    assert prompts == [PROMPT_TURN] * 2

def generate_safe_draw_moves(n):
    moves = []
    # pattern repeats every 4 rows
    for r in range(1, n+1):
        is_A_row = ((r - 1) // 2) % 2 == 0
        for c in range(1, n+1):
            if is_A_row:
                # Row starts with A: A, B, A, B...
                cell_is_A = (c % 2 == 1)
            else:
                # Row starts with B: B, A, B, A...
                cell_is_A = (c % 2 == 0)

            moves.append((r, c, cell_is_A))

    result_moves = []
    move_index = 0
    for r, c, intended_A in moves:
        correct_player_A = (move_index % 2 == 0)
        if intended_A != correct_player_A:
            # swap with next move (guaranteed possible)
            next_r, next_c, next_intended_A = moves[move_index+1]
            moves[move_index] = (next_r, next_c, next_intended_A)
            moves[move_index+1] = (r, c, intended_A)
            r, c, intended_A = moves[move_index]
        result_moves.append(f"{r} {c}")
        move_index += 1

    return result_moves

# test of is_game_won function
def test_is_game_won_empty():
    # Test that an empty grid returns False
    grid = empty_grid(15, 15)
    assert is_game_won(grid) == False


def test_is_game_won_horizontal():
    # Test 5 stones in a row (Horizontal)
    grid = empty_grid(15, 15)
    # Place 5 'True' (Player A) stones from (0,0) to (4,0)
    for col in range(5):
        grid[col][0] = True
    assert is_game_won(grid) == True


def test_is_game_won_vertical():
    # Test 5 stones in a column (Vertical)
    grid = empty_grid(15, 15)
    # Place 5 'False' (Player B) stones from (5,5) to (5,9)
    for row in range(5, 10):
        grid[5][row] = False
    assert is_game_won(grid) == True


def test_is_game_won_diagonal_down():
    # Test Diagonal Down-Right direction (1, 1)
    grid = empty_grid(15, 15)
    # Place stones at (1,1), (2,2), (3,3), (4,4), (5,5)
    for i in range(5):
        grid[1 + i][1 + i] = True
    assert is_game_won(grid) == True


def test_is_game_won_diagonal_up():
    # Test Diagonal Up-Right direction (1, -1)
    grid = empty_grid(15, 15)
    # Place stones starting at col 2, row 6 going up to col 6, row 2
    # (2,6), (3,5), (4,4), (5,3), (6,2)
    for i in range(5):
        grid[2 + i][6 - i] = True
    assert is_game_won(grid) == True


def test_is_game_won_negative_cases():
    grid = empty_grid(15, 15)

    # Case 1: Only 4 stones in a row (Not a win)
    for i in range(4):
        grid[i][0] = True
    assert is_game_won(grid) == False

    # Case 2: 5 stones in a row, but mixed colors (Not a win)
    # True, True, True, True, False
    grid[4][0] = False
    assert is_game_won(grid) == False


##########################  GAME TEST ON STANDARD BOARD ##########################
def test_play_standard_size_game_draw(monkeypatch):
    moves = generate_safe_draw_moves(15)

    stdin = io.StringIO(
        "Player A\nPlayer B\n" +
        "\n".join(moves) +
        "\n\n"  # final Enter for return to menu
    )

    monkeypatch.setattr('sys.stdin', stdin)

    assert play_standard_size_game() is None
    assert stdin.read() == ''  # Ensure all input was consumed

# DIAGONAL WIN
winning_moves_A = ['8 8', '9 9', '7 7', '10 10', '6 6', '11 11', '5 5', '12 12', '4 4']

inputs_standard_size_game_win_A = \
    ['Player A', 'Player B'] + \
    winning_moves_A + \
    [''] # final ENTER for return to menu

def test_play_standard_size_game_interaction_win_A(monkeypatch):
    TOTAL_TURNS = 9

    PLAYER_A_NAME = 'Player A'
    PLAYER_B_NAME = 'Player B'

    headlines = mock_ui_fn(monkeypatch, 'display_headline')
    messages = mock_ui_fn(monkeypatch, 'display_message')
    prompts = mock_ui_fn(monkeypatch, 'prompt', inputs_standard_size_game_win_A)

    play_standard_size_game()

    expected_headlines = [HEADLINE_NAMES] + [HEADLINE_TURN] * TOTAL_TURNS + [HEADLINE_WIN]
    assert headlines == expected_headlines

    MESSAGE_WIN_A = f'{PLAYER_A_NAME} won the game!'

    expected_messages = ([message_turn(PLAYER_A_NAME, 'X'), message_turn(PLAYER_B_NAME, 'O')] * 4) \
                        + [message_turn(PLAYER_A_NAME, 'X')] \
                        + [MESSAGE_WIN_A]
    assert messages == expected_messages

    expected_prompts = [prompt_name(True), prompt_name(False)] + \
                       [PROMPT_TURN] * TOTAL_TURNS + \
                       [PROMPT_RETURN_MENU]
    assert prompts == expected_prompts


COLS = '15'
ROWS = '15'
PLAYER_A = 'Player A'
PLAYER_B = 'Player B'

draw_moves = generate_safe_draw_moves(15)

inputs_game_draw = [
    COLS,
    ROWS,
    PLAYER_A,
    PLAYER_B
] + draw_moves + [
    '',
    ''
]

# test on custom size, use 15x15 because is easier to check winning
def test_play_game_draw(monkeypatch):
    stdin = io.StringIO('\n'.join(inputs_game_draw))
    monkeypatch.setattr('sys.stdin', stdin)

    result = play_game()

    assert result == None

    assert stdin.read() == ''

# test UI flow when the game end in a draw.
def test_play_game_interaction_draw(monkeypatch):
    headlines = mock_ui_fn(monkeypatch, 'display_headline')
    messages = mock_ui_fn(monkeypatch, 'display_message')
    prompts = mock_ui_fn(monkeypatch, 'prompt', inputs_game_draw)

    play_game()

    expected_headlines = [HEADLINE_SIZE, HEADLINE_NAMES] + \
                         [HEADLINE_TURN] * 225 + \
                         [HEADLINE_DRAW]

    assert headlines == expected_headlines
    expected_messages = [message_turn('Player A', 'X'), message_turn('Player B', 'O')] * 112 + \
                        [message_turn('Player A', 'X'), MESSAGE_DRAW]
    # check UI messages
    assert messages == expected_messages
    # check prompts
    expected_prompts = [prompt_size(True), prompt_size(False), prompt_name(True), prompt_name(False)] + \
                       [PROMPT_TURN] * 225 + \
                       [PROMPT_RETURN_MENU]

    assert prompts == expected_prompts

# vertical win
inputs_game_win = [
    '15', '15',
    'Player A', 'Player B',
    '1 1', '2 1',
    '1 2', '2 2',
    '1 3', '2 3',
    '1 4', '2 4',
    '1 5',
    '',
    ''
]
def test_play_game_win(monkeypatch):
    stdin = io.StringIO('\n'.join(inputs_game_win))
    monkeypatch.setattr('sys.stdin', stdin)
    assert play_game() == 'Player A'
    assert stdin.read() == '' # Check that all input was read

def test_play_game_interaction_win(monkeypatch):
    TOTAL_TURNS = 9
    TURNS_A_AND_B_PAIRS = 4

    headlines = mock_ui_fn(monkeypatch, 'display_headline')
    messages = mock_ui_fn(monkeypatch, 'display_message')
    # Uses the new 15x15 input list defined above
    prompts = mock_ui_fn(monkeypatch, 'prompt', inputs_game_win)

    play_game()

    expected_headlines = [HEADLINE_SIZE, HEADLINE_NAMES] + [HEADLINE_TURN] * TOTAL_TURNS + [HEADLINE_WIN]
    assert headlines == expected_headlines

    expected_messages = [message_turn('Player A', 'X'), message_turn('Player B', 'O')] * TURNS_A_AND_B_PAIRS + \
        [message_turn('Player A', 'X'), message_won('Player A')]
    assert messages == expected_messages

    expected_prompts = [prompt_size(True), prompt_size(False), prompt_name(True), prompt_name(False)] + \
        [PROMPT_TURN] * TOTAL_TURNS + [PROMPT_RETURN_MENU]
    assert prompts == expected_prompts


##########################  Remove function test, and customizable board size 10x10 ##########################
COLS_SM = '10'
ROWS_SM = '10'

draw_moves_100 = generate_safe_draw_moves(10)

# standard moves
M1_M4 = draw_moves_100[:4]

# 'replay' move
M4_REPLAY = draw_moves_100[3]

# The rest of the draw moves
M5_M100 = draw_moves_100[4:]

# Total moves provided: 4 + 1 (remove) + 1 (replay) + 96 (rest) = 102 inputs for moves
inputs_game_with_remove_draw = [
    COLS_SM, ROWS_SM, 'Player A', 'Player B'
] + M1_M4 + [
    '-1',           # remove
    M4_REPLAY,      # replay
] + M5_M100 + [
    '',
    ''
]

def test_play_game_with_remove_draw(monkeypatch):
    # Total inputs consumed: 4 (config) + 102 (moves + undo) + 1 (return) = 107
    stdin = io.StringIO('\n'.join(inputs_game_with_remove_draw))
    monkeypatch.setattr('sys.stdin', stdin)

    assert play_game_with_remove() == None

    assert stdin.read().strip() == ''


def test_play_game_with_remove_interaction_draw(monkeypatch):
    TOTAL_INTERACTIONS = 102

    headlines = mock_ui_fn(monkeypatch, 'display_headline')
    messages = mock_ui_fn(monkeypatch, 'display_message')
    prompts = mock_ui_fn(monkeypatch, 'prompt', inputs_game_with_remove_draw)

    play_game_with_remove()

    expected_headlines = [HEADLINE_SIZE, HEADLINE_NAMES] + \
                         [HEADLINE_TURN] * TOTAL_INTERACTIONS + \
                         [HEADLINE_DRAW]
    assert headlines == expected_headlines

    turn_sequence = [message_turn('Player A', 'X'), message_turn('Player B', 'O')]
    expected_messages = turn_sequence * 2 + [message_turn('Player A', 'X')] + [message_turn('Player B', 'O')] + \
                        turn_sequence * 48 + \
                        [MESSAGE_DRAW]
    assert messages == expected_messages

    # Correct way to construct the list:
    expected_prompts_list = [prompt_size(True), prompt_size(False), prompt_name(True), prompt_name(False)] + \
                            [PROMPT_TURN] * (TOTAL_INTERACTIONS ) + [PROMPT_RETURN_MENU]

    assert prompts == expected_prompts_list


inputs_game_with_remove_win = [
    '10', '10',
    'Player A', 'Player B',
    '5 5', '6 6',
    '5 6', '6 7',
    '1 1', '2 1',
    '-1',
    '-1',
    '5 7', '6 8',
    '5 8', '6 9',
    '5 9',
    '',
    ''
]

def test_play_game_with_remove_win(monkeypatch):
    stdin = io.StringIO('\n'.join(inputs_game_with_remove_win))
    monkeypatch.setattr('sys.stdin', stdin)
    assert play_game_with_remove() == 'Player A'
    assert stdin.read().strip() == '' # Use .strip() for robust EOF check


def test_play_game_with_remove_interaction_win(monkeypatch):
    TOTAL_INTERACTIONS = 13
    headlines = mock_ui_fn(monkeypatch, 'display_headline')
    messages = mock_ui_fn(monkeypatch, 'display_message')
    prompts = mock_ui_fn(monkeypatch, 'prompt', inputs_game_with_remove_win)

    play_game_with_remove()

    expected_headlines = [HEADLINE_SIZE, HEADLINE_NAMES] + \
                         [HEADLINE_TURN] * TOTAL_INTERACTIONS + \
                         [HEADLINE_WIN]
    assert headlines == expected_headlines

    expected_messages = [message_turn('Player A', 'X'), message_turn('Player B', 'O')] * 6 + \
                        [message_turn('Player A', 'X'), message_won('Player A')]
    assert messages == expected_messages

    expected_prompts_list = [prompt_size(True), prompt_size(False), prompt_name(True), prompt_name(False)] + \
                            [PROMPT_TURN] * (TOTAL_INTERACTIONS) + [PROMPT_RETURN_MENU]

    assert prompts == expected_prompts_list

##########################  END TO END TEST ##########################

def test_end_to_end(monkeypatch):
    # Winning sequence ons standard 15x15 Game
    # For this one we check A winning vertically
    MOVES_A_WINS = ['1 1', '2 1', '1 2', '2 2', '1 3', '2 3', '1 4', '2 4', '1 5']
    # B wins: 5 moves for A, 5 for B (2,1 to 2,5).
    MOVES_B_WINS = ['1 1', '2 1', '1 2', '2 2', '1 3', '2 3', '1 4', '2 4', '3 1', '2 5']

    # input stream
    inputs = [
        # Check Scoreboard (Empty at start)
        '4', '',

        # Standard mode (select 1), then A wins
        '1', 'Player A', 'Player B', *MOVES_A_WINS, '',

        # Check Scoreboard (A should be 1)
        '4', '',

        # Play Game 2 (Standard - Selection 1): Player A Wins again
        '1', 'Player A', 'Player B', *MOVES_A_WINS, '',

        # Check Scoreboard (A should be 2)
        '4', '',

        # Play Game 3 (Standard - Selection 1): Player B Wins
        '1', 'Player A', 'Player B', *MOVES_B_WINS, '',

        # Check Scoreboard (A=2, B=1)
        '4', '',

        # Exit
        '5'
    ]

    # Prepare the mock input stream
    stdin = io.StringIO('\n'.join(inputs))
    monkeypatch.setattr('sys.stdin', stdin)

    # Mock the scoreboard display to capture the results
    scoreboards = mock_ui_fn(monkeypatch, 'display_scoreboard')

    remove_file(SCOREBOARD_FILE)

    main()

    # We expect 4 calls to display_scoreboard
    assert scoreboards == [
        {},  # Initial (Empty)
        {'Player A': 1},  # After Game 1
        {'Player A': 2},  # After Game 2, A won 2 games
        {'Player A': 2, 'Player B': 1}  # After Game 3, A won 2 games, B only one
    ]

    # Verify Persistence
    scoreboards.clear()

    # New input stream just to check scoreboard and exit
    stdin_check = io.StringIO('4\n\n5')
    monkeypatch.setattr('sys.stdin', stdin_check)

    main()

    # Verify it loaded the data from the file created in the previous run
    assert scoreboards == [{'Player A': 2, 'Player B': 1}]

    # Verify Cleanup
    scoreboards.clear()
    remove_file(SCOREBOARD_FILE)  # Delete the file

    # New input stream to check empty scoreboard
    stdin_empty = io.StringIO('4\n\n5')
    monkeypatch.setattr('sys.stdin', stdin_empty)

    main()

    # Verify it handles missing file correctly (empty dict)
    assert scoreboards == [{}]

    # Final Cleanup
    remove_file(SCOREBOARD_FILE)