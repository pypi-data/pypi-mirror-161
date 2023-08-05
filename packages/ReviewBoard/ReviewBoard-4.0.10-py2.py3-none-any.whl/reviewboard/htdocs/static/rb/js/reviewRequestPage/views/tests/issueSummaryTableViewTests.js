"use strict";

suite('rb/reviewRequestPage/views/IssueSummaryTable', function () {
  const issueSummaryTableTemplate = _.template("<div>\n <div class=\"rb-c-review-request-field-tabular\n             rb-c-issue-summary-table\">\n  <header class=\"rb-c-review-request-field-tabular__header\">\n   <div class=\"rb-c-review-request-field-tabular__filters\">\n    <select class=\"rb-c-issue-summary-table__reviewer-filter\">\n     <option value=\"all\"></option>\n    </select>\n   </div>\n   <ul class=\"rb-c-tabs\">\n    <li class=\"rb-c-tabs__tab -is-active\" data-issue-state=\"open\">\n     <label class=\"rb-c-tabs__tab-label\">\n      <span id=\"open-counter\"\n            class=\"rb-c-issue-summary-table__counter\">2</span>\n     </label>\n    </li>\n    <li class=\"rb-c-tabs__tab\" data-issue-state=\"verifying\">\n     <label class=\"rb-c-tabs__tab-label\">\n      <span id=\"verifying-counter\"\n            class=\"rb-c-issue-summary-table__counter\">3</span>\n     </label>\n    </li>\n    <li class=\"rb-c-tabs__tab\" data-issue-state=\"resolved\">\n     <label class=\"rb-c-tabs__tab-label\">\n      <span id=\"resolved-counter\"\n            class=\"rb-c-issue-summary-table__counter\">3</span>\n     </label>\n    </li>\n    <li class=\"rb-c-tabs__tab\" data-issue-state=\"dropped\">\n     <label class=\"rb-c-tabs__tab-label\">\n      <span id=\"dropped-counter\"\n            class=\"rb-c-issue-summary-table__counter\">1</span>\n     </label>\n    </li>\n    <li class=\"rb-c-tabs__tab\" data-issue-state=\"all\">\n     <label class=\"rb-c-tabs__tab-label\">\n      <span id=\"total-counter\"\n            class=\"rb-c-issue-summary-table__counter\">6</span>\n     </label>\n    </li>\n   </ul>\n  </header>\n  <table class=\"rb-c-review-request-field-tabular__data\">\n   <thead>\n    <tr>\n     <th class=\"-is-sortable\"></th>\n     <th class=\"-is-sortable\"></th>\n     <th class=\"-is-sortable\"></th>\n    </tr>\n   </thead>\n   <tbody>\n    <tr class=\"-is-resolved -is-hidden\"\n        data-issue-id=\"1\"\n        data-reviewer=\"user1\"\n        data-comment-type=\"diff\"\n        data-comment-href=\"#comment1\">\n     <td>\n      <span class=\"rb-icon rb-icon-issue-resolved\"></span>\n      <p>Resolved comment 1</p>\n     </td>\n     <td>user1</td>\n     <td>\n      <time class=\"timesince\" datetime=\"2017-02-01T20:30:00-07:00\">\n       February 1, 2017, 8:30 p.m.\n      </time>\n     </td>\n    </tr>\n    <tr class=\"-is-resolved -is-hidden\"\n        data-issue-id=\"2\"\n        data-reviewer=\"user2\"\n        data-comment-type=\"diff\"\n        data-comment-href=\"#comment2\">\n     <td>\n      <span class=\"rb-icon rb-icon-issue-resolved\"></span>\n      <p>Resolved comment 2</p>\n     </td>\n     <td>user2</td>\n     <td>\n      <time class=\"timesince\" datetime=\"2017-02-02T20:30:00-07:00\">\n       February 2, 2017, 8:30 p.m.\n      </time>\n     </td>\n    </tr>\n    <tr class=\"-is-resolved -is-hidden\"\n        data-issue-id=\"3\"\n        data-reviewer=\"user3\"\n        data-comment-type=\"diff\"\n        data-comment-href=\"#comment3\">\n     <td>\n      <span class=\"rb-icon rb-icon-issue-resolved\"></span>\n      <p>Resolved comment 3</p>\n     </td>\n     <td>user3</td>\n     <td>\n      <time class=\"timesince\" datetime=\"2017-02-03T20:30:00-07:00\">\n       February 3, 2017, 8:30 p.m.\n      </time>\n     </td>\n    </tr>\n    <tr class=\"-is-open\"\n        data-issue-id=\"4\"\n        data-reviewer=\"user1\"\n        data-comment-type=\"diff\"\n        data-comment-href=\"#comment4\">\n     <td>\n      <span class=\"rb-icon rb-icon-issue-open\"></span>\n      <p>Open comment 4</p>\n     </td>\n     <td>user1</td>\n     <td>\n      <time class=\"timesince\" datetime=\"2017-02-01T20:30:00-07:00\">\n       February 1, 2017, 8:30 p.m.\n      </time>\n     </td>\n    </tr>\n    <tr class=\"-is-open\"\n        data-issue-id=\"5\"\n        data-reviewer=\"user2\"\n        data-comment-type=\"diff\"\n        data-comment-href=\"#comment5\">\n     <td>\n      <span class=\"rb-icon rb-icon-issue-open\"></span>\n      <p>Open comment 5</p>\n     </td>\n     <td>user2</td>\n     <td>\n      <time class=\"timesince\" datetime=\"2017-02-02T20:30:00-07:00\">\n       February 2, 2017, 8:30 p.m.\n      </time>\n     </td>\n    </tr>\n    <tr class=\"-is-dropped -is-hidden\"\n        data-issue-id=\"6\"\n        data-reviewer=\"user1\"\n        data-comment-type=\"diff\"\n        data-comment-href=\"#comment6\">\n     <td>\n      <span class=\"rb-icon rb-icon-issue-dropped\"></span>\n      <p>Dropped comment 6</p>\n     </td>\n     <td>user1</td>\n     <td>\n      <time class=\"timesince\" datetime=\"2017-02-01T20:30:00-07:00\">\n       February 1, 2017, 8:30 p.m.\n      </time>\n     </td>\n    </tr>\n    <tr class=\"-is-verifying-dropped -is-hidden\"\n        data-issue-id=\"7\"\n        data-reviewer=\"user3\"\n        data-comment-type=\"diff\"\n        data-comment-href=\"#comment7\">\n     <td>\n      <span class=\"rb-icon rb-icon-issue-dropped\"></span>\n      <p>Verifying comment 7</p>\n     </td>\n     <td>user3</td>\n     <td>\n      <time class=\"timesince\" datetime=\"2017-02-03T18:30:00-07:00\">\n       February 3, 2017, 6:30 p.m.\n      </time>\n     </td>\n    </tr>\n    <tr class=\"-is-verifying-resolved -is-hidden\"\n        data-issue-id=\"8\"\n        data-reviewer=\"user2\"\n        data-comment-type=\"diff\"\n        data-comment-href=\"#comment8\">\n     <td>\n      <span class=\"rb-icon rb-icon-issue-dropped\"></span>\n      <p>Verifying comment 8 - resolved</p>\n     </td>\n     <td>user2</td>\n     <td>\n      <time class=\"timesince\" datetime=\"2017-02-04T20:30:00-07:00\">\n       February 4, 2017, 8:30 p.m.\n      </time>\n     </td>\n    </tr>\n   </tbody>\n  </table>\n </div>\n</div>");

  const TAB_SEL = '.rb-c-tabs__tab';
  const NO_ISSUES_SEL = '.rb-c-issue-summary-table__no-issues';
  const ISSUE_ROW_SEL = "tbody tr:not(".concat(NO_ISSUES_SEL, ")");
  const DESCRIPTION_HEADER_SEL = 'th:nth-child(1)';
  const REVIEWER_HEADER_SEL = 'th:nth-child(2)';
  const LAST_UPDATED_HEADER_SEL = 'th:nth-child(3)';
  const LAST_UPDATED_CELL_SEL = 'td:nth-child(3)';
  let view;

  function getTab(state) {
    return view.$("".concat(TAB_SEL, "[data-issue-state=\"").concat(state, "\"]"));
  }

  beforeEach(function () {
    view = new RB.ReviewRequestPage.IssueSummaryTableView({
      el: $(issueSummaryTableTemplate()),
      model: new RB.CommentIssueManager()
    });
    view.$el.appendTo($testsScratch);
  });
  describe('render', function () {
    it('Initial state', function () {
      view.render();
      expect(view.statusFilterState).toBe('open');
      expect(view.reviewerFilterState).toBe('all');
      expect(view.reviewerToSelectorMap).toEqual({
        all: '',
        user1: '[data-reviewer="user1"]',
        user2: '[data-reviewer="user2"]',
        user3: '[data-reviewer="user3"]'
      });

      const $reviewers = view._$reviewerFilter.children();

      expect($reviewers.length).toBe(4);
      expect($reviewers.eq(0).val()).toBe('all');
      expect($reviewers.eq(1).val()).toBe('user1');
      expect($reviewers.eq(2).val()).toBe('user2');
      expect($reviewers.eq(3).val()).toBe('user3');
    });
    it('With existing state', function () {
      view.render();
      view.statusFilterState = 'dropped';
      view.reviewerFilterState = 'user1';
      /* Fully replace the element, like when an update is applied. */

      const $oldEl = view.$el;
      view.setElement($(issueSummaryTableTemplate()));
      $oldEl.replaceWith(view.$el);
      view.render();
      expect(view.statusFilterState).toBe('dropped');
      expect(view.reviewerFilterState).toBe('user1');
      expect(view.reviewerToSelectorMap).toEqual({
        all: '',
        user1: '[data-reviewer="user1"]',
        user2: '[data-reviewer="user2"]',
        user3: '[data-reviewer="user3"]'
      });
      const $activeTab = view.$('.rb-c-tabs__tab.-is-active');
      expect($activeTab.length).toBe(1);
      expect($activeTab.data('issue-state')).toBe('dropped');
      expect($activeTab[0]).toBe(view._$currentTab[0]);
      const $reviewer = view.$('.rb-c-issue-summary-table__reviewer-filter');
      expect($reviewer.length).toBe(1);
      expect($reviewer[0]).toBe(view._$reviewerFilter[0]);
      expect($reviewer.val()).toBe('user1');
      const $issues = view.$el.find(ISSUE_ROW_SEL).not('.-is-hidden');
      expect($issues.length).toBe(1);
      const $issue = $issues.eq(0);
      expect($issue.hasClass('-is-dropped')).toBe(true);
      expect($issue.data('reviewer')).toBe('user1');
    });
  });
  describe('Filters', function () {
    describe('Reviewer filter', function () {
      describe('To all', function () {
        it('With issues', function () {
          view.render();

          view._$reviewerFilter.val('user1');

          view._$reviewerFilter.trigger('change');

          view._$reviewerFilter.val('all');

          view._$reviewerFilter.trigger('change');

          const $issues = view.$el.find(ISSUE_ROW_SEL).not('.-is-hidden');
          expect($issues.length).toBe(2);
          expect($issues.eq(0).data('issue-id')).toBe(4);
          expect($issues.eq(1).data('issue-id')).toBe(5);
        });
        it('Without issues', function () {
          view.$el.find(ISSUE_ROW_SEL).remove();
          view.render();

          view._$reviewerFilter.val('user1');

          view._$reviewerFilter.trigger('change');

          view._$reviewerFilter.val('all');

          view._$reviewerFilter.trigger('change');

          expect(view.$el.find(ISSUE_ROW_SEL).not('.-is-hidden').length).toBe(0);
          const $noIssues = view.$(NO_ISSUES_SEL);
          expect($noIssues.length).toBe(1);
        });
      });
      describe('To user', function () {
        it('With issues', function () {
          view.render();

          view._$reviewerFilter.val('user1');

          view._$reviewerFilter.trigger('change');

          const $issues = view.$el.find(ISSUE_ROW_SEL).not('.-is-hidden');
          expect($issues.length).toBe(1);
          expect($issues.eq(0).data('issue-id')).toBe(4);
        });
        describe('Without issues', function () {
          function testByUserWithoutIssues(state) {
            it("And filtered by ".concat(state, " issues"), function () {
              view.$el.find("".concat(ISSUE_ROW_SEL, ".-is-").concat(state) + '[data-reviewer="user1"]').remove();
              view.render();

              view._$reviewerFilter.val('user1');

              view._$reviewerFilter.trigger('change');

              const $tab = getTab(state);
              $tab.click();
              expect(view.$el.find(ISSUE_ROW_SEL).not('.-is-hidden').length).toBe(0);
              const $noIssues = view.$(NO_ISSUES_SEL);
              expect($noIssues.length).toBe(1);
              expect($noIssues.text().strip()).toBe("There are no ".concat(state, " issues from user1"));
            });
          }

          testByUserWithoutIssues('open');
          testByUserWithoutIssues('resolved');
          testByUserWithoutIssues('dropped');
        });
      });
    });
    describe('Status filters', function () {
      function testStatusFilters(options) {
        const state = options.state;
        describe(options.description, function () {
          it('With issues', function () {
            const expectedIDs = options.expectedIDs;
            view.render();
            const $tab = getTab(state);
            $tab.click();
            expect($tab.hasClass('-is-active')).toBe(true);
            const $allIssues = view.$el.find(ISSUE_ROW_SEL);
            const $issues = $allIssues.not('.-is-hidden');
            expect(view.$el.find("".concat(ISSUE_ROW_SEL, ".-is-hidden")).length).toBe($allIssues.length - expectedIDs.length);
            expect($issues.length).toBe(expectedIDs.length);
            expect(view.$(NO_ISSUES_SEL).length).toBe(0);

            for (let i = 0; i < expectedIDs.length; i++) {
              expect($issues.eq(i).data('issue-id')).toBe(expectedIDs[i]);
            }
          });
          it('Without issues', function () {
            const stateSel = view.stateToSelectorMap[state];
            view.$el.find("".concat(ISSUE_ROW_SEL).concat(stateSel)).remove();
            view.render();
            const $tab = getTab(state);
            $tab.click();
            expect($tab.hasClass('-is-active')).toBe(true);
            expect(view.$el.find(ISSUE_ROW_SEL).not('.-is-hidden').length).toBe(0);
            const $noIssues = view.$(NO_ISSUES_SEL);
            expect($noIssues.length).toBe(1);
            expect($noIssues.text().strip()).toBe(options.noIssuesText);
          });
        });
      }

      testStatusFilters({
        description: 'All',
        state: 'all',
        expectedIDs: [1, 2, 3, 4, 5, 6, 7, 8],
        noIssuesText: ''
      });
      testStatusFilters({
        description: 'Verifying',
        state: 'verifying',
        expectedIDs: [7, 8],
        noIssuesText: 'There are no issues waiting for verification'
      });
      testStatusFilters({
        description: 'Open',
        state: 'open',
        expectedIDs: [4, 5],
        noIssuesText: 'There are no open issues'
      });
      testStatusFilters({
        description: 'Resolved',
        state: 'resolved',
        expectedIDs: [1, 2, 3],
        noIssuesText: 'There are no resolved issues'
      });
      testStatusFilters({
        description: 'Dropped',
        state: 'dropped',
        expectedIDs: [6],
        noIssuesText: 'There are no dropped issues'
      });
    });
  });
  describe('Events', function () {
    it('"No Issues" row clicked', function () {
      const cb = jasmine.createSpy();
      view.$el.find(ISSUE_ROW_SEL).remove();
      view.render();
      view.on('issueClicked', cb);

      view._$reviewerFilter.val('user1');

      view._$reviewerFilter.trigger('change');

      view.$(NO_ISSUES_SEL).click();
      expect(cb).not.toHaveBeenCalled();
    });
    it('Issue clicked', function () {
      const cb = jasmine.createSpy();
      view.render();
      view.on('issueClicked', cb);
      view.commentIDToRowMap['4'].click();
      expect(cb).toHaveBeenCalledWith({
        commentType: 'diff',
        commentID: 4,
        commentURL: '#comment4'
      });
    });
    describe('Issue status updated', function () {
      const date = new Date(2017, 7, 6, 1, 4, 30);
      let $issue;
      let $icon;
      let comment;
      beforeEach(function () {
        comment = new RB.DiffComment({
          id: 4
        });
        view.render();
        expect(view.$('#resolved-counter').text()).toBe('3');
        expect(view.$('#open-counter').text()).toBe('2');
        expect(view.$('#dropped-counter').text()).toBe('1');
        expect(view.$('#total-counter').text()).toBe('6');
        $issue = view.commentIDToRowMap['4'];
        $icon = $issue.find('.rb-icon');
      });
      it('To dropped', function () {
        comment.set('issueStatus', 'dropped');
        view.model.trigger('issueStatusUpdated', comment, 'open', date);
        expect(view.$('#open-counter').text()).toBe('1');
        expect(view.$('#dropped-counter').text()).toBe('2');
        expect(view.$('#total-counter').text()).toBe('6');
        expect($icon.hasClass('rb-icon-issue-open')).toBe(false);
        expect($icon.hasClass('rb-icon-issue-dropped')).toBe(true);
      });
      it('To resolved', function () {
        comment.set('issueStatus', 'resolved');
        view.model.trigger('issueStatusUpdated', comment, 'open', date);
        expect(view.$('#resolved-counter').text()).toBe('4');
        expect(view.$('#open-counter').text()).toBe('1');
        expect(view.$('#total-counter').text()).toBe('6');
        expect($icon.hasClass('rb-icon-issue-open')).toBe(false);
        expect($icon.hasClass('rb-icon-issue-resolved')).toBe(true);
      });
      it('To open', function () {
        comment.set({
          issueStatus: 'open',
          id: 1
        });
        view.model.trigger('issueStatusUpdated', comment, 'resolved', date);
        $issue = view.commentIDToRowMap['1'];
        $icon = $issue.find('.rb-icon');
        expect(view.$('#resolved-counter').text()).toBe('2');
        expect(view.$('#open-counter').text()).toBe('3');
        expect(view.$('#total-counter').text()).toBe('6');
        expect($icon.hasClass('rb-icon-issue-resolved')).toBe(false);
        expect($icon.hasClass('rb-icon-issue-open')).toBe(true);
      });
      it('After re-renders', function () {
        view.render();
        view.render();
        comment.set('issueStatus', 'resolved');
        view.model.trigger('issueStatusUpdated', comment, 'open', date);
        expect(view.$('#resolved-counter').text()).toBe('4');
        expect(view.$('#open-counter').text()).toBe('1');
        expect(view.$('#total-counter').text()).toBe('6');
        expect($icon.hasClass('rb-icon-issue-open')).toBe(false);
        expect($icon.hasClass('rb-icon-issue-resolved')).toBe(true);
      });
      afterEach(function () {
        expect($issue.find("".concat(LAST_UPDATED_CELL_SEL, " time")).attr('datetime')).toBe(date.toISOString());
      });
    });
    describe('Header clicked', function () {
      function testHeaderSorting(options) {
        it(options.description, function () {
          view.render();
          const event = $.Event('click');
          event.shiftKey = !!options.shiftKey;
          const $header = view.$(options.headerSel);
          console.assert($header.length === 1);
          $header.trigger(event);
          const $issues = view.$(ISSUE_ROW_SEL);
          expect($issues.length).toBe(8);
          const foundIDs = [];

          for (let i = 0; i < $issues.length; i++) {
            foundIDs.push($issues.eq(i).data('issue-id'));
          }

          expect(foundIDs).toEqual(options.expectedIDs);
        });
      }

      describe('Ascending', function () {
        testHeaderSorting({
          description: 'Description',
          headerSel: DESCRIPTION_HEADER_SEL,
          expectedIDs: [6, 4, 5, 1, 2, 3, 7, 8]
        });
        testHeaderSorting({
          description: 'From',
          headerSel: REVIEWER_HEADER_SEL,
          expectedIDs: [1, 4, 6, 2, 5, 8, 3, 7]
        });
        testHeaderSorting({
          description: 'Last Updated',
          headerSel: LAST_UPDATED_HEADER_SEL,
          expectedIDs: [8, 3, 7, 2, 5, 1, 4, 6]
        });
      });
      describe('Descending', function () {
        testHeaderSorting({
          description: 'Description',
          headerSel: DESCRIPTION_HEADER_SEL,
          expectedIDs: [8, 7, 3, 2, 1, 5, 4, 6],
          shiftKey: true
        });
        testHeaderSorting({
          description: 'From',
          headerSel: REVIEWER_HEADER_SEL,
          expectedIDs: [3, 7, 2, 5, 8, 1, 4, 6],
          shiftKey: true
        });
        testHeaderSorting({
          description: 'Last Updated',
          headerSel: LAST_UPDATED_HEADER_SEL,
          expectedIDs: [1, 4, 6, 2, 5, 7, 3, 8],
          shiftKey: true
        });
      });
    });
  });
});

//# sourceMappingURL=issueSummaryTableViewTests.js.map