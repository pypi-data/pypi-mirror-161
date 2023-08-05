"use strict";

/**
 * A view for updating the diff on a review request.
 */
RB.UpdateDiffView = RB.UploadDiffView.extend({
  className: 'update-diff',
  template: _.template("<div class=\"input dnd\" id=\"prompt-for-diff\">\n <form>\n  <%= selectDiff %>\n </form>\n</div>\n<div class=\"input dnd\" id=\"prompt-for-parent-diff\">\n <form>\n  <div id=\"parent-diff-error-contents\" />\n  <%= selectParentDiff %>\n </form>\n <a href=\"#\" class=\"startover\"><%- startOver %></a>\n</div>\n<div class=\"input\" id=\"prompt-for-basedir\">\n <form id=\"basedir-form\">\n  <%- baseDir %>\n  <input id=\"basedir-input\" />\n  <input type=\"submit\" value=\"<%- ok %>\" />\n </form>\n <a href=\"#\" class=\"startover\"><%- startOver %></a>\n</div>\n<div class=\"input\" id=\"processing-diff\">\n <div class=\"spinner\"><span class=\"fa fa-spinner fa-pulse\"></div>\n</div>\n<div class=\"input\" id=\"uploading-diffs\">\n <div class=\"spinner\"><span class=\"fa fa-spinner fa-pulse\"></div>\n</div>\n<div class=\"input\" id=\"error-indicator\">\n <div id=\"error-contents\" />\n <a href=\"#\" class=\"startover\"><%- startOver %></a>\n</div>"),

  /**
   * Render the view.
   *
   * Returns:
   *     RB.UpdateDiffView:
   *     This object, for chaining.
   */
  render() {
    RB.UploadDiffView.prototype.render.call(this);
    this.$el.modalBox({
      title: gettext("Update Diff"),
      buttons: [$('<input type="button" />').val(gettext("Cancel"))]
    });
    return this;
  }

});

//# sourceMappingURL=updateDiffView.js.map