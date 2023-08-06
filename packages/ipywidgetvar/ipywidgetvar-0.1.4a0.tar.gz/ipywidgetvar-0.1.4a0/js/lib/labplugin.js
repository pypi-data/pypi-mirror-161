var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'ipywidgetvar:plugin',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'ipywidgetvar',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};

