/* globals define, console */
define([
    "dojo/_base/declare",
    "dijit/layout/ContentPane",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "@nextgisweb/pyramid/i18n!",
    "ngw-resource/serialize",
    "dojo/text!./template/StyleWidget.hbs",
    // template
    "dijit/Dialog",
    "dijit/layout/BorderContainer",
    "dijit/form/Textarea",
    "ngw-pyramid/form/CodeMirror",
    "ngw-file-upload/Uploader",
    "dijit/Toolbar",
    "dijit/form/Button",
    "dojox/layout/TableContainer",
    "dijit/layout/TabContainer",
    "dijit/form/TextBox",
    "dijit/ColorPalette",
    "dijit/form/NumberSpinner"
], function (
    declare,
    ContentPane,
    _TemplatedMixin,
    _WidgetsInTemplateMixin,
    i18n,
    serialize,
    template
) {
    return declare([ContentPane, serialize.Mixin, _TemplatedMixin, _WidgetsInTemplateMixin], {
        templateString: i18n.renderTemplate(template),
        title: i18n.gettext("MapServer style"),
        activateOn: { create: true },
        prefix: "mapserver_style",

        postCreate: function () {
            this.inherited(arguments);

            if (this.composite.operation === "create") {
                var defaultValue = this.composite.config["ngw-mapserver/StyleWidget"].defaultValue;
                if (defaultValue){
                    this.xml.set("value", defaultValue);
                }
            }
        }
    });
});
