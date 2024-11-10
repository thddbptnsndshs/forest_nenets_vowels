import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
from matplotlib import cm
from matplotlib.font_manager import fontManager, FontProperties

fontManager.addfont(os.getenv('FONT_PATH') or "/System/Library/Fonts/Supplemental/Times New Roman.ttf")
prop = FontProperties(fname=os.getenv('FONT_PATH'))
sns.set(font=prop.get_name())


class FNPlots:
    data: pd.DataFrame

    def __init__(self, data):
        self.data: pd.DataFrame = data
        print(self.data.word.unique())

    def formant_plot(
            self,
            save_fn: str = None,
            filter_query: str = '',
            **kwargs
    ):
        """
        Draw an F1--F2 plot from formant data
        :param save_fn: str, filename to save the plot, if None, plot is not saved
        :param filter_query: str, query to filter the data with pd.DataFrame.query()
        :param kwargs:
        """
        data = self.data.loc[self.data.query(filter_query).index]
        cmap = cm.get_cmap('Dark2')

        fig, ax = plt.subplots(figsize=(10, 8))

        x_name = 'F2'
        y_name = 'F1'

        x = data[x_name]
        y = data[y_name]

        ax.scatter(x, y, marker="")

        for v, color in zip(data.segment.unique(), cmap.colors):
            X = data[x_name].loc[data.segment == v]
            Y = data[y_name].loc[data.segment == v]
            for x, y in zip(X, Y):
                ax.annotate(v, (x, y), fontsize=14, color=color)

        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.set_xlabel(x_name, fontsize=16)
        ax.set_ylabel(y_name, fontsize=16)
        ax.yaxis.tick_right()
        ax.xaxis.tick_top()
        ax.yaxis.set_label_position("right")
        ax.xaxis.set_label_position("top")
        ax.set_title('Vowels, palatalized', fontsize=18)
        if save_fn:
            plt.savefig(save_fn)

    def duration_plot(
            self,
            save_fn: str = None,
            filter_query: str = '',
            barplot_args: dict = {},
            facetgrid_args=None,
            rename_columns_dict: dict = None,
            **kwargs
    ):
        """
        Draw an sns.FacetGrid of duration barplots from duration data
        :param save_fn: str, filename to save the plot, if None, plot is not saved
        :param filter_query: str, query to filter the data with pd.DataFrame.query()
        :param barplot_args: Dict, args and kwargs to be passed to sns.barplot
        :param facetgrid_args: Dict, kwargs to be passed to sns.FacetGrid
        :param rename_columns_dict: Dict, rename dict if some columns are to be renamed
        :param kwargs: optional kwargs (top, suptitle, dpi)
        """
        if facetgrid_args is None:
            facetgrid_args = {'height': 3, 'aspect': .55, 'ylim': (0, 140), }
        data = self.data.loc[self.data.query(filter_query).index]
        data['duration'] *= 1000
        if rename_columns_dict is not None:
            data.rename(columns=rename_columns_dict, inplace=True)
        plt.figure(figsize=kwargs.get('figsize') or (30, 30))
        g = sns.FacetGrid(data, margin_titles=True, sharey=True, **facetgrid_args)
        g.map(sns.barplot, *barplot_args['args'], **barplot_args['kwargs'])
        g.add_legend()
        if 'top' in kwargs:
            g.fig.subplots_adjust(top=kwargs.get('top'))  # adjust the Figure in rp
        if 'suptitle' in kwargs:
            g.fig.suptitle(kwargs.get('suptitle'))
        if save_fn:
            plt.savefig(save_fn, dpi=kwargs.get('dpi') or 400)

    def get_word_duration_table(
            self,
            word: str,
            round_factor: int = 5,
            columns_to_add=None
    ):
        """
        Make LaTeX table with mean and std of vowel durations
        :param word: str, word
        :param round_factor: int, factor to round the durations (as measured in seconds, NOT ms)
        :param columns_to_add: List[str], extra columns to include in the LaTeX table
        :return: str, LaTeX table
        """
        print(word)
        if columns_to_add is None:
            columns_to_add = ['position', 'stress']
        grpb_object = self.data.loc[(self.data.word == word)].groupby([
            'word', 'segment',
            'syllable_structure',
            'position', 'stress',
            'vowel', 'pre_schwa',
        ])['duration']
        mean, std, count = grpb_object.mean(), grpb_object.std(), grpb_object.count()
        table = mean.rename('mean, ms').to_frame() \
                    .join(std.rename('std, ms')) \
                    .round(round_factor) * 1000
        table = table.join(count.rename('count'))
        table = table.reset_index()[['word', 'segment', 'mean, ms', 'std, ms', 'count'] + columns_to_add]
        return table.to_latex(index=False)
