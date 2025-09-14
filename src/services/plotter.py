from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def plot_dataframe(parent, df, x_col, y_col, kind="line"):
    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)

    if kind == "line":
        df.plot(x=x_col, y=y_col, ax=ax)
    elif kind == "bar":
        df.plot.bar(x=x_col, y=y_col, ax=ax)
    elif kind == "pie":
        df.set_index(x_col)[y_col].plot.pie(ax=ax, autopct='%1.1f%%')
    elif kind == "scatter":
        df.plot.scatter(x=x_col, y=y_col, ax=ax)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas.draw()
