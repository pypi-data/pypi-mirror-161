"use strict";

/**
 * A view for a committed revision.
 *
 * This is used specifically for new review request creation. A click on the
 * element will either navigate the page to the review request (if one exists),
 * or emit a 'create' event.
 */
RB.CommitView = Backbone.View.extend({
  className: 'commit',

  /**
   * Template for the main view.
   */
  template: _.template("<div class=\"progress\">\n <span class=\"fa fa-spinner fa-pulse\"></span>\n</div>\n<% if (accessible) { %>\n <div class=\"summary\">\n  <% if (reviewRequestURL) { %>\n   <span class=\"fa fa-arrow-circle-right jump-to-commit\"/>\n  <% } %>\n  <%- summary %>\n </div>\n<% } %>\n<div class=\"commit-info\">\n <span class=\"revision\">\n  <span class=\"fa fa-code-fork\"></span>\n  <%- revision %>\n  <% if (!accessible) { %>\n   <%- RB.CommitView.strings.COMMIT_NOT_ACCESSIBLE %>\n  <% } %>\n </span>\n <% if (accessible && author) { %>\n  <span class=\"author\">\n   <span class=\"fa fa-user\"></span>\n   <%- author %>\n  </span>\n <% } %>\n <% if (date) { %>\n  <span class=\"time\">\n   <span class=\"fa fa-clock-o\"></span>\n   <time class=\"timesince\" datetime=\"<%- date %>\"></time>\n  </span>\n <% } %>\n</div>"),

  /**
   * Template for the body content of the confirmation dialog.
   */
  _dialogBodyTemplate: _.template("<p><%- prefixText %></p>\n<p><code><%- commitID %>: <%- summary %></code></p>\n<p><%- suffixText %></p>"),
  events: {
    'click': '_onClick'
  },

  /**
   * Render the view.
   *
   * Returns:
   *     RB.CommitView:
   *     This object, for chaining.
   */
  render: function () {
    if (!this.model.get('accessible')) {
      this.$el.addClass('disabled');
    }

    let commitID = this.model.get('id');

    if (commitID.length === 40) {
      commitID = commitID.slice(0, 7);
    }

    if (this.model.get('reviewRequestURL')) {
      this.$el.addClass('has-review-request');
    }

    const date = this.model.get('date');
    this.$el.html(this.template(_.defaults({
      revision: commitID,
      author: this.model.get('authorName') || gettext("<unknown>"),
      date: date ? date.toISOString() : null
    }, this.model.attributes)));

    if (date) {
      this.$('.timesince').timesince();
    }

    return this;
  },

  /**
   * Handler for when the commit is clicked.
   *
   * Shows a confirmation dialog allowing the user to proceed or cancel.
   */
  _onClick() {
    let commitID = this.model.get('id');

    if (commitID.length > 7) {
      commitID = commitID.slice(0, 7);
    }

    const dialogView = new RB.DialogView({
      title: gettext("Create Review Request?"),
      body: this._dialogBodyTemplate({
        prefixText: gettext("You are creating a new review request from the following published commit:"),
        commitID: commitID,
        summary: this.model.get('summary'),
        suffixText: gettext("Are you sure you want to continue?")
      }),
      buttons: [{
        id: 'cancel',
        label: gettext("Cancel")
      }, {
        id: 'create',
        label: gettext("Create Review Request"),
        primary: true,
        onClick: this._createReviewRequest.bind(this)
      }]
    });
    dialogView.show();
  },

  /**
   * Create a new review request for the selected commit.
   *
   * If a review request already exists for this commit, redirect the browser
   * to it. If not, trigger the 'create' event.
   */
  _createReviewRequest() {
    if (this.model.get('accessible')) {
      const url = this.model.get('reviewRequestURL');

      if (url) {
        window.location = url;
      } else {
        this.model.trigger('create', this.model);
      }
    }
  },

  /**
   * Toggle a progress indicator on for this commit.
   */
  showProgress() {
    this.$('.progress').show();
  },

  /**
   * Toggle a progress indicator off for this commit.
   */
  cancelProgress() {
    this.$('.progress').hide();
  }

}, {
  strings: {
    COMMIT_NOT_ACCESSIBLE: gettext("(not accessible on this repository)")
  }
});

//# sourceMappingURL=commitView.js.map