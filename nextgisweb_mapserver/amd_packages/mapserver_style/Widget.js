/*global define*/
define([
    "dojo/_base/declare",
    "ngw/modelWidget/Widget",
    "ngw/modelWidget/ErrorDisplayMixin",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "dojo/text!./templates/Widget.html",
    // template
    "dijit/layout/BorderContainer",
    "dijit/form/Textarea",
    "ngw/form/CodeMirror",
    "dijit/form/Button",
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
        title: "Стиль MapServer",

        _getValueAttr: function () {
            return {
                xml: this.xml.get("value")
            };
        },

        _setValueAttr: function (value) {
            this.inherited(arguments);
            this.xml.set("value", value.xml);
        }
    });
});