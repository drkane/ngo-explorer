# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ChartJS(Component):
    """A ChartJS component.
ChartJS renders charts using the ChartJS library

Keyword arguments:
- id (string; optional): The ID used to identify this component in Dash callbacks
- type (a value equal to: 'scatter', 'bubble', 'polarArea', 'radar', 'horizontalBar', 'bar', 'line', 'pie', 'doughnut'; optional): Type of chart to draw
- data (dict; required): Object holding the data to be displayed in the chart
eg <https://www.chartjs.org/docs/latest/charts/line.html#data-structure> for line charts
- height (number; optional): Height of chart
- width (number; optional): Width of chart
- legend (dict; optional): Legend configuration
See <https://www.chartjs.org/docs/latest/configuration/legend.html>
- options (dict; optional): Configuration of the chart
See <https://www.chartjs.org/docs/latest/>
- redraw (boolean; optional): Whether to redraw chart when it changes

Available events: """
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, type=Component.UNDEFINED, data=Component.REQUIRED, height=Component.UNDEFINED, width=Component.UNDEFINED, legend=Component.UNDEFINED, options=Component.UNDEFINED, redraw=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'type', 'data', 'height', 'width', 'legend', 'options', 'redraw']
        self._type = 'ChartJS'
        self._namespace = 'dash_chartjs'
        self._valid_wildcard_attributes =            []
        self.available_events = []
        self.available_properties = ['id', 'type', 'data', 'height', 'width', 'legend', 'options', 'redraw']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['data']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(ChartJS, self).__init__(**args)

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('ChartJS(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'ChartJS(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
