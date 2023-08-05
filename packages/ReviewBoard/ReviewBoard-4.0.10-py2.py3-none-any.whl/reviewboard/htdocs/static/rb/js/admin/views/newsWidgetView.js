"use strict";

/**
 * A widget for displaying news items from an RSS feed.
 */
RB.Admin.NewsWidgetView = RB.Admin.WidgetView.extend({
  canReload: true,
  reloadTitle: gettext("Reload news posts"),
  itemsTemplate: _.template("<% _.each(items, function(item) { %>\n <a href=\"<%- item.url %>\" class=\"rb-c-admin-news-widget__item\"\n    target=\"_blank\">\n  <span class=\"rb-c-admin-news-widget__item-date\">\n   <%- item.date.format('MMM DD') %>\n  </span>\n  <span class=\"rb-c-admin-news-widget__item-title\">\n   <%- item.title %>\n  </span>\n </a>\n<% }) %>"),

  /**
   * Render the widget.
   *
   * This will set up the actions and begin loading the news.
   */
  renderWidget() {
    const model = this.model;
    this.addFooterAction({
      id: 'more-news',
      el: $('<a href="#" target="_blank">').text(gettext("More News")).attr('href', model.get('newsURL'))
    });
    const subscribeURL = this.model.get('subscribeURL');

    if (subscribeURL) {
      this.addFooterAction({
        id: 'subscribe',
        cssClasses: '-is-right',
        el: $('<a href="#" target="_blank">').text(gettext("Subscribe")).attr('href', subscribeURL)
      });
    }

    this.listenTo(model, 'loadingNews', () => this.setReloading(true));
    this.listenTo(model, 'change:newsItems', this._onNewsItemsChanged);
    model.loadNews();
  },

  /**
   * Reload the news posts.
   *
   * This is called in response to a user clicking the Reload action.
   */
  reloadContent() {
    this.model.loadNews();
  },

  /**
   * Handle changes to the list of loaded news items.
   *
   * If the list is empty, this will present an error pointing to the news
   * feed. Otherwise, it will render each of the news items.
   */
  _onNewsItemsChanged() {
    const items = this.model.get('newsItems');
    this.setReloading(false);

    if (items.length > 0) {
      this.$content.html(this.itemsTemplate({
        items: items
      }));
    } else {
      const $error = $('<p class="rb-c-admin-news-widget__error">').html(interpolate(gettext("There was an error loading the news. Please <a href=\"%s\">visit the news page</a> directly, or try again later."), [this.model.get('newsURL')]));
      this.$content.empty().append($error);
    }

    this.trigger('sizeChanged');
  }

});

//# sourceMappingURL=newsWidgetView.js.map