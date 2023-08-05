"use strict";

/**
 * A view for selecting a repository from a collection.
 */
RB.RepositorySelectionView = RB.CollectionView.extend({
  tagName: 'ul',
  className: 'rb-c-sidebar__items repository-selector',
  itemViewType: RB.RepositoryView,
  template: _.template("<li class=\"rb-c-sidebar__section -no-icons\">\n <header class=\"rb-c-sidebar__section-header\">\n  <%- repositoriesLabel %>\n </header>\n <ul class=\"rb-c-sidebar__items\">\n  <li class=\"rb-c-sidebar__item\">\n   <div class=\"rb-c-sidebar__item-label\">\n    <div class=\"rb-c-search-field\">\n     <span class=\"fa fa-search\"></span>\n     <input class=\"rb-c-search-field__input\"\n            placeholder=\"<%- filterLabel %>\" />\n    </div>\n   </div>\n  </li>\n </ul>\n <ul class=\"rb-c-sidebar__items\n            rb-c-new-review-request__repository-items\">\n</li>"),
  events: {
    'input .rb-c-search-field__input': '_onSearchChanged'
  },

  /**
   * Initialize the view.
   */
  initialize() {
    RB.CollectionView.prototype.initialize.apply(this, arguments);
    this._selected = null;
    this._searchActive = false;
    this._onSearchChanged = _.throttle(this._onSearchChanged.bind(this), 100);
    this.listenTo(this.collection, 'selected', this._onRepositorySelected);
  },

  /**
   * Render the view.
   *
   * Returns:
   *     RB.RepositorySelectionView:
   *     This object, for chaining.
   */
  render() {
    this.$el.html(this.template({
      repositoriesLabel: gettext("Repositories"),
      filterLabel: gettext("Filter")
    }));
    this.$container = this.$('.rb-c-new-review-request__repository-items');
    this._$searchBox = this.$('.rb-c-search-field__input');
    RB.CollectionView.prototype.render.apply(this, arguments);
    return this;
  },

  /**
   * Unselect a repository.
   */
  unselect() {
    this.views.forEach(view => {
      if (view.model === this._selected) {
        view.$el.removeClass('active');
      }
    });
    this._selected = null;
    this.trigger('selected', null);
  },

  /**
   * Callback for when an individual repository is selected.
   *
   * Ensures that the selected repository has the 'selected' class applied
   * (and no others do), and triggers the 'selected' event on the view.
   *
   * Args:
   *     item (RB.Repository):
   *         The selected repository;
   */
  _onRepositorySelected(item) {
    this._selected = item;
    this.views.forEach(view => {
      if (view.model === item) {
        view.$el.addClass('-is-active');
      } else {
        view.$el.removeClass('-is-active');
      }
    });
    this.trigger('selected', item);
  },

  /**
   * Callback for when the text in the search input changes.
   *
   * Filters the visible items.
   */
  _onSearchChanged() {
    const searchTerm = this._$searchBox.val().toLowerCase();

    console.log('search', searchTerm);
    this.collection.search(searchTerm);
  }

});

//# sourceMappingURL=repositorySelectionView.js.map