/* globals define, console */
define([
    "dojo/_base/declare",
    "dojo/aspect",
    "dojo/json",
    "dojo/request/xhr",
    "dijit/layout/ContentPane",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "ngw/route",
    "ngw-pyramid/i18n!mapserver",
    "ngw-pyramid/hbs-i18n",
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
    aspect,
    json,
    xhr,
    ContentPane,
    _TemplatedMixin,
    _WidgetsInTemplateMixin,
    route,
    i18n,
    hbsI18n,
    serialize,
    template
) {
    return declare([ContentPane, serialize.Mixin, _TemplatedMixin, _WidgetsInTemplateMixin], {
        templateString: hbsI18n(template, i18n),
        prefix: "mapserver_style",
        title: "MapServer",

        postCreate: function () {
            this.inherited(arguments);

            var widget = this;
            aspect.after(this.qmlUploader, "uploadComplete", function (file) {
                widget.qmlUploadComplete(file);
            }, true);

            aspect.after(this.qmlUploader, "uploadBegin", function () {
                widget.qmlUploadBegin();
            }, true);

            if (this.composite.operation === "create" && this.composite.config["ngw-mapserver/StyleWidget"].defaultValue) {
                this.xml.set("value", this.composite.config["ngw-mapserver/StyleWidget"].defaultValue);
            }
        },

        qmlShowDialog: function () {
            this.qmlDialog.show();
        },

        qmlUploadBegin: function () {
            this.qmlPreview.set("value", "");
        },

        qmlUploadComplete: function (file) {
            var widget = this;
            xhr.post(route.mapserver.qml_transform(), {
                data: json.stringify({file: file})
            }).then(
                function (data) { widget.qmlPreview.set("value", data); },
                function () { widget.qmlPreview.set("value", i18n.gettext("<!-- An unknown error occurred during the file conversion -->")); }
            ).then(undefined, function (err) { console.error(err); });
        },

        qmlAccept: function () {
            this.xml.set("value", this.qmlPreview.get("value"));
            this.qmlDialog.hide();
        }
    });
});
