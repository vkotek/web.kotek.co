import operator, sqlite3
from bokeh.plotting import figure, output_file, save
import pandas, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Bokeh
from bokeh.plotting import figure, output_file, show
from bokeh.io import output_notebook
from bokeh.models import LinearAxis, Range1d, HoverTool

def load():
    """
    Loads all the words in set word list file. Calculates the score of each word.

    :return: dictionary with words and word scores
    """
    try:
        words = load_words_txt()
        words_scores = words_scored(words)
    except Exception as e:
        print(str(e))
    return {'words': words, 'words_scores': words_scores }

def load_words_txt():
    try:
        filename = "./plugins/en.txt"
        with open(filename, "r") as en_words:
            words = en_words.readlines()
            words = [word.strip() for word in words if len(word) < 9]
        return words
    except Exception as e:
        return str(e)

def word_score(word):
    letter_values = {
        'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1,
        'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1,
        's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10,
    }
    value = 0
    for letter in word:
        value += letter_values[letter]
    return value

def words_scored(words):
    words_dictionary = {}
    for word in words:
        words_dictionary[word] = word_score(word)
    return words_dictionary

def words_top(words):
    response = ['Highest Points', 'Shortest', 'Suggested']
    words = words.items()
    response[0] = sorted(words, key=operator.itemgetter(1),reverse=True)
    response[1] = sorted(words, key = lambda s: len(s[0]))
    response[2] = sorted(words, key = lambda s: s[1]/len(s[0]), reverse=True)
    return response

def words_shortest(words):
    return sorted(words, key = lambda s: len(s[0]))

def words_with(letter, length=None):
    words = load_words_txt()
    response = [word for word in load_words_txt if letter in word and validate(word)]
    if length:
        return [word for word in response if len(word) < length+1]
    return response

def words_end():
    return

def words_from(letters, length=None):
    words = load_words_txt()
    tried_words = []
    valid_words = []
    for word in words:
        tried_words.append(word)
        temp = list(letters)
        valid = True
        for character in word:
            if character in temp:
                temp.pop(temp.index(character))
            else:
                valid = False
                break
        if valid and validate(word) and length and len(word) < length+1:
            valid_words.append(word)
    return valid_words

def validate(word):

    # check if letter frequency is valid (e.g. Q used once)
    letters = list(word)
    if letters.count('z') > 1:
        return False
    if letters.count('q') > 1:
        return False
    if letters.count('x') > 1:
        return False
    if letters.count('k') > 1:
        return False
    return True

def get_games():

    try:
        conn = sqlite3.connect('./plugins/scrabble.db')
        c = conn.cursor()

        # Get all game data
        c.execute("""SELECT turns.game, games.date, MAX(turns.turn),
            	SUM(CASE WHEN PLAYER = 'VOJTA' THEN turns.score END) VO,
            	SUM(CASE WHEN PLAYER = 'VLADA' THEN turns.score END) VL
            FROM turns
            LEFT JOIN games
            ON turns.game = games.ID
            GROUP BY game""")
        data = c.fetchall()

        # Get overall statistics
        c.execute("""SELECT
                SUM(CASE WHEN PLAYER = 'VOJTA' THEN score END),
                SUM(CASE WHEN PLAYER = 'VLADA' THEN score END),
                MAX(CASE WHEN PLAYER = 'VOJTA' THEN score END),
                MAX(CASE WHEN PLAYER = 'VLADA' THEN score END),
                MAX(game)
            FROM turns""")
        d = c.fetchone()
        stats = {
            "sum_vojta": d[0], "sum_vlada": d[1],
            "max_turn_vojta": d[2], "max_turn_vlada": d[3],
            "games_played": d[4],
        }

        c.execute("""SELECT MAX(VKM), MAX(VLM), MIN(VKM), MIN(VLM)
            FROM
            	(SELECT
            		SUM(CASE WHEN PLAYER = 'VOJTA' THEN score END) VKM,
            		SUM(CASE WHEN PLAYER = 'VLADA' THEN score END) VLM
            	FROM turns
            	GROUP BY game)
        	""")
        d = c.fetchone()

        game_max = d[0] if d[0] > d[1] else d[1]
        game_min = d[2] if d[2] < d[3] else d[3]
        stats['max_game_vojta'] = d[0]
        stats['max_game_vlada'] = d[1]
        stats['min_game_vojta'] = d[2]
        stats['min_game_vlada'] = d[3]
        stats['avg_game_vojta'] = round(stats['sum_vojta'] / stats['games_played'])
        stats['avg_game_vlada'] = round(stats['sum_vlada'] / stats['games_played'])
        stats['max'] = game_max
        stats['min'] = game_min

        c.execute("""SELECT SUM(CASE WHEN VO > VL THEN 1 ELSE 0 END) AS VO,
                SUM(CASE WHEN VO < VL THEN 1 ELSE 0 END) AS VL,
                SUM(CASE WHEN VO == VL THEN 1 ELSE 0 END) AS TIE
            FROM ( SELECT
            SUM(CASE WHEN PLAYER = 'VOJTA' THEN score END) as VO,
            SUM(CASE WHEN PLAYER = 'VLADA' THEN score END) as VL
            FROM turns GROUP BY game )
        """)
        d = c.fetchone()

        stats['wins_vojta'] = d[0]
        stats['wins_vlada'] = d[1]
        stats['wins_tied'] = d[2]

        conn.close()
        result = {
            'data': data,
            'stats': stats
        }


        return result
    except Exception as e:
        return [['ERROR', str(e)]]

def get_game(game):

    try:
        conn = sqlite3.connect('./plugins/scrabble.db')
        c = conn.cursor()
        t = (game,)
        c.execute('SELECT turn, score FROM turns WHERE GAME = ? GROUP BY turn', t)
        c.execute("""SELECT turn,
            	SUM(CASE WHEN PLAYER = 'VOJTA' THEN score END) VO,
            	SUM(CASE WHEN PLAYER = 'VLADA' THEN score END) VA
            FROM turns
            WHERE game = ?
            GROUP BY turn;""", t)
        result = c.fetchall()
        conn.close()
        return result
    except Exception as e:
        return e

def get_turns():

    try:
        conn = sqlite3.connect('/home/vojtech/api.kotek.co/myapp/plugins/scrabble.db')
        c = conn.cursor()
        c.execute("""SELECT turn,
                SUM(CASE WHEN PLAYER = 'VOJTA' THEN score END) VO,
                SUM(CASE WHEN PLAYER = 'VLADA' THEN score END) VL
                FROM turns
                GROUP BY game, turn""")
        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        print("ERROR in 'get_turns()': {}".format(str(e)))
        return False

def get_last_game_id():

    try:
        conn = sqlite3.connect('/home/vojtech/api.kotek.co/myapp/plugins/scrabble.db')
        c = conn.cursor()
        c.execute("SELECT MAX(ID) FROM games")
        data = c.fetchone()
        conn.close()
        return int(data[0]) + 1
    except Exception as e:
        print(str(e))

def update_graphs():

    try:
        scrabbler.update_graph()
    except:
        print("Failed to update_graph()")
    try:
        scrabbler.update_histogram()
    except:
        print("Failed to update_histogram()")

def update_graph():

    data = scrabbler.get_games()['data']


    # Average for past X games:
    x = 10

    # Prepare table, add calculated columns
    df = pandas.DataFrame(data, columns=['ID','DATE','TURNS','VOJTA','VLADA'])
    df['DIFF'] = df['VOJTA'] - df['VLADA']
    df['VOJTA_MEAN'] = df['VOJTA'].rolling(x).mean().round()
    df['VLADA_MEAN'] = df['VLADA'].rolling(x).mean().round()
    df['VOJTA_PPT'] = (df['VOJTA'] / df['TURNS']).round(1)
    df['VLADA_PPT'] = (df['VLADA'] / df['TURNS']).round(1)
    df['VOJTA_TURN'] = df['VOJTA_PPT'].rolling(x).mean().round(1)
    df['VLADA_TURN'] = df['VLADA_PPT'].rolling(x).mean().round(1)
    df['VOJTA_CUM'] = df['VOJTA'].expanding().sum()
    df['VLADA_CUM'] = df['VLADA'].expanding().sum()
    df['TOTAL'] = df['VLADA'] + df['VOJTA']
    df['TOTAL_MEAN'] = df['TOTAL'].rolling(x).mean().round(1)

    # Set X Axis to game played
    x = df['ID']

    # output to static HTML file
    output_file("./static/media/scrabble.html")

    # create a new plot with a title and axis labels
    p = figure(title=None, x_axis_label='Game #', y_axis_label='Points per Game', plot_width=900, plot_height=500,
              toolbar_sticky=False, toolbar_location='above')

    # add a line renderer with legend and line thickness
    p.extra_y_ranges = {"foo": Range1d(start=0, end=100)}

    # Per Turn Data
    p.line(x, df['VOJTA_TURN'], legend="Vojta (Turn)", line_width=2, color='red', line_alpha=0.3, line_dash='dashed', y_range_name="foo")
    p.line(x, df['VLADA_TURN'], legend="Vlada (Turn)", line_width=2, color='blue', line_alpha=0.3, line_dash='dashed', y_range_name="foo")

    p.line(x, df['VOJTA_PPT'], legend="Vojta (Turn)", line_width=2, color='red', line_alpha=0.5, y_range_name="foo")
    p.line(x, df['VLADA_PPT'], legend="Vlada (Turn)", line_width=2, color='blue', line_alpha=0.5, y_range_name="foo")

    p.scatter(x, df['VOJTA_PPT'], legend="Vojta (Turn)", size=6, color='red', y_range_name="foo")
    p.scatter(x, df['VLADA_PPT'], legend="Vlada (Turn)", size=6, color='blue', y_range_name="foo")

    # Per Game Data
    p.line(x, df['VOJTA_MEAN'], legend="Vojta (Game)", line_width=2, color='green', line_alpha=0.3, line_dash='dashed')
    p.line(x, df['VLADA_MEAN'], legend="Vlada (Game)", line_width=2, color='purple', line_alpha=0.3, line_dash='dashed')

    p.line(x, df['VOJTA'], legend="Vojta (Game)", line_width=2, line_alpha=0.5, color='green')
    p.line(x, df['VLADA'], legend="Vlada (Game)", line_width=2, line_alpha=0.5, color='purple')
    p.line(x, df['TOTAL'], legend="Total (Game)", line_width=2, line_alpha=0.5, color='black')
    p.line(x, df['TOTAL_MEAN'], legend="Total (Game)", line_width=2, line_alpha=0.5, color='black', line_dash='dashed')

    p.scatter(x, df['VOJTA'], legend="Vojta (Game)", size=6, color='green')
    p.scatter(x, df['VLADA'], legend="Vlada (Game)", size=6, color='purple')

    p.add_layout(LinearAxis(y_range_name="foo", axis_label='Av. Points per Turn'), 'right')

    p.grid.grid_line_alpha = 0.7
    p.grid.grid_line_dash = [6, 4]
    p.xgrid.minor_grid_line_color = 'gray'
    p.xgrid.minor_grid_line_alpha = 0.1
    p.legend.location = 'top_left'

    # show the results
    save(p)
    print("Graph updated.")

def update_histogram():

    bins = 20
    data = scrabbler.get_turns()
    df  = pandas.DataFrame(data, columns=['turn', 'Vojta', 'Vlada'])
    x = df['Vojta'].plot.hist( bins=bins, alpha=0.5, figsize=(10,6),  legend=True)
    x = df['Vlada'].plot.hist( bins=bins, alpha=0.5, legend=True)
    fig = x.get_figure()
    plt.savefig("/home/vojtech/api.kotek.co/myapp/static/media/histogram.png")
    plt.close(fig)

    print("Histogram updated.")


# Insert functions

def data_parse(data):

    try:
        response = {}

        try:
            response['game_id'] = data.get('game_id')
            response['game_date'] = data.get('game_date')
            response['vlada'] = [x for x in data.getlist('vlada') if x != '']
            response['vojta'] = [x for x in data.getlist('vojta') if x != '']
        except:
            print("Error 123")

        if len(response['vlada']) != len(response['vojta']):
            print('Assymetrical game length.')
            return False

        print("RESPONSE:", response)
        return response

    except Exception as e:
        print("Failed at 'data_parse():", str(e))
        return False

def database_insert(data):
    # data = {'game_id': 'int', 'game_date': 'date', 'vlada': ['int','int'], 'vojta': ['int','int']}

    def database_prepare_turns(scores, game_id, player):
        try:
            turns = []
            for turn in range(0, len(scores)):
                row = (game_id, turn+1, player.upper(), scores[turn])
                turns.append(row)
            print(turns)
            return turns
        except Exception as e:
            print("Failed at 'database_prepare_turns()':", str(e))

    try:
        conn = sqlite3.connect('/home/vojtech/api.kotek.co/myapp/plugins/scrabble.db')
        c = conn.cursor()

        # Insert game to games table
        t = (data['game_id'], data['game_date'])
        print('Insert game:', t)
        c.execute("INSERT INTO games ('ID', 'DATE') VALUES (?,?)", t)

        # Prepare and insert turn data for each player.
        for player in ('vojta', 'vlada'):
            t = database_prepare_turns(data[player], data['game_id'], player)
            print("Inserting:", t)
            c.executemany("INSERT INTO 'turns' (GAME, TURN, PLAYER, SCORE) VALUES (?,?,?,?)", t)

        conn.commit()
        conn.close()
        print('Data successfully inserted into database.')
    except Exception as e:
        print("Failed at 'database_insert():'", str(e))
        print(data)
        return False

if __name__ == '__main__':
    scrabbler.update_graphs()
