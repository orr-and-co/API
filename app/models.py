"""
Models describe how the API interacts with the database. Generally, these models are database-agnostic due to SQLAlchemy.

Reference: :download:`Deliverable 2 <../ref/deliverable-2.pdf>`.
"""

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

    id = db.Column(db.Integer, autoincrement=True)
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
    """

    pass


class Interest(Model):
    """
    An Interest represents a classification of a :class:`Post`. These are used to allow
    users to subscribe to their own interests.
    """

    pass


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
