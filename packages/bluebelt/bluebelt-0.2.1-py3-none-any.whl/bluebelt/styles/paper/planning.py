import bluebelt.styles.defaults as defaults

# main plot | pyplot.plot
plot_quantity = {
    'color': defaults.black,
    'linestyle': 'solid',
    'linewidth': 1,
    'zorder': 90,
}
# main plot | pyplot.fill_between
fill_between_quantity = {
    'color': None,
    'hatch': '////',
    'linestyle': 'dashed',
    'linewidth': 0.5,
    'zorder': 50,
}

# main plot | pyplot.plot
plot_distribution = {
    'color': defaults.blue,
    'linestyle': 'solid',
    'linewidth': 1,
    'zorder': 89,
}

# main plot | pyplot.fill_between
fill_between_distribution = {
    'color': None,
    'edgecolor': defaults.blue,
    'hatch': '\\\\\\\\',
    'linestyle': 'dashed',
    'linewidth': 0.5,
    'zorder': 49,
}

plot_skills = {
    'color': defaults.green,
    'linestyle': 'solid',
    'linewidth': 1,
    'zorder': 88,
}
# main plot | pyplot.fill_between
fill_between_skills = {
    'color': None,
    'edgecolor': defaults.green,
    'hatch': '||||',
    'linestyle': 'dashed',
    'linewidth': 0.5,
    'zorder': 48,
}

# main plot | pyplot.plot
plot_qds = {
    'color': defaults.red,
    'linestyle': 'solid',
    'linewidth': 2,
    'zorder': 100,
}

#########################
# ease plot
#########################

# plot | bar
bar_border = {
    'facecolor': None,
    'edgecolor': defaults.black,
    'hatch': None,
    'linestyle': 'solid',
    'linewidth': 1,
    'zorder':  70,
}

bar_top = {
    'facecolor': None,
    'edgecolor': defaults.red,
    'hatch': '////',
    'linestyle': 'solid',
    'linewidth': 0.5,
    'zorder':  50,
}

bar_bottom = {
    'facecolor': None,
    'edgecolor': defaults.black,
    'hatch': '////',
    'linestyle': 'solid',
    'linewidth': 0.5,
    'zorder':  50,
}

bar_connectors = {
    'facecolor': None,
    'edgecolor': defaults.black,
    'hatch': None,
    'linestyle': 'dotted',
    'linewidth': 1,
}

# value text | pyplot.text
value_text = {
    'color': defaults.black,
    #'backgroundcolor': defaults.white,
    'ha': 'center',
    'va': 'center',
    'zorder': 90,
}

# plot title | pyplot.set_title
title = {
    'loc': 'left',
}