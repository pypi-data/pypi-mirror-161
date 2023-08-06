var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');

// See example.py for the kernel counterpart to this file.


// Custom Model. Custom widgets models must at least provide default values
// for model attributes, including
//
//  - `_view_name`
//  - `_view_module`
//  - `_view_module_version`
//
//  - `_model_name`
//  - `_model_module`
//  - `_model_module_version`
//
//  when different from the base class.

// When serialiazing the entire widget state for embedding, only values that
// differ from the defaults will be specified.
var IpywidgetVarModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name : 'IpywidgetVarModel',
        _view_name : 'IpywidgetVarView',
        _model_module : 'ipywidgetvar',
        _view_module : 'ipywidgetvar',
        _model_module_version : '0.1.2',
        _view_module_version : '0.1.2',
        value : 'IpywidgetVar!',
        id: 'id1'
    })
});


// Custom View. Renders the widget model.
var IpywidgetVarView = widgets.DOMWidgetView.extend({
    // Defines how the widget gets rendered into the DOM
    render: function() {
        this.value_changed();
        this.id_changed();

        // Observe changes in the value traitlet in Python, and define
        // a custom callback.
        this.model.on('change:value', this.value_changed, this);
        this.model.on('change:id', this.id_changed, this);
    },

    value_changed: function() {
        console.log("set value");
        this.el.textContent = this.model.get('value');
    },

    id_changed: function(){
        console.log("set id");
        this.el.id = this.model.get('id');
    }
});


module.exports = {
    IpywidgetVarModel: IpywidgetVarModel,
    IpywidgetVarView: IpywidgetVarView
};
