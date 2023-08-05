"use strict";

suite('rb/admin/models/NewsWidget', function () {
  let model;
  beforeEach(function () {
    model = new RB.Admin.NewsWidget({
      rssURL: 'http://example.com/news/rss'
    });
  });
  describe('Methods', function () {
    describe('loadNews', function () {
      it('Success', function () {
        function _loadNews(url, options) {
          expect(url).toBe('http://example.com/news/rss');
          const payload = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n\n<rss xmlns:atom=\"http://www.w3.org/2005/Atom\"\n     version=\"2.0\">\n <channel>\n  <title>Channel Name</title>\n  <link>http://example.com/news/</link>\n  <description>Channel description...</description>\n  <atom:link href=\"http://example.com/news/rss\"\n             rel=\"self\"></atom:link>\n  <language>en-us</language>\n  <lastBuildDate>Sun, 20 Oct 2019 17:26:32 -0700</lastBuildDate>\n  <item>\n   <title>Headline 6</title>\n   <pubDate>Sun, 20 Oct 2019 17:26:32 -0700</pubDate>\n   <link>http://example.com/news/post6</link>\n   <description>Brief summary of 6</description>\n   <author>user1@example.com</author>\n   <guid>http://example.com/news/post6</guid>\n  </item>\n  <item>\n   <title>Headline 5</title>\n   <pubDate>Tue, 01 Oct 2019 13:29:00 -0700</pubDate>\n   <link>http://example.com/news/post5</link>\n   <description>Brief summary of 5</description>\n   <author>user2@example.com</author>\n   <guid>http://example.com/news/post5</guid>\n  </item>\n  <item>\n   <title>Headline 4</title>\n   <pubDate>Thu, 26 Sep 2019 19:29:33 -0700</pubDate>\n   <link>http://example.com/news/post4</link>\n   <description>Brief summary of 4</description>\n   <author>user1@example.com</author>\n   <guid>http://example.com/news/post4</guid>\n  </item>\n  <item>\n   <title>Headline 3</title>\n   <pubDate>Sun, 08 Sep 2019 11:27:05 -0700</pubDate>\n   <link>http://example.com/news/post3</link>\n   <description>Brief summary of 3</description>\n   <author>user2@example.com</author>\n   <guid>http://example.com/news/post3</guid>\n  </item>\n  <item>\n   <title>Headline 2</title>\n   <pubDate>Fri, 30 Aug 2019 23:15:01 -0700</pubDate>\n   <link>http://example.com/news/post2</link>\n   <description>Brief summary of 2</description>\n   <author>user1@example.com</author>\n   <guid>http://example.com/news/post2</guid>\n  </item>\n  <item>\n   <title>Headline 1</title>\n   <pubDate>Thu, 29 Aug 2019 14:30:00 -0700</pubDate>\n   <link>http://example.com/news/post1</link>\n   <description>Brief summary of 1</description>\n   <author>user2@example.com</author>\n   <guid>http://example.com/news/post1</guid>\n  </item>\n </channel>\n</rss>";
          const parser = new DOMParser();
          options.success(parser.parseFromString(payload, 'application/xml'));
        }

        const loadingNewsEventHandler = jasmine.createSpy();
        spyOn($, 'ajax').and.callFake(_loadNews);
        model.on('loadingNews', loadingNewsEventHandler);
        model.loadNews();
        expect(loadingNewsEventHandler).toHaveBeenCalled();
        expect($.ajax).toHaveBeenCalled();
        const newsItems = model.get('newsItems');
        expect(newsItems.length).toBe(5);
        let newsItem = newsItems[0];
        expect(newsItem.date.isSame(Date.UTC(2019, 9, 21, 0, 26, 32))).toBeTrue();
        expect(newsItem.title).toBe('Headline 6');
        expect(newsItem.url).toBe('http://example.com/news/post6');
        newsItem = newsItems[1];
        expect(newsItem.date.isSame(Date.UTC(2019, 9, 1, 20, 29, 0))).toBeTrue();
        expect(newsItem.title).toBe('Headline 5');
        expect(newsItem.url).toBe('http://example.com/news/post5');
        newsItem = newsItems[2];
        expect(newsItem.date.isSame(Date.UTC(2019, 8, 27, 2, 29, 33))).toBeTrue();
        expect(newsItem.title).toBe('Headline 4');
        expect(newsItem.url).toBe('http://example.com/news/post4');
        newsItem = newsItems[3];
        expect(newsItem.date.isSame(Date.UTC(2019, 8, 8, 18, 27, 5))).toBeTrue();
        expect(newsItem.title).toBe('Headline 3');
        expect(newsItem.url).toBe('http://example.com/news/post3');
        newsItem = newsItems[4];
        expect(newsItem.date.isSame(Date.UTC(2019, 7, 31, 6, 15, 1))).toBeTrue();
        expect(newsItem.title).toBe('Headline 2');
        expect(newsItem.url).toBe('http://example.com/news/post2');
      });
      it('Error loading feed', function () {
        function _loadNews(url, options) {
          expect(url).toBe('http://example.com/news/rss');
          options.error();
        }

        const loadingNewsEventHandler = jasmine.createSpy();
        spyOn($, 'ajax').and.callFake(_loadNews);
        model.on('loadingNews', loadingNewsEventHandler);
        model.loadNews();
        expect(loadingNewsEventHandler).toHaveBeenCalled();
        expect($.ajax).toHaveBeenCalled();
        const newsItems = model.get('newsItems');
        expect(newsItems.length).toBe(0);
      });
    });
  });
});

//# sourceMappingURL=newsWidgetModelTests.js.map