"use strict";

/*
 * The templates should be kept in sync with:
 *
 * - templates/reviews/changedesc_commit_list.html
 * - templates/reviews/commit_list_field.html
 *
 * so that they render items identically.
 */
(function () {
  const itemTemplate = _.template("<tr<% if (rowClass) { %> class=\"<%- rowClass %>\"<% } %>>\n <% if (showHistorySymbol) { %>\n  <td class=\"marker\">\n   <%- historyDiffEntry.getSymbol() %>\n  </td>\n <% } else if (showInterCommitDiffControls) { %>\n  <td class=\"select-base\">\n   <input type=\"radio\"\n          class=\"base-commit-selector\"\n          name=\"base-commit-id\"\n          <% if (baseSelected) { %>checked<% } %>\n          <% if (baseDisabled) { %>disabled<% } %>\n          value=\"<%- commit.id %>\">\n  </td>\n  <td class=\"select-tip\">\n   <input type=\"radio\"\n          class=\"tip-commit-selector\"\n          name=\"tip-commit-id\"\n          <% if (tipSelected) { %>checked<% } %>\n          <% if (tipDisabled) { %>disabled<% } %>\n          value=\"<%- commit.id %>\">\n  </td>\n <% } %>\n <% if (showExpandCollapse) { %>\n  <td>\n   <% if (commit && commit.hasSummary()) { %>\n    <a href=\"#\"\n       class=\"expand-commit-message\"\n       data-commit-id=\"<%- commit.id %>\"\n       aria-role=\"button\">\n     <span class=\"fa fa-plus\" title=\"<%- expandText %>\"></span>\n    </a>\n   <% } %>\n  </td>\n <% } %>\n <td<% if (showHistorySymbol) { %> class=\"value\"<% } %>>\n  <% if (commit !== null) { %>\n   <pre><%- commit.get('summary') %></pre>\n  <% } %>\n </td>\n <td<% if (showHistorySymbol) { %> class=\"value\"<% } %>>\n  <% if (commit !== null) { %>\n   <%- commit.get('authorName') %>\n  <% } %>\n </td>\n</tr>");

  const headerTemplate = _.template("<thead>\n <tr>\n  <% if (showHistorySymbol) { %>\n   <th></th>\n  <% } else if (showInterCommitDiffControls) { %>\n   <th><%- firstText %></th>\n   <th><%- lastText %></th>\n  <% } %>\n  <th<% if (showExpandCollapse) { %> colspan=\"2\"<% } %>>\n   <%- summaryText %>\n   </th>\n  <th><%- authorText %></th>\n </tr>\n</thead>");

  const tableTemplate = _.template("<form>\n <table class=\"commit-list\">\n  <colgroup>\n   <% if (showHistorySymbol) { %>\n    <col>\n   <% } else if (showInterCommitDiffControls) { %>\n     <col>\n     <col>\n   <% } %>\n   <% if (showExpandCollapse) { %>\n    <col class=\"expand-collapse-control\">\n   <% } %>\n   <col>\n   <col>\n  </colgroup>\n </table>\n</form>");
  /**
   * A view for displaying a list of commits and their metadata.
   */


  RB.DiffCommitListView = Backbone.View.extend({
    events: {
      'change .base-commit-selector': '_onBaseChanged',
      'change .tip-commit-selector': '_onTipChanged',
      'click .collapse-commit-message': '_collapseCommitMessage',
      'click .expand-commit-message': '_expandCommitMessage'
    },

    /**
     * Initialize the view.
     *
     * Args:
     *     options (object):
     *         Options that control how this view behaves.
     *
     * Option Args:
     *     showInterCommitDiffControls (boolean):
     *         Whether or not to show interdiff controls.
     */
    initialize(options) {
      this.listenTo(this.model.get('commits'), 'reset', this.render);
      this._showInterCommitDiffControls = !!options.showInterCommitDiffControls;
      this._$baseSelectors = $();
      this._$tipSelectors = $();
    },

    /**
     * Render the view.
     *
     * Returns:
     *     RB.DiffCommitListView:
     *     This view, for chaining.
     */
    render() {
      const commits = this.model.get('commits');
      const isInterdiff = this.model.isInterdiff();
      const commonContext = {
        showExpandCollapse: commits.some(commit => commit.hasSummary()),
        showHistorySymbol: isInterdiff,
        showInterCommitDiffControls: this._showInterCommitDiffControls
      };
      const $content = $(tableTemplate(commonContext));
      const $table = $content.find('table').toggleClass('changed', isInterdiff).append(headerTemplate(_.extend({
        authorText: gettext("Author"),
        firstText: gettext("First"),
        lastText: gettext("Last"),
        summaryText: gettext("Summary")
      }, commonContext)));
      const $tbody = $('<tbody />');
      commonContext.expandText = gettext("Expand commit message.");

      if (isInterdiff) {
        this.model.get('historyDiff').each(historyDiffEntry => {
          const entryType = historyDiffEntry.get('entryType');
          let key;
          let rowClass;

          switch (entryType) {
            case RB.CommitHistoryDiffEntry.ADDED:
              rowClass = 'new-value';
              key = 'newCommitID';
              break;

            case RB.CommitHistoryDiffEntry.REMOVED:
              rowClass = 'old-value';
              key = 'oldCommitID';
              break;

            case RB.CommitHistoryDiffEntry.UNMODIFIED:
            case RB.CommitHistoryDiffEntry.MODIFIED:
              key = 'newCommitID';
              break;

            default:
              console.error('Invalid history entry type: %s', entryType);
              break;
          }

          const commit = commits.get(historyDiffEntry.get(key));
          $tbody.append(itemTemplate(_.extend({
            commit: commit,
            historyDiffEntry: historyDiffEntry,
            rowClass: rowClass
          }, commonContext)));
        });
      } else {
        commonContext.rowClass = '';
        const baseCommitID = this.model.get('baseCommitID');
        const tipCommitID = this.model.get('tipCommitID');
        const lastIndex = commits.size() - 1;
        const baseIndex = baseCommitID === null ? 0 : commits.indexOf(commits.getChild(commits.get(baseCommitID)));
        const tipIndex = tipCommitID === null ? lastIndex : commits.indexOf(commits.get(tipCommitID));
        commits.each((commit, i) => {
          $tbody.append(itemTemplate(_.extend({
            commit: commit,
            baseSelected: i === baseIndex,
            tipSelected: i === tipIndex,
            baseDisabled: i > tipIndex,
            tipDisabled: i < baseIndex
          }, commonContext)));
        });
      }

      $table.append($tbody);
      this.$el.empty().append($content);
      this._$baseSelectors = this.$('.base-commit-selector');
      this._$tipSelectors = this.$('.tip-commit-selector');
      return this;
    },

    /**
     * Handle the expand button being clicked.
     *
     * Args:
     *     e (jQuery.Event):
     *         The click event.
     */
    _expandCommitMessage(e) {
      e.preventDefault();
      e.stopPropagation();

      this._expandOrCollapse($(e.target).closest('.expand-commit-message'), true);
    },

    /**
     * Handle the collapse button being clicked.
     *
     * Args:
     *     e (jQuery.Event):
     *         The click event.
     */
    _collapseCommitMessage(e) {
      e.preventDefault();
      e.stopPropagation();

      this._expandOrCollapse($(e.target).closest('.collapse-commit-message'), false);
    },

    /**
     * Expand or collapse the commit message on the same row as the link.
     *
     * Args:
     *     $link (jQuery):
     *         The expand or collapse link that was clicked.
     *
     *     expand (boolean):
     *         Whether we are expanding (``true``) or collapsing (``false``).
     */
    _expandOrCollapse($link, expand) {
      const $icon = $link.find('.fa');
      const commitID = $link.data('commitId');
      const commit = this.model.get('commits').get(commitID);
      const newText = commit.get(expand ? 'commitMessage' : 'summary');
      $link.closest('tr').find('pre').text(newText);
      $link.attr('class', expand ? 'collapse-commit-message' : 'expand-commit-message');
      $icon.attr({
        'class': expand ? 'fa fa-minus' : 'fa fa-plus',
        'title': expand ? gettext("Collapse commit message.") : gettext("Expand commit message.")
      });
    },

    /**
     * Handle the base commit selection changing.
     *
     * The view's model will be updated to reflect this change.
     *
     * Args:
     *     e (jQuery.Event):
     *         The change event.
     */
    _onBaseChanged(e) {
      const $target = $(e.target);
      const commits = this.model.get('commits');
      const commit = commits.get(parseInt($target.val(), 10));
      const index = commits.indexOf(commit);
      this.model.set('baseCommitID', index === 0 ? null : commits.getParent(commit).id);

      this._$tipSelectors.slice(0, index).prop('disabled', true);

      this._$tipSelectors.slice(index).prop('disabled', false);
    },

    /**
     * Handle the tip commit selection changing.
     *
     * The view's model will be updated to reflect this change.
     *
     * Args:
     *     e (jQuery.Event):
     *         The change event.
     */
    _onTipChanged(e) {
      const $target = $(e.target);
      const commits = this.model.get('commits');
      const commit = commits.get(parseInt($target.val(), 10));
      const index = commits.indexOf(commit);
      this.model.set('tipCommitID', index === commits.size() - 1 ? null : commit.id);

      this._$baseSelectors.slice(0, index + 1).prop('disabled', false);

      this._$baseSelectors.slice(index + 1).prop('disabled', true);
    }

  });
})();

//# sourceMappingURL=diffCommitListView.js.map