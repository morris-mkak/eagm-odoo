/* global odoo, _, $ */
"use strict";

odoo.define("camera_preview_dialog", function (require) {

    var core = require("web.core");
    var Widget = require("web.Widget");

    var QWeb = core.qweb;

    var CameraPreviewDialog = Widget.extend({
        init: function (parent, video) {
            var self = this;

            self.parent = parent;
            self._opened = $.Deferred();
            self._super(parent);

            self.$modal = $(QWeb.render("CameraPreviewDialog", {
                title: "Preview photo",
                self: self
            }));

            var canvas = self.$modal.find("canvas")[0];
            var ctx = canvas.getContext("2d");

            ctx.drawImage(video, 0, 0, 640, 480);
            console.log(self);
            self.$modal.find(".btn-apply").on("click", function (ev) {
                ev.preventDefault();

                canvas.toBlob(function (blob) {
                    var data = canvas.toDataURL("image/jpg");
                    var photo_field = parent.parent.field_manager.fields.model_photo;

                    photo_field.on_file_uploaded(blob.size, "Photo-1.jpg", "image/jpg", data.split(",")[1]);
                }, "image/jpg");
            });

            self.$modal.on("hidden.bs.modal", _.bind(self.destroy, self));

        },

        open: function () {
            var self = this;
            self.$modal.modal("show");
            self._opened.resolve();


        },

        close: function () {
            this.$modal.modal("hide");
        },

        destroy: function (reason) {
            $(".tooltip").remove();

            if (this.isDestroyed()) {
                return;
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

    CameraPreviewDialog.createCameraDialog = function (owner, video) {
        return new CameraPreviewDialog(owner, video).open();
    };

    return CameraPreviewDialog;
});