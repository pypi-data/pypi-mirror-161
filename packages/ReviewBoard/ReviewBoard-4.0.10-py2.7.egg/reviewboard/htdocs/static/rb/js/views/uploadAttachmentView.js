"use strict";

/**
 * A dialog for updating file attachments.
 */
RB.UploadAttachmentView = RB.DialogView.extend({
  className: 'upload-attachment',
  title: gettext("Upload File"),
  buttons: [{
    id: 'cancel',
    label: gettext("Cancel")
  }, {
    id: 'upload',
    label: gettext("Upload"),
    primary: true,
    disabled: true,
    onClick: 'send'
  }],
  template: _.template("<div class=\"formdlg\" style=\"width: 50em;\">\n <div class=\"error\" style=\"display: none;\"></div>\n <form encoding=\"multipart/form-data\" enctype=\"multipart/form-data\"\n       id=\"attachment-upload-form\">\n  <table>\n   <tbody>\n    <tr>\n     <td class=\"label\"><label><%- captionText %></label></td>\n     <td>\n      <input name=\"caption\" type=\"text\" value=\"<%- presetCaption %>\">\n     </td>\n     <td><ul class=\"errorlist\" style=\"display: none;\"></ul></td>\n    </tr>\n    <tr>\n     <td class=\"label\">\n      <label class=\"required\"><%- pathText %></label>\n     </td>\n     <td><input name=\"path\" id=\"path\" type=\"file\" class=\"js-path\"></td>\n     <td><ul class=\"errorlist\" style=\"display: none;\"></ul></td>\n    </tr>\n   </tbody>\n  </table>\n  <% if (attachmentHistoryID >= 0) { %>\n    <input type=\"hidden\" name=\"attachment_history\"\n           value=\"<%- attachmentHistoryID %>\" />\n  <% } %>\n </form>\n</div>"),
  events: _.extend({
    'change .js-path': 'updateUploadButtonEnabledState'
  }, RB.DialogView.prototype.events),

  /**
   * Initialize the view.
   *
   * Args:
   *     options (object):
   *         Options for the view.
   *
   * Option Args:
   *     attachmentHistoryID (number, optional):
   *         The ID of the attachment history to add to. This can be omitted
   *         if this is a new attachment (as opposed to updating an existing
   *         one).
   *
   *     presetCaption (string):
   *         The initial caption of the attachment.
   *
   *     reviewRequestEditor (RB.ReviewRequestEditor):
   *         The review request editor.
   */
  initialize: function () {
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

    _.defaults(options, {
      attachmentHistoryID: -1,
      presetCaption: ''
    });

    const body = this.template({
      attachmentHistoryID: options.attachmentHistoryID,
      captionText: gettext("Caption:"),
      pathText: gettext("Path:"),
      presetCaption: options.presetCaption
    });
    RB.DialogView.prototype.initialize.call(this, $.extend({
      body: body
    }, options));
  },

  /**
   * Create a file attachment on the review request.
   *
   * On success, the dialog will be closed.
   *
   * Otherwise, on error, the dialog will display the errors.
   */
  send() {
    const attrs = {
      attachmentHistoryID: this.options.attachmentHistoryID
    };
    this.options.reviewRequestEditor.createFileAttachment(attrs).save({
      form: this.$('#attachment-upload-form'),
      success: () => {
        // Close 'Add File' modal.
        this.remove();
      },
      error: function (model, xhr) {
        this.displayErrors($.parseJSON(xhr.responseText));
      }
    }, this);
  },

  /**
   * Display errors on the form.
   *
   * Args:
   *     rsp (object):
   *         The server response.
   */
  displayErrors(rsp) {
    const errorStr = rsp && rsp.err ? rsp.err.msg : gettext("Unknown Error");
    this.$('.error').text(errorStr).show();

    if (rsp && rsp.fields) {
      /* Invalid form data */
      const nameToRow = {
        caption: 0,
        path: 1
      };

      for (let fieldName in rsp.fields) {
        if (rsp.fields.hasOwnProperty(fieldName)) {
          const $errorList = this.$('.errorlist').css('display', 'block');
          const elIndex = nameToRow[fieldName];
          const errorListEl = $errorList[elIndex];

          for (let i = 0; i < rsp.fields[fieldName].length; i++) {
            $('<li>').html(rsp.fields[fieldName][i]).appendTo(errorListEl);
          }
        }
      }
    }
  },

  /**
   * Render the dialog.
   *
   * Returns:
   *     RB.UploadAttachmentView:
   *     This object, for chaining.
   */
  render() {
    RB.DialogView.prototype.render.call(this);
    this._$path = this.$('.js-path');
    this._$uploadBtn = this.$buttonsMap.upload;
    return this;
  },

  /**
   * Set the upload button to be clickable or not based on context.
   */
  updateUploadButtonEnabledState() {
    this._$uploadBtn.enable(this._$path.val());
  }

});

//# sourceMappingURL=uploadAttachmentView.js.map