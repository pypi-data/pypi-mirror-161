"use strict";

/**
 * Mixin for resources that are children of a draft resource.
 *
 * This will ensure that the draft is in a proper state before operating
 * on the resource.
 */
RB.DraftResourceChildModelMixin = {
  /**
   * Delete the object's resource on the server.
   *
   * This will ensure the draft is created before deleting the object,
   * in order to record the deletion as part of the draft.
   *
   * Args:
   *     options (object):
   *         Options for the operation, including callbacks.
   *
   *     context (object):
   *         Context to bind when calling callbacks.
   */
  destroy() {
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    let context = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : undefined;
    this.get('parentObject').ensureCreated({
      success: _super(this).destroy.bind(this, options, context),
      error: options.error
    }, context);
  },

  /**
   * Call a function when the object is ready to use.
   *
   * This will ensure the draft is created before ensuring the object
   * is ready.
   *
   * Args:
   *     options (object):
   *         Options for the operation, including callbacks.
   *
   *     context (object):
   *         Context to bind when calling callbacks.
   */
  ready() {
    let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    let context = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : undefined;
    this.get('parentObject').ensureCreated({
      success: _super(this).ready.bind(this, options, context),
      error: options.error
    }, context);
  }

};

//# sourceMappingURL=draftResourceChildModelMixin.js.map