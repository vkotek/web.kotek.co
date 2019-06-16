import pandas, sqlite3
from bokeh.plotting import figure, show, output_file, save

def load_data():
    db = '/home/vojtech/scripts/botfinex/data.db'
    conn = sqlite3.connect(db)
    q = """SELECT * FROM history"""
    df = pandas.read_sql_query(q, conn)
    return df

def drawchart():

    output_file('/home/vojtech/api.kotek.co/myapp/static/graph.html')

    data = load_data()
    data['time'] = pandas.to_datetime(data['time'])

    plot = figure(x_axis_type="datetime",
                title = "BTC/USD",
               x_axis_label = "Time",
               x_range = [data['time'].iloc[-1]-pandas.to_timedelta(24,'h'),data['time'].iloc[-1]],
               y_axis_label = "Price (USD)",
               y_range = [data['price'][-1440:].min(), data['price'][-1440:].max()],
               plot_width = 900,
               plot_height = 600
               )

    plot.line(data['time'], data['price'], legend="Price", line_color="blue", line_width=2)
    plot.line(data['time'], data['max'], legend="Max", line_color="green", line_width=1)
    plot.line(data['time'], data['min'], legend="Min", line_color="red", line_width=1)
    plot.line(data['time'], data['buy'], legend="Buy", line_color="orange", line_width=1)
    plot.line(data['time'], data['sell'], legend="Sell", line_color="orange", line_width=1)

    save(plot)

    return True

if __name__ == "__main__":
    drawchart()
