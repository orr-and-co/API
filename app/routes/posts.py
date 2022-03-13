from datetime import datetime

from flask import abort, jsonify, request

from .. import db
from ..models import Post
from . import api
from .authentication import auth


@api.route("/posts/recent/", methods=["GET"])
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
                "published_at": post.published_at.timestamp(),
            }
            for post in posts.items
        ]
    )


@api.route("/posts/", methods=["GET"])
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
        if post.published_at is None or post.published_at > datetime.now():
            abort(404)

        else:
            json_data = {
                "title": post.title,
                "content": post.content,
                "link": post.link,
                "published_at": post.published_at.timestamp(),
                "publisher": {
                    "name": post.publisher.name if post.publisher is not None else None
                },
                "followup": post.followup_id,
            }

            return jsonify(json_data)
    else:
        abort(404)


@api.route("/posts/", methods=["POST"])
@auth.login_required
def create_posts():
    """
    Create a new :class:`Post`. Requires authorization

    **Route**: /api/v1/posts

    **Method**: POST

    :param title: The title of the Post.
    :type title: str

    :param content: Markdown content of the Post.
    :type content: str

    :param link: Link of the Post if available.
    :type link: str

    :param publish_at: When to publish this post. If not specified, this post will be held
        as a draft. Provide a UNIX timestamp
    :type publish_at: int

    :return: ID of the new post
    """
    if request.json is None:
        abort(400)

    title = request.json.get("title")

    if title is None:
        abort(400)

    content = request.json.get("content")
    link = request.json.get("link")

    if (content or link) is None:
        abort(400)

    if request.json.get("publish_at") is not None:
        published_at = datetime.fromtimestamp(request.json.get("publish_at"))
    else:
        published_at = None

    post = Post(title=title, content=content, link=link, published_at=published_at)

    db.session.add(post)
    db.session.commit()

    return jsonify({"id": post.id})
