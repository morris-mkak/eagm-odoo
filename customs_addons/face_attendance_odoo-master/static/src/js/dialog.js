/* global odoo, _ $ */
"use strict";

odoo.define("camera_dialog", function (require) {

    var core = require("web.core");
    var CameraPreviewDialog = require("camera_preview_dialog");
    var Widget = require("web.Widget");

    var QWeb = core.qweb;

    var CameraDialog = Widget.extend({
        init: function (parent)  {
            var self = this;

            self.parent = parent;
            self._opened = $.Deferred();
            self.localStream = undefined;
            self._super(parent);

            self.$modal = $(QWeb.render("CameraDialog", {
                title: "Take employee photo",
                self: self
            }));

            self.$modal.on("hidden.bs.modal", _.bind(self.destroy, self));

            self.$modal.find(".btn-take-photo").on("click", function (ev) {
                ev.preventDefault();

                CameraPreviewDialog.createCameraDialog(self, self.video);
            });
        },

        open: function ()  {
            var self = this;
            self.video = self.$modal.find("#video")[0];

            self.$modal.modal("show");
            self._opened.resolve();
            console.log(navigator)
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ video: true }).then(function (stream) {
                    self.video.src = window.URL.createObjectURL(stream);
                    self.video.play();
                    self.cameraStream = stream.getTracks()[0];
                });
            }
        },

        close: function ()  {
            this.$modal.modal("hide");
        },

        destroy: function (reason)  {
            $(".tooltip").remove();

            if (this.isDestroyed()) {
                return;
            }

            console.log("destroy");
            if (this.cameraStream) {
                console.log(this.cameraStream);
                this.cameraStream.stop();
            }
            this.trigger("closed", reason);
            this._super();
            this.$modal.modal("hide");
            this.$modal.remove();
            setTimeout(function () {
                var modals = $("body > .modal").filter(":visible");
                if(modals.length) {
                    modals.last().focus();
                    $("body").addClass("modal-open");
                }
            }, 0);
        }
    });

    CameraDialog.createCameraDialog = function (owner) {
        return new CameraDialog(owner).open();
    };

    return CameraDialog;
});