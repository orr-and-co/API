from datetime import datetime

from flask import abort, jsonify, request

from ..models import Post
from . import api


@api.route("/posts/recent", methods=["GET"])
def recent_posts():
    """
    Get a page of recent posts.

    **Route**: /api/v1/posts/recent

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
    if request.json is not None:
        page = request.json.get("page") or 1
    else:
        page = 1

    posts = (
        Post.query.order_by(Post.published_at.desc())
        .filter(Post.published_at <= datetime.now())
        .paginate(page, 15)
    )

    return jsonify(
        [
            {
                "title": post.title,
                "content": post.content,
                "published_at": post.published_at,
            }
            for post in posts.items
        ]
    )


@api.route("/posts", methods=["GET"])
def get_posts():
    """
    Get a specific :class:`Post`. Used when loading a post in full and not just the
        preview.

    **Route**: /api/v1/posts

    **Method**: GET

    :param id: The ID of the :class:`Post` to get.
    :type id: int

    :return: :class:`Post`
    """
    if request.json is None:
        abort(400)

    id = request.json.get("id")

    if id is None:
        abort(400)

    post = Post.query.get(id)

    if post is not None:
        json_data = {
            "title": post.title,
            "content": post.content,
            "link": post.link,
            "published_at": post.published_at,
            "publisher": {
                "name": post.publisher.name if post.publisher is not None else None
            },
            "followup": post.followup_id,
        }

        return jsonify(json_data)
    else:
        abort(404)
