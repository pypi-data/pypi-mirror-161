"use strict";

suite('rb/admin/views/InlineFormGroupView', function () {
  const inlineTemplate = _.template("<div class=\"rb-c-admin-form-inline <%- classes || '' %>\">\n <h3 class=\"rb-c-admin-form-inline__title\">\n  <span class=\"rb-c-admin-form-inline__title-prefix\"></span>\n  <span class=\"rb-c-admin-form-inline__title-object\"></span>\n  <span class=\"rb-c-admin-form-inline__title-index\"></span>\n  <span class=\"rb-c-admin-form-inline__actions\">\n   <span class=\"rb-c-admin-form-inline__delete-action\"></span>\n  </span>\n </h3>\n <fieldset>\n  <div>\n   <label for=\"myprefix-<%- index %>-foo\"></label>\n   <input id=\"myprefix-<%- index %>-foo\"\n          name=\"myprefix-<%- index %>-foo\">\n  </div>\n  <div>\n   <label for=\"myprefix-<%- index %>-bar\"></label>\n   <input id=\"myprefix-<%- index %>-bar\"\n          name=\"myprefix-<%- index %>-bar\">\n  </div>\n </fieldset>\n</div>");

  const template = _.template("<div class=\"rb-c-admin-form-inline-group\">\n <h2 class=\"rb-c-admin-form-inline-group__title\"></h2>\n <div class=\"rb-c-admin-form-inline-group__inlines\">\n  <input type=\"hidden\"\n         id=\"id_myprefix-TOTAL_FORMS\"\n         name=\"myprefix-TOTAL_FORMS\"\n         value=\"<%- totalForms %>\">\n  <input type=\"hidden\"\n         id=\"id_myprefix-INITIAL_FORMS\"\n         name=\"myprefix-INITIAL_FORMS\"\n         value=\"<%- initialForms %>\">\n  <input type=\"hidden\"\n         id=\"id_myprefix-MIN_NUM_FORMS\"\n         name=\"myprefix-MIN_NUM_FORMS\"\n         value=\"<%- minNumForms %>\">\n  <input type=\"hidden\"\n         id=\"id_myprefix-MAX_NUM_FORMS\"\n         name=\"myprefix-MAX_NUM_FORMS\"\n         value=\"<%- maxNumForms %>\">\n\n  <% for (let i = 0; i < numInlines; i++) { %>\n   <%= inlineTemplate({\n       classes: '',\n       index: i\n   }) %>\n  <% } %>\n  <%= inlineTemplate({\n      classes: '-is-template',\n      index: '__prefix__'\n  }) %>\n </div>\n <div class=\"rb-c-admin-form-inline-group__actions\">\n  <a href=\"#\" class=\"rb-c-admin-form-inline-group__add-action\"></a>\n </div>\n</div>");

  let $el;
  let model;
  let view;

  function buildView(options) {
    $el = $(template(_.extend({
      initialForms: 0,
      inlineTemplate: inlineTemplate,
      maxNumForms: '',
      minNumForms: 0,
      numInlines: 0,
      totalForms: 0
    }, options))).appendTo($testsScratch);
    view = new RB.Admin.InlineFormGroupView({
      el: $el,
      model: model
    });
    view.render();
  }

  beforeEach(function () {
    model = new RB.Admin.InlineFormGroup({
      prefix: 'myprefix'
    });
  });
  describe('State', function () {
    it('Populated on render', function () {
      buildView({
        numInlines: 2,
        initialForms: 2,
        minNumForms: 1,
        maxNumForms: 5,
        totalForms: 2
      });
      expect($el.find('.rb-c-admin-form-inline').length).toBe(2);
      expect(view._$inlineTemplate.length).toBe(1);
      expect(view._$inlineTemplate.hasClass('-is-template')).toBeFalse();
      expect(model.get('initialInlines')).toBe(2);
      expect(model.get('maxInlines')).toBe(5);
      expect(model.get('minInlines')).toBe(1);
      expect(model.inlines.length).toBe(2);
      expect(view._inlineViews.length).toBe(2);
      let inline = model.inlines.at(0);
      expect(inline.get('index')).toBe(0);
      expect(inline.get('isInitial')).toBeTrue();
      expect(view._inlineViews[0].model).toBe(inline);
      inline = model.inlines.at(1);
      expect(inline.get('index')).toBe(1);
      expect(inline.get('isInitial')).toBeTrue();
      expect(view._inlineViews[1].model).toBe(inline);
    });
    it('Updated when inlines added', function () {
      buildView({
        numInlines: 1,
        initialForms: 1,
        totalForms: 1
      });
      const $totalForms = $el.find('#id_myprefix-TOTAL_FORMS');
      const $addButton = $el.find('.rb-c-admin-form-inline-group__add-action');
      expect($el.find('.rb-c-admin-form-inline').length).toBe(1);
      expect($totalForms.val()).toBe('1');
      $addButton.click();
      expect($el.find('.rb-c-admin-form-inline').length).toBe(2);
      expect($totalForms.val()).toBe('2');
      $addButton.click();
      expect($el.find('.rb-c-admin-form-inline').length).toBe(3);
      expect($totalForms.val()).toBe('3');
    });
    it('Updated when inlines added', function () {
      buildView({
        numInlines: 2,
        initialForms: 2,
        totalForms: 2
      });
      const $totalForms = $el.find('#id_myprefix-TOTAL_FORMS');
      expect(model.inlines.length).toBe(2);
      expect($totalForms.val()).toBe('2');
      model.inlines.at(0).destroy();
      const $inlines = $el.find('.rb-c-admin-form-inline');
      expect($inlines.length).toBe(1);
      expect(model.inlines.length).toBe(1);
      expect($totalForms.val()).toBe('1');
      expect($inlines[0].id).toBe('myprefix-0');
    });
  });
  describe('UI', function () {
    describe('Add Button', function () {
      let $addButton;
      beforeEach(function () {
        buildView({
          numInlines: 1,
          initialForms: 1,
          minNumForms: 0,
          maxNumForms: 3,
          totalForms: 1
        });
        $addButton = $el.find('.rb-c-admin-form-inline-group__add-action');
        expect($addButton.length).toBe(1);
      });
      it('When under limit', function () {
        expect($addButton.is(':visible')).toBeTrue();
        view.addInlineForm();
        expect($addButton.is(':visible')).toBeTrue();
      });
      it('When limit hit', function () {
        expect($addButton.is(':visible')).toBeTrue();
        view.addInlineForm();
        view.addInlineForm();
        expect($addButton.is(':visible')).toBeFalse();
      });
    });
  });
});

//# sourceMappingURL=inlineFormGroupViewTests.js.map