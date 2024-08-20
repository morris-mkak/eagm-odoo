/* global odoo */
odoo.define("my_custom_button", function (require) {
    "use strict";

    var core = require("web.core");
    var widget = require("web.form_widgets");
    var CameraDialog = require("camera_dialog");

    // var QWeb = core.qweb;

    var CameraButton = widget.WidgetButton.extend({
        on_click: function () {
            var self = this;

            CameraDialog.createCameraDialog(self);
        }
    });

    core.form_tag_registry.add("camera-button", CameraButton);

    return {
        CameraButton: CameraButton
    };
});