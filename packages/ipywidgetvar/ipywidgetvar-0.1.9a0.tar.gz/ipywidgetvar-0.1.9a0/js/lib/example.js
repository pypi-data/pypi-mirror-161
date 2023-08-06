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
        _model_module_version : '0.1.9',
        _view_module_version : '0.1.9',
        value : 'IpywidgetVar!',
        id: 'id1',
        tojs: 'from python to js',
        topython: 'from js to python'
    })
});


// Custom View. Renders the widget model.
var IpywidgetVarView = widgets.DOMWidgetView.extend({
    // Defines how the widget gets rendered into the DOM
    render: function() {
        this.value_changed();
        this.id_changed();
        this.topython_changed()
        Object.defineProperty(this.el, 'tojs_callback_List', {
            value: [],
            configurable: true
            }
        );       
        Object.defineProperty(this.el, 'tojs_callback', {
            value: function(callback){
                this.el.tojs_callback_List.push(callback);
            }.bind(this),
            configurable: true
        });
        this.tojs_changed();

        // Observe changes in the value traitlet in Python, and define
        // a custom callback.
        this.model.on('change:value', this.value_changed, this);
        this.model.on('change:id', this.id_changed, this);
        this.model.on('change:tojs', this.tojs_changed, this);
        this.model.on('change:topython', this.topython_changed, this);
    },

    value_changed: function() {
        console.log("set value");
        // can be used as a communication status
        this.el.textContent = this.model.get('value');
    },

    id_changed: function(){
        console.log("set id");
        this.el.id = this.model.get('id');
        // attach function update to el
        // to use it
        // var myvar = document.querySelector("#id")
        // myvar.IpywidgetVarValue(val)
        Object.defineProperty(this.el, 'IpywidgetVarValue', {
                                        value: function(val){
                                                    this.model.set('value',val);
                                                    this.model.save_changes();
                                                    }.bind(this),
                                        configurable: true
                                    }
                            );   
    },
    tojs_changed: function(){
        // just register a callback with
        // var myvar = document.querySelector("#id")
        // myvar.tojs_callback(function(){...})
        for(var i =0; i<this.el.tojs_callback_List.length; i++){
            this.el.tojs_callback_List[i](JSON.parse(this.model.get('tojs')))
        }
    },
    topython_changed: function(){
        // var myvar = document.querySelector("#id")
        // myvar.IpywidgetVarTopython(val)
        Object.defineProperty(this.el, 'IpywidgetVarTopython', {
            value: function(val){
                        this.model.set('topython',JSON.stringify(val)); // js sends json
                        this.model.save_changes();
                        }.bind(this),
            configurable: true
           }
        );   
    },

});


module.exports = {
    IpywidgetVarModel: IpywidgetVarModel,
    IpywidgetVarView: IpywidgetVarView
};
