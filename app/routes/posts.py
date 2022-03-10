from . import app


@app.route("/api/posts/recent", methods=["GET"])
def recent_posts():
    """
    Get a page of recent posts.

    **Route**: /api/posts/recent

    **Method**: GET

    :param page: Optionally specify the page to get. Otherwise returns the first page.
    :type page: int

    :return: A list of previews of posts.

    .. code-block:: json

            {
                "title": "title",
                "content": "content",
                "published_at": "time"
            }
    """
    pass


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """
    Get a specific :class:`Post`. Used when loading a post in full and not just the
        preview.

    **Route**: /api/posts

    **Method**: GET

    :param id: The ID of the :class:`Post` to get.
    :type id: int

    :return: :class:`Post`
    """
    pass
