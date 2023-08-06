"""
This package contains functions used for attaching different types of html
tables to allure report.
"""

from . import impl as _impl


def attach_table(df, allure_title='', caption='', attach_as_step=False):
    """
    Adds HTML table with a simple CSS
    configuration to allure report. This type of table can be used to show:
        - Numbers
        - Strings
        -
            HTML Paragraph code (See
            ``typhoon.test.reporting.tables.text_style``
            function)

            - Bold and Italic shape letters
            -
                Colors (See ``text_style`` docstring to
                be into all color options available)

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe with the table content.

    allure_title : string
        It is an empty string ("") by default. The title presented in the
        allure report.

    caption : string
        It is an empty string ("") by default. Table title attach directly to
        HTML code.

    attach_as_step: bool - default False
        If set to False, table is added at the end of the report, no matter when in test it is actually attached. This
        is default allure behaviour, all the attachments are added at the end of the report. To overwrite this
        behaviour and place attachment in the report chronologically in the moment when it is added, it must be
        added in the separate report step. This is achieved by setting this argument to True.

    Returns
    -------
    result: string
        HTML code of the table.

    Examples
    --------
    >>> from typhoon.test.reporting.tables import attach_table
    >>> import pandas as pd
    >>> import numpy as np
    >>> from pathlib import Path
    >>> df = pd.DataFrame(np.random.random(size=(10, 10)))
    >>> # attach table to report and return html code of it
    >>> html_code = attach_table(df, allure_title="Allure Table Title", caption="Allure Caption")
    >>> html_file = str(Path(__file__).parent / "attached_table.html")
    >>> with open(html_file, 'w') as fhtml:
    >>>     fhtml.write(html_code)
    """
    return _impl.attach_table(df, allure_title, caption, attach_as_step)


def attach_table_custom_colormap(df, threshold, allure_title='', caption='', colormaps=None, attach_as_step=False,
                                 center_at=None):
    """
    Adds HTML table with a specific colormap applied in the table's background to the allure report.
    Based on the minimum and maximum table values, as well as in
    threshold the table can have different green color tons
    (for good values - below the threshold) and red color
    tons (for bad values - above the threshold). These
    colors are set by default and can be changed by setting different values to the
    ``colormaps`` dictionary. For more information about
    colormaps access
    https://matplotlib.org/3.3.1/tutorials/colors/colormaps.html

    This type of table can be used to show data in different scenarios:
        - THD and wTHD
        - TRD
        - RMS Value
        - Power (Active, Reactive and Apparent)

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe with the table content.

    threshold : float-like
        The border value used to define if the table values pass or fail in
        the test. If the value is below defined value, the test case passed; otherwise, it failed.

    allure_title : string
        It is an empty string ("") by default. The title presented in the
        allure report.

    caption : string
        It is an empty string ("") by default. Table title attached directly to
        HTML code.

    colormaps : dict - defaults to None
        A dictionary with the colormap to color the table. If not specified, green color tons are used for passed cases,
        while red is used for failed.
        The ``pass`` key is for the colormap to the pass results and the ``fail`` key is for the
        colormap to the fail results. The colormaps available can be checked in
        matplotlib documentation.
        https://matplotlib.org/tutorials/colors/colormaps.html

    attach_as_step : bool - default False
        If set to False, table is added at the end of the report, no matter when in test it is actually attached. This
        is default allure behaviour, all the attachments are added at the end of the report. To overwrite this
        behaviour and place attachment in the report chronologically in the moment when it is added, it must be
        added in the separate report step. This is achieved by setting this argument to True.

    center_at : float-like
        It is a ``None`` by default. If None the table will be colorized as discussed in the introduction of the
        docstring. If set up with an integer or float value this will be the expected value and the ``threshold``
        option will configure a range of acceptable values below and above the ``center_at`` value. So the table
        values will pass if ``(center_at - threshold) < values < (center_at + threshold)``, out of this range the
        values will be considered failed.

    Returns
    -------
    result: string
        HTML code of the table.

    Examples
    --------
    >>> from typhoon.test.reporting.tables import attach_table_custom_colormap
    >>> import pandas as pd
    >>> from pathlib import Path
    >>> # filenames used to save the tables in html format
    >>> html_file = str(Path(__file__).parent / "attached_table_colormap.html")
    >>> html_file2 = str(Path(__file__).parent / "attached_table_colormap_new_colors.html")
    >>> html_file3 = str(Path(__file__).parent / "attached_table_colormap_center_at.html")
    >>> threshold = 220  # Threshold used to the first two tables
    >>> threshold3 = 10  # Threshold used to the third table
    >>> # Center valued is used to build the table and to render the third one
    >>> center_at_value = threshold
    >>> df_tmp = pd.DataFrame()
    >>> for i in range(11):
    >>>     for j in range(11):
    >>>         df_tmp.loc[i, j] = center_at_value + 2 * (i + j - (11 - 1))
    >>> df = pd.DataFrame(df_tmp, dtype=int)
    >>> # table 1 - attach html table with default colormap - green color for pass, red color for fail
    >>> html_code = attach_table_custom_colormap(
    >>>     df, threshold,
    >>>     allure_title='Green and red table',
    >>>     caption='Detailed table with green and red colors')
    >>> # table 1 - write resulting table code to html file
    >>> with open(html_file, 'w') as fhtml:
    >>>     fhtml.write(html_code)
    >>> # table 2 - create a second table, with changed colors - blue color for pass, orange for fail
    >>> html_code = attach_table_custom_colormap(
    >>>     df, threshold,
    >>>     allure_title='Blue and orange table',
    >>>     caption='Detailed table with blue and orange colors',
    >>>     colormaps={'pass': 'Blues', 'fail': 'Oranges'})
    >>> # table 2 - write resulting table code to html file
    >>> with open(html_file2, 'w') as fhtml:
    >>>     fhtml.write(html_code)
    >>> # table 3 - create a thirth table, with colormap application centered - green color for pass, red color for fail
    >>> html_code = attach_table_custom_colormap(
    >>>     df, threshold3,
    >>>     allure_title='Green and red center at table',
    >>>     caption='Detailed table with green and red colors center at',
    >>>     center_at=center_at_value)
    >>> # table 3 - write resulting table code to html file
    >>> with open(html_file3, 'w') as fhtml:
    >>>     fhtml.write(html_code)
    """
    return _impl.attach_table_custom_colormap(df, threshold, allure_title, caption, colormaps, attach_as_step,
                                              center_at)


def attach_table_custom_colormap_by_column(df, thresholds, allure_title='', caption='', colormaps=None,
                                           attach_as_step=False):
    """
    Adds html table to allure report in the same way as the ``attach_table_custom_colormap``
    with only difference that the threshold value is unique for each column; the user
    can repeat the threshold values, but threshold value is needed for every column.
    Same as there, if colormap is not specified, tons of green color are used for ``pass``,
    while red is used for ``fail`` cases.
    This  behaviour is overwritten by seting ``colormaps`` dictionary. For more information about
    colormaps access
    https://matplotlib.org/3.3.1/tutorials/colors/colormaps.html

    This type of table can be used to show for example:
        - Measurements in specific harmonic components

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe with the table content.

    threshold : dict
        Dictionary for setting the border values which define if test passed or failed, specific for every column.
        For this type of table, it's necessary to offer one threshold for each column in a dictionary.

    allure_title : string
        It is an empty string ("") by default.
        The title presented in the Allure-Report.

    caption : string
        It is an empty string ("") by default.
        Table title attached directly to HTML code.

    colormaps : dict
        It is None by default. As said earlier, if not specified, green color is used for ``pass``, while red is
        used for ``fail`` test cases.
        A dictionary with the colormap to color the table. The ``pass`` key is
        for the colormap to the pass results and the ``fail`` key is for the
        colormap to the fail results. The colormaps available can be checked in
        matplotlib documentation.
        https://matplotlib.org/tutorials/colors/colormaps.html

    attach_as_step: bool - default False
        If set to False, table is added at the end of the report, no matter when in test it is actually attached. This
        is default allure behaviour, all the attachments are added at the end of the report. To overwrite this
        behaviour and place attachment in the report chronologically in the moment when it is added, it must be
        added in the separate report step. This is achieved by setting this argument to True.

    Returns
    -------
    result: string
        HTML code of the table.

    Examples
    --------
    >>> from typhoon.test.reporting.tables import attach_table_custom_colormap_by_column
    >>> import pandas as pd
    >>> import numpy as np
    >>> from pathlib import Path
    >>> columns = np.linspace(0, 9, 10)
    >>> thresholds = {0: .1, 1: .2, 2: .3, 3: .4, 4: .5,
    >>>               5: .6, 6: .7, 7: .8, 8: .9, 9: 1.}
    >>> # create table for the harmonics from 0 to 9 with default colors
    >>> df = pd.DataFrame(np.random.random(size=(10, 10)), columns=columns)
    >>> html_code = attach_table_custom_colormap_by_column(
    >>>     df, thresholds,
    >>>     allure_title='Random Integer Values',
    >>>     caption='Harmonic table with Random Integer Values')
    >>> html_file = str(Path(__file__).parent / "harmonics_table.html")
    >>> with open(html_file, 'w') as fhtml:
    >>>     fhtml.write(html_code)
    >>> # create same  table with blue color for passed and orange color for failed cases
    >>> html_code = attach_table_custom_colormap_by_column(
    >>>     df, thresholds,
    >>>     allure_title='Random Integer Values',
    >>>     caption='Harmonic table with Random Integer Values',
    >>>     colormaps={'pass': 'Blues', 'fail': 'Oranges'})
    >>> html_file = str(Path(__file__).parent / "harmonics_table_new_colors.html")
    >>> with open(html_file, 'w') as fhtml:
    >>>     fhtml.write(html_code)
    """
    return _impl.attach_table_custom_colormap_by_column(df, thresholds, allure_title, caption, colormaps,
                                                        attach_as_step)


def text_style(paragraph, bold=False, italic=False, color="black"):
    """
    Set a string to be a paragraph with specifics HTML tags.

    Parameters
    ----------
    paragraph: string
        The text to be processed by applying the HTML tags.

    bold: bool
        It is False by default. If True, applies the tags
        ``<strong> ... </strong>`` on the paragraph.

    italic: bool
        It is False by default. If True, applies the tags ``<i> ... </i>``
        on the paragraph.

    color: string
        It is "black" by default,but other values can be selected: ``"blue"``, ``"green"``,
        ``"red"``, ``"orange"``, ``"gray"``, ``"purple"``, ``"pink"``. Also, it can be specified
        in a RGB style, like ``"rgb(96, 128, 0)"`` (Olive),
        ``"rgb(0, 255, 255)"`` (Cyan) and more. Check
        https://www.w3schools.com/colors/ to know more about HTML colors.

    Examples
    --------
    >>> import allure
    >>> from typhoon.test.reporting.tables import text_style
    >>> from pathlib import Path
    >>> html_file = str(Path(__file__).parent / 'tmp_text_style_docs.html')
    >>> dummy_text = [
    >>>     "Lorem ipsum dolor sit amet, consectetuer adipiscing elit.",
    >>>     "Aenean commodo ligula eget dolor. Aenean massa.",
    >>>     "Cum sociis natoque penatibus et magnis dis parturient.",
    >>>     "Donec quam felis, ultricies nec, pellentesque eu, pretiu.",
    >>>     "Nulla consequat massa quis enim.",
    >>>     "Donec pede justo, fringilla vel, aliquet nec, vulputate.",
    >>>     "In enim justo, rhoncus ut, imperdiet a, venenatis vitae.",
    >>>     "Nullam dictum felis eu pede mollis pretium.",
    >>>     "Integer tincidunt. Cras dapibus.",
    >>>     "Vivamus elementum semper nisi."
    >>> ]
    >>> dummy_styled_text = [
    >>>     text_style(dummy_text[0], bold=False, italic=False, color="black"),
    >>>     text_style(dummy_text[1], bold=True, italic=False, color="black"),
    >>>     text_style(dummy_text[2], bold=False, italic=True, color="black"),
    >>>     text_style(dummy_text[3], bold=False, italic=False, color="blue"),
    >>>     text_style(dummy_text[4], bold=True, italic=False, color="blue"),
    >>>     text_style(dummy_text[5], bold=False, italic=True, color="blue"),
    >>>     text_style(dummy_text[6], bold=True, italic=True, color="blue"),
    >>>     text_style(dummy_text[7], bold=True, italic=True, color="red"),
    >>>     text_style(dummy_text[8], bold=True, italic=False,
    >>>                color="rgb(96, 128, 0)"),
    >>> text_style(dummy_text[9], bold=False, italic=True,
    >>>            color="rgb(0, 255, 255)")
    >>> ]
    >>> with open(html_file, 'w') as fhtml:
    >>>     fhtml.writelines(dummy_styled_text)
    >>> string_list = "".join(text for text in dummy_styled_text)
    >>> allure.attach(string_list, "Dummy Text",
    >>>               allure.attachment_type.HTML)
    """
    return _impl.text_style(paragraph, bold=bold, italic=italic, color=color)
