/*global define, console, ngwConfig*/
define([
    "dojo/_base/declare",
    "dojo/aspect",
    "dojo/json",
    "dojo/request/xhr",
    "ngw/modelWidget/Widget",
    "ngw/modelWidget/ErrorDisplayMixin",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "dojo/text!./templates/Widget.html",
    // template
    "dijit/Dialog",
    "dijit/layout/BorderContainer",
    "dijit/form/Textarea",
    "ngw/form/CodeMirror",
    "ngw/form/Uploader",
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

        postCreate: function () {
            this.inherited(arguments);

            var widget = this;
            aspect.after(this.qmlUploader, 'uploadComplete', function (file) {
                widget.qmlUploadComplete(file);
            }, true);

            aspect.after(this.qmlUploader, 'uploadBegin', function () {
                widget.qmlUploadBegin();
            }, true);

        },

        _getValueAttr: function () {
            return {
                xml: this.xml.get("value")
            };
        },

        _setValueAttr: function (value) {
            this.inherited(arguments);
            this.xml.set("value", value.xml);
        },

        qmlShowDialog: function () {
            this.qmlDialog.show();
        },

        qmlUploadBegin: function () {
            this.qmlPreview.set('value', '');
        },

        qmlUploadComplete: function (file) {
            var widget = this;
            xhr.post(ngwConfig.applicationUrl + '/mapserver_style/qml', {
                data: json.stringify({file: file})
            }).then(
                function (data) {
                    widget.qmlPreview.set("value", data);
                },
                function () {
                    widget.qmlPreview.set(
                        "value",
                        '<!-- В ходе конвертации файла возникла ошибка -->'
                    );
                }
            ).then(undefined, function (err) { console.error(err); });
        },

        qmlAccept: function () {
            this.xml.set('value', this.qmlPreview.get('value'));
            this.qmlDialog.hide();
        }
    });
});