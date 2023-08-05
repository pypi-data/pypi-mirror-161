"use strict";

/**
 * A view for pre-commit review request creation.
 *
 * This will guide users through several steps, depending on the requirements of
 * the repository.
 */
RB.PreCommitView = RB.UploadDiffView.extend({
  className: 'pre-commit',
  template: _.template("<div class=\"section-header\"><%- pendingChangeHeader %></div>\n<div class=\"tip\">\n <strong><%- tipHeader %></strong>\n <%= tip %>\n</div>\n<div class=\"input dnd\" id=\"prompt-for-diff\">\n <form>\n  <%= selectDiff %>\n </form>\n</div>\n<div class=\"input dnd\" id=\"prompt-for-parent-diff\">\n <form>\n  <div id=\"parent-diff-error-contents\" />\n  <%= selectParentDiff %>\n </form>\n <a href=\"#\" class=\"startover\"><%- startOver %></a>\n</div>\n<div class=\"input\" id=\"prompt-for-basedir\">\n <form id=\"basedir-form\">\n  <%- baseDir %>\n  <input id=\"basedir-input\" />\n  <input type=\"submit\" value=\"<%- ok %>\" />\n </form>\n <a href=\"#\" class=\"startover\"><%- startOver %></a>\n</div>\n<div class=\"input\" id=\"prompt-for-change-number\">\n <form id=\"changenum-form\">\n  <%- changeNum %>\n  <input type=\"number\" step=\"1\" id=\"changenum-input\" />\n  <input type=\"submit\" value=\"<%- ok %>\" />\n </form>\n <a href=\"#\" class=\"startover\"><%- startOver %></a>\n</div>\n<div class=\"input\" id=\"processing-diff\">\n <div class=\"spinner\"><span class=\"fa fa-spinner fa-pulse\"></div>\n</div>\n<div class=\"input\" id=\"uploading-diffs\">\n <div><span class=\"fa fa-spinner fa-pulse\"></div>\n</div>\n<div class=\"input\" id=\"error-indicator\">\n <div id=\"error-contents\" />\n <a href=\"#\" class=\"startover\"><%- startOver %></a>\n</div>")
});

//# sourceMappingURL=preCommitView.js.map