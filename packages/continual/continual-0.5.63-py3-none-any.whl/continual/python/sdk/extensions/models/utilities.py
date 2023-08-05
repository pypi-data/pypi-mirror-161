import logging


class Utilities:
    """
    Base class for utilities provided by the sdk such as a logger,
    artifact management etc.
    """

    def logger(self) -> logging.Logger:
        """
        Get a python logger instance
        to log in custom classes
        """
        raise NotImplementedError

    def save_artifact(self, source_path: str, description: str = None):
        """
        Save a custom artifact to source_path with optional description

        Parameters
        ----------
        source_path : str
            location of a file on disk
        description : str
            An optional descrption to associate with the saved artifact

        """
        raise NotImplementedError

    def save_pyplot_png(self, filename: str, display: bool):
        """
        Save the current figure in matplotlib as a png artifact
        Gets title and description from pyplot.

        Parameters
        ----------
        filename: str
            Name to save the png
        display: bool
            Whether to show the plot on the Continual UI
        """
        raise NotImplementedError

    def display_plot_from_file(self, title: str, source_path: str):
        """
        Display a plot image from disk on the Continual UI.

        Parameters
        ----------
        title: str
            Title for the plot
        source_path: str
            location of a file on disk
        """

        raise NotImplementedError
