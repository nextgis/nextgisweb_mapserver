define([
    "dojo/_base/declare",
    "ngw/modelWidget/Widget",
    "ngw/modelWidget/ErrorDisplayMixin",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "dojo/text!./templates/Widget.html",
    "dojox/layout/TableContainer",
    "dijit/layout/TabContainer",
    "dijit/form/TextBox",
    "dijit/ColorPalette",
    "dijit/form/NumberSpinner"
], function (
    declare,
    Widget,
    ErrorDisplayMixin,
    _TemplatedMixin,
    _WidgetsInTemplateMixin,
    template
) {
    return declare([Widget, ErrorDisplayMixin, _TemplatedMixin, _WidgetsInTemplateMixin], {
        templateString: template,
        identity: "mapserver_style",
        title: "Стиль Mapserver",

        _getValueAttr: function () {
            return {
                opacity: this.wOpacity.get("value"),
                stroke_width: this.wStrokeWidth.get("value"),
                stroke_color: this.wStrokeColor.get("value").substring(1),
                fill_color: this.wFillColor.get("value").substring(1)
            };
        },

        _setValueAttr: function (value) {
            this.inherited(arguments);
            this.wOpacity.set("value", value.opacity);
            this.wStrokeWidth.set("value", value.stroke_width);
            this.wStrokeColor.set("value", '#' + value.stroke_color);
            this.wFillColor.set("value", '#' + value.fill_color);
        }
    });
})