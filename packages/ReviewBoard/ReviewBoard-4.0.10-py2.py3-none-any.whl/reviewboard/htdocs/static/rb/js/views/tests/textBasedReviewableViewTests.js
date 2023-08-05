"use strict";

suite('rb/views/TextBasedReviewableView', function () {
  const template = "<div id=\"container\">\n <div class=\"text-review-ui-views\">\n  <ul>\n   <li class=\"active\" data-view-mode=\"rendered\">\n    <a href=\"#rendered\">Rendered</a>\n   </li>\n   <li data-view-mode=\"source\"><a href=\"#source\">Source</a></li>\n  </ul>\n </div>\n <table class=\"text-review-ui-rendered-table\"></table>\n <table class=\"text-review-ui-text-table\"></table>\n</div>";
  let $container;
  let reviewRequest;
  let model;
  let view;
  beforeEach(function () {
    $container = $(template).appendTo($testsScratch);
    reviewRequest = new RB.ReviewRequest({
      reviewURL: '/r/123/'
    });
    model = new RB.TextBasedReviewable({
      hasRenderedView: true,
      viewMode: 'rendered',
      fileAttachmentID: 456,
      reviewRequest: reviewRequest
    });
    view = new RB.TextBasedReviewableView({
      model: model,
      el: $container
    });
    /*
     * Disable the router so that the page doesn't change the URL on the
     * page while tests run.
     */

    spyOn(window.history, 'pushState');
    spyOn(window.history, 'replaceState');
    /*
     * Bypass all the actual history logic and get to the actual
     * router handler.
     */

    spyOn(Backbone.history, 'matchRoot').and.returnValue(true);
    spyOn(view.router, 'trigger').and.callThrough();
    spyOn(view.router, 'navigate').and.callFake((url, options) => {
      if (!options || options.trigger !== false) {
        Backbone.history.loadUrl(url);
      }
    });
    view.render();
  });
  afterEach(function () {
    view.remove();
    $container.remove();
    Backbone.history.stop();
  });
  it('Router switches view modes', function () {
    view.router.navigate('#rendered');
    expect(view.router.trigger).toHaveBeenCalledWith('route:viewMode', 'rendered', null, null);
    expect($container.find('.active').attr('data-view-mode')).toBe('rendered');
    expect(model.get('viewMode')).toBe('rendered');
    view.router.navigate('#source');
    expect(view.router.trigger).toHaveBeenCalledWith('route:viewMode', 'source', null, null);
    expect($container.find('.active').attr('data-view-mode')).toBe('source');
    expect(model.get('viewMode')).toBe('source');
    view.router.navigate('#rendered');
    expect(view.router.trigger).toHaveBeenCalledWith('route:viewMode', 'rendered', null, null);
    expect($container.find('.active').attr('data-view-mode')).toBe('rendered');
    expect(model.get('viewMode')).toBe('rendered');
  });
});

//# sourceMappingURL=textBasedReviewableViewTests.js.map