# CHANGELOG - FlexSearch Plugin

## v0.2 (March 21, 2025)

### New Features
- **Page Indexing**: Added support for indexing pages in addition to posts by removing the post-only restriction in build_index()
- **Configuration Options**: 
  - `FLEXSEARCH_INDEX_POSTS` (default: `True`) - Control whether posts are indexed
  - `FLEXSEARCH_INDEX_PAGES` (default: `False`) - Control whether pages are indexed
  - `FLEXSEARCH_INDEX_DRAFTS` (default: `False`) - Control whether draft content is indexed
- **Content Type Display**: Search results now display content type (post/page) with badges using CSS-styled spans
- **Enhanced Search Index**: 
  - Improved indexing to include title, content, and tags in search for better relevance
  - Created a multi-field search approach: `searchIndex.add(key, data[key].title + " " + data[key].content + data[key].tags + " " + data[key].content)`
  - Optional `FLEXSEARCH_OVERLAY` version available with advanced features (not enabled by default)
- **Basic UI Improvements**:
  - Better handling of search results with clear formatting and type badges
  - Support for both overlay and inline result display options
- **Keyboard Shortcuts**:
  - ESC key to close search overlay via global event listener
  - Enter key support for search submission with preventDefault() to avoid form submission
- **Tracking**: Added `?utm_source=internal_search` to result URLs for analytics tracking
- **Updated Libraries**: Using the latest FlexSearch v0.8.0 from CDN with minified bundle

### Improvements
- Added console logging for easier debugging
- Upgraded search index structure to include tags
- Better structured code with improved organization
- Two available search implementations:
  - Simple implementation (FLEXSEARCH_EXTEND) for reliable basic functionality
  - Advanced implementation (FLEXSEARCH_OVERLAY) available for future enhancements

### Bug Fixes
- Fixed issue where search only worked on post content, not pages by modifying the `if post.is_post` condition in build_index()
- Added specific null checks in JavaScript (`if (searchButton)`, `if (searchInput)`, etc.) to prevent errors when elements aren't found
- Resolved event handler issues by moving key functions outside the DOMContentLoaded scope
- Fixed closeSearch function accessibility by defining it globally in the window scope
- Improved error handling with console.log statements for debugging common issues
- Changed URL path in fetch() to `/search_index.json` (with leading slash) to ensure correct file loading regardless of current page URL

### Technical Changes
- Modified search index generation to remove the `post.is_post` filter that previously excluded pages from indexing
- Added support for tags in the search index: `item.meta('tags')` is now included in each indexed item
- Changed the search approach to concatenate multiple fields (`title + content + tags`) for more comprehensive search. This can be changed in `build_index` and in 
  ```javascript
  // Change here which keys should be used for the search index.
  searchIndex.add(key, data[key].title + " " + data[key].content + data[key].tags + " " + data[key].content);
  ```
- Implemented two distinct JavaScript implementations:
  - The default simple version (FLEXSEARCH_EXTEND) prioritizes reliability 
  - An optional advanced version (FLEXSEARCH_OVERLAY) with separate title/content indices
- Changed index URL from relative to absolute path (`/search_index.json`) to avoid path resolution issues
- Added content type field to search index to distinguish between posts and pages
- Commented out content indexing in plugin code but added comprehensive content indexing in JavaScript

### Documentation
- Added comprehensive documentation for new features
- Updated installation and configuration instructions
- Added code comments for better maintainability

---

## v0.1 (Initial Release)
- Basic search functionality for posts
- Support for triggering search via button click or Enter key
- Simple search index generation
- Basic overlay and inline result display options