"""
Models describe how the API interacts with the database. Generally, these models are
database-agnostic due to SQLAlchemy.

Reference: :download:`Deliverable 2 <../ref/deliverable-2.pdf>`.
"""

from datetime import datetime

from flask_sqlalchemy import Model
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Publisher(Model):
    """Database model for publisher information.

    :param id: Internal database ID of the publisher. Automatically increments. Should not
        be used for sensitive transactions due to auto-increment.
    :type id: int

    :param name: Real name provided by publisher.
    :type name: str

    :param email: Email provided by publisher. Used for login.
    :type email: str

    :param password_hash: Hash of the password for authenticating the user.
    :type password_hash: str

    :param full_admin: Boolean describing if the publisher has full admin capabilities,
        i.e can they create other admins.
    :type full_admin: bool
    """

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(256))
    email = db.Column(db.String(512))
    password_hash = db.Column(db.String(200))
    full_admin = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def password(self):
        """Property representing publisher password. This converts setter calls to
        hash/set calls. Property therefore cannot be read, only set."""
        raise AttributeError("Cannot read password")

    @password.setter
    def password(self, password):
        """Set the password. This generates a hash via Werkzeug"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check that the provided password hashes to the hash stored in the database"""
        return check_password_hash(self.password_hash, password)


class Post(Model):
    """
    Posts represent data that is displayed to the end user. Posts are created by
    publishers.

    :param id: Internal ID of the post. Do not use for sensitive actions, since it
        autoincrements.
    :type id: int

    :param publisher_id: Internal ID of the :class:`Publisher` responsible for creating
        this Post. Use :attr:`publisher` instead!
    :type publisher_id: int

    :param publisher: :class:`Publisher` associated with the :attr:`publisher_id`.
    :type publisher: :class:`Publisher`

    :param title: The title of the Post.
    :type title: str

    :param content: Markdown content of the Post.
    :type content: str

    :param link: Link of the Post if available.
    :type link: str

    :param created_at: When this Post was created.
    :type created_at: datetime

    :param published_at: When this Post is set to be published (if not the same as
        :attr:`created_at`).
    :type published_at: datetime

    :param likes: How many likes this Post has.
    :type likes: int

    :param dislikes: How many dislieks this Post has.
    :type dislikes: int
    """

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey(Publisher.id))
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.String(8000))
    link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    published_at = db.Column(db.DateTime, default=datetime.now())
    likes = db.Column(db.Integer, nullable=False, default=0)
    dislikes = db.Column(db.Integer, nullable=False, default=0)

    publisher = db.relationship("Publisher", foreign_keys="Post.publisher_id")


class Interest(Model):
    """
    An Interest represents a classification of a :class:`Post`. These are used to allow
    users to subscribe to their own interests.

    :param id: Internal ID of the Interest.
    :type id: int

    :param name: The name of the Interest that is presented to the user.
    :type name: str

    :param description: Description of the Interest presented to the user.
    :type description: str
    """

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)


class PostInterest(Model):
    """
    Join table for :class:`Post` and :class:`Interest`
    """

    pass


class PostFollowup(Model):
    """
    Join table for :class:`Post` to :class:`Post` joins
    """

    pass


class PostModification(Model):
    """
    Stores the edit history of a :class:`Post`
    """

    pass
