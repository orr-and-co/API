from datetime import datetime

from flask import abort, jsonify, request

from .. import db
from ..models import Interest, Post
from . import api
from .authentication import auth


@api.route("/posts/all/", methods=["GET"])
@auth.login_required
def all_posts():
    """
    Get a page of posts ordered by creation date. Requires authorization.

    **Route**: /api/v1/posts/all/?page=page

    **Method**: GET

    :param page: Optionally specify the page to get. Otherwise returns the first page.
    :type page: int

    :return: A list of previews of posts.

    .. code-block:: json

            {
                "id": 1,
                "title": "title",
                "short_content": "short_content",
                "published_at": "time",
                "preview": "preview base64",
                "interests": []
            }
    """
    try:
        page = int(request.args.get("page") or 1)
    except ValueError:
        abort(400)
    else:
        posts = Post.query.order_by(Post.created_at.desc()).paginate(page, 15)

        return jsonify(
            [
                {
                    "id": post.id,
                    "title": post.title,
                    "short_content": post.short_content,
                    "created_at": post.created_at.timestamp(),
                    "published_at": published_at.timestamp()
                    if (published_at := post.published_at) is not None
                    else None,
                    "preview": post.preview_image,
                    "interests": [interest.name for interest in post.interests],
                }
                for post in posts.items
            ]
        )


@api.route("/posts/media/", methods=["GET"])
def media_posts():
    """
    Get a page of recent media posts.

    **Route**: /api/v1/posts/media/?page=page

    **Method**: GET

    :param page: Optionally specify the page to get. Otherwise returns the first page.
    :type page: int

    :return: A list of previews of posts.

    .. code-block:: json

            {
                "id": 1,
                "title": "title",
                "published_at": "time",
                "preview": "preview base64",
                "interests": []
            }
    """
    try:
        page = int(request.args.get("page") or 1)
    except ValueError:
        abort(400)
    else:
        posts = (
            Post.query.order_by(Post.published_at.desc())
            .filter(Post.published_at <= datetime.now())
            .filter(Post.binary_content.isnot(None))
            .paginate(page, 15)
        )

        return jsonify(
            [
                {
                    "id": post.id,
                    "title": post.title,
                    "published_at": post.published_at.timestamp(),
                    "preview": post.preview_image,
                    "interests": [interest.name for interest in post.interests],
                }
                for post in posts.items
            ]
        )


@api.route("/posts/recent/", methods=["GET"])
def recent_posts():
    """
    Get a page of recent posts.

    **Route**: /api/v1/posts/recent/?page=page

    **Method**: GET

    :param page: Optionally specify the page to get. Otherwise returns the first page.
    :type page: int

    :param interests: Optionally specify a list of interest names to filter to,
        space-separated (use %20 for HTML encoded).
    :type interests: List[str]

    :return: A list of previews of posts.

    .. code-block:: json

            {
                "id": 1,
                "title": "title",
                "short_content": "short_content",
                "published_at": "time",
                "preview": "preview base64",
                "interests": []
            }
    """
    try:
        page = int(request.args.get("page") or 1)
    except ValueError:
        abort(400)
    else:
        if (interests := request.args.get("interests")) is not None:
            interests = interests.split(" ")

            # please man please just let me write SQL
            posts = (
                Post.query.order_by(Post.published_at.desc())
                .filter(Post.published_at <= datetime.now())
                .filter(Post.interests.any(Interest.name.in_(interests)))
                .paginate(page, 15)
            )
        else:
            posts = (
                Post.query.order_by(Post.published_at.desc())
                .filter(Post.published_at <= datetime.now())
                .paginate(page, 15)
            )

        return jsonify(
            [
                {
                    "id": post.id,
                    "title": post.title,
                    "short_content": post.short_content,
                    "published_at": post.published_at.timestamp(),
                    "preview": post.preview_image,
                    "interests": [interest.name for interest in post.interests],
                }
                for post in posts.items
            ]
        )


@api.route("/posts/<int:id>/", methods=["GET"])
def get_posts(id: int):
    """
    Get a specific :class:`Post`. Used when loading a post in full and not just the
        preview. Substitute **id** in the route for the ID to get.

    **Route**: /api/v1/posts/ID/

    **Method**: GET

    :param id: The ID of the :class:`Post` to get.
    :type id: int

    :return: :class:`Post`
    """
    if id is None:
        abort(400)

    post = Post.query.get(id)

    if post is not None:
        if post.published_at is None or post.published_at > datetime.now():
            abort(404)

        else:
            json_data = {
                "title": post.title,
                "short_content": post.short_content,
                "content": post.content,
                "link": post.link,
                "published_at": post.published_at.timestamp(),
                "publisher": {
                    "name": post.publisher.name if post.publisher is not None else None
                },
                "media": post.binary_content,
                "followup": post.followup_id,
                "interests": [interest.name for interest in post.interests],
            }

            return jsonify(json_data)
    else:
        abort(404)


@api.route("/posts/", methods=["POST"])
@auth.login_required
def create_posts():
    """
    Create a new :class:`Post`. Requires authorization

    **Route**: /api/v1/posts/

    **Method**: POST

    :param title: The title of the Post.
    :type title: str

    :param short_content: Plain text content for the Post preview.
    :type short_content: str

    :param content: Markdown content of the Post.
    :type content: str

    :param link: Link of the Post if available.
    :type link: str

    :param preview_image: Base 64 encoded review image of the post.
    :type preview_image: str

    :param binary_content: Base 64 encoded multimedia of the post.
    :type binary_content: str

    :param interests: Names of interests to attach to this post.
    :type interests: List[str]

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

    short_content = request.json.get("short_content")
    content = request.json.get("content")
    link = request.json.get("link")
    preview_image = request.json.get("preview_image")
    binary_content = request.json.get("binary_content")

    if (content or link) is None:
        abort(400)

    if request.json.get("publish_at") is not None:
        published_at = datetime.fromtimestamp(request.json.get("publish_at"))
    else:
        published_at = None

    interests = [
        Interest.query.filter(Interest.name == interest).first()
        for interest in (request.json.get("interests") or [])
    ]

    if any(interest is None for interest in interests):
        abort(400)

    post = Post(
        title=title,
        short_content=short_content,
        content=content,
        link=link,
        published_at=published_at,
        preview_image=preview_image,
        binary_content=binary_content,
        interests=interests,
        publisher=auth.current_user(),
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({"id": post.id})


@api.route("/posts/<int:id>/", methods=["PATCH"])
@auth.login_required
def update_posts(id: int):
    """
    Update an existing :class:`Post` by ID. Requires authorization

    **Route**: /api/v1/posts/id/

    **Method**: PATCH

    :param title: The new title of the Post.
    :type title: str

    :param content: New markdown content of the Post.
    :type content: str

    :param link: New link of the Post.
    :type link: str

    :param preview_image: New base 64 encoded review image of the post.
    :type preview_image: str

    :param binary_content: New base 64 encoded multimedia of the post.
    :type binary_content: str

    :param interests: List of interests to attach to the post.
    :type interests: List[str]

    :return: 201
    """
    if request.json is None:
        abort(400)

    post = Post.query.get(id)

    if post is None:
        abort(404)
    else:
        if (title := request.json.get("title")) is not None:
            post.title = title

        if (content := request.json.get("content")) is not None:
            post.content = content

        if (link := request.json.get("link")) is not None:
            post.link = link

        if (preview_image := request.json.get("preview_image")) is not None:
            post.preview_image = preview_image

        if (binary_content := request.json.get("binary_content")) is not None:
            post.binary_content = binary_content

        if (interests := request.json.get("interests")) is not None:
            interests = [
                Interest.query.filter(Interest.name == interest).first()
                for interest in interests
            ]

            if any(interest is None for interest in interests):
                # rollback db to prevent odd changes sticking around in memory
                db.session.rollback()

                abort(400)
            else:
                post.interests = interests

        db.session.commit()

        return "", 201


@api.route("/posts/<int:id>/followup/", methods=["POST"])
@auth.login_required
def create_followup_posts(id: int):
    """
    Create a new :class:`Post` that follows up on an existing :class:`Post`. Requires authorization

    **Route**: /api/v1/posts/ID/followup/

    **Method**: POST

    :param title: The title of the Post.
    :type title: str

    :param content: Markdown content of the Post.
    :type content: str

    :param link: Link of the Post if available.
    :type link: str

    :param preview_image: Base 64 encoded review image of the post.
    :type preview_image: str

    :param binary_content: Base 64 encoded multimedia of the post.
    :type binary_content: str

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
    preview_image = request.json.get("preview_image")
    binary_content = request.json.get("binary_content")

    if (content or link) is None:
        abort(400)

    if request.json.get("publish_at") is not None:
        published_at = datetime.fromtimestamp(request.json.get("publish_at"))
    else:
        published_at = None

    post = Post(
        title=title,
        content=content,
        link=link,
        published_at=published_at,
        preview_image=preview_image,
        binary_content=binary_content,
        publisher=auth.current_user(),
    )

    previous_post = Post.query.get(id)
    if previous_post is None:
        abort(404)
    else:
        # flush must be done first to give `post' an ID
        db.session.add(post)
        db.session.flush()

        previous_post.followup = post
        db.session.commit()

        return jsonify({"id": post.id})
