from matplotlib import rc, rcParams


def set_xminor(b=True):
    rcParams["xtick.minor.bottom"] = b  ## draw x axis bottom minor ticks
    rcParams["xtick.minor.top"] = b
    rcParams["xtick.minor.visible"] = b
    return


def set_yminor(b=True):
    rcParams["ytick.minor.left"] = b  ## draw y axis left minor ticks
    rcParams["ytick.minor.right"] = b  ## draw y axis right minor ticks
    rcParams["ytick.minor.visible"] = b  ## visibility of minor ticks on y-axis
    return


def set_cham(fontsize=15, xminor=True, yminor=True, latex=True):

    if latex:
        rc('text', usetex=True)
        rcParams["mathtext.fontset"] = "cm"
        rcParams['text.latex.preamble'] = r"\usepackage{amsmath}"
    else:
        rc('text', usetex=False)
        rcParams["mathtext.fontset"] = "dejavusans"
        rcParams['text.latex.preamble'] = ""

    # font size
    rcParams["font.size"] = fontsize

    # xticks
    rcParams["xtick.top"] = True  ## draw ticks on the top side
    rcParams["xtick.bottom"] = True  ## draw ticks on the bottom side
    rcParams["xtick.major.size"] = 4  ## major tick size in points
    rcParams["xtick.minor.size"] = 2  ## minor tick size in points
    rcParams["xtick.major.width"] = 1.2  ## major tick width in points
    rcParams["xtick.direction"] = "in"  ## direction: {in, out, inout}

    # yticks
    rcParams["ytick.left"] = True  ## draw ticks on the left side
    rcParams["ytick.right"] = True  ## draw ticks on the right side
    rcParams["ytick.major.size"] = 4  ## major tick size in points
    rcParams["ytick.minor.size"] = 2  ## minor tick size in points
    rcParams["ytick.major.width"] = 1.2  ## major tick width in points
    rcParams["ytick.direction"] = "in"  ## direction: {in, out, inout}

    set_xminor(xminor)
    set_yminor(yminor)
    return

# capture cursor position ===============

# ref:
# https://matplotlib.org/stable/users/event_handling.html

# import matplotlib.pylab as plt
# import numpy as np
#
# f,a = plt.subplots()
# x = np.linspace(1,10,100)
# y = np.sin(x)
# a.plot(x,y)
# pos = []
# def onclick(event):
#     pos.append([event.xdata,event.ydata])
# f.canvas.mpl_connect('button_press_event', onclick)
# f.show()


def black_labels(labels, ind_black):
    # labels = ax.get_xticklabels()
    for i, label in enumerate(labels):
        if i in ind_black:
            label.set_color("white")
            label.set_weight(600)
            label.set_bbox(
                dict(
                    boxstyle="round,pad=.25",
                    linewidth=0.5,
                    facecolor="black",
                    edgecolor="black",
                )
            )
    return


if __name__ == "__main__":
    set_cham()
    set_xminor()
    set_yminor()
