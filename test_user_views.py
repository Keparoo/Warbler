"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py
#    FLASK_ENV=production python -m unittest -v test_user_views.py # For more verbose output


import os
from unittest import TestCase
from bs4 import BeautifulSoup

from models import db, connect_db, Message, User, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.uid = 666
        self.testuser.id = self.uid

        self.u1 = User.signup("user1", "test1@test.com", "password1", None)
        self.u1_id = 667
        self.u1.id = self.u1_id
        self.u2 = User.signup("user2", "test2@test.com", "password2", None)
        self.u2_id = 668
        self.u2.id = self.u2_id
        self.u3 = User.signup("user3", "test3@test.com", "password3", None)
        self.u3_id = 669
        self.u3.id = self.u3_id
        self.u4 = User.signup("user4", "test4@test.com", "password4", None)
        self.u4_id = 670
        self.u4.id = self.u4_id

        db.session.commit()

    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()

    #=========================================================================================================
    # View Users Tests
    #=========================================================================================================

    def test_users_show(self):
        """Test /users"""

        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@user1", str(resp.data))
            self.assertIn("@user2", str(resp.data))
            self.assertIn("@user3", str(resp.data))
            self.assertIn("@user4", str(resp.data))

    def test_search_user(self):
        """Test search query string on /users"""

        with self.client as c:
            resp = c.get("/users?q=test")

        self.assertIn("@testuser", str(resp.data))
        self.assertNotIn("@user1", str(resp.data))
        self.assertNotIn("@user2", str(resp.data))
        self.assertNotIn("@user3", str(resp.data))
        self.assertNotIn("@user4", str(resp.data))

    def test_users_show(self):
        """Test /users/<user_id>"""

        with self.client as c:
            resp = c.get(f"/users/{self.uid}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))

    #=========================================================================================================
    # Follow Tests
    #=========================================================================================================

    def setup_followers(self):
        """Setup test data for follower/following"""

        t_u1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.uid)
        t_u2 = Follows(user_being_followed_id=self.u2_id, user_following_id=self.uid)
        u1_t = Follows(user_being_followed_id=self.uid, user_following_id=self.u1_id)
        u2_t = Follows(user_being_followed_id=self.uid, user_following_id=self.u2_id)

        db.session.add_all([t_u1,t_u2, u1_t, u2_t])
        db.session.commit()

    def test_show_following(self):
        """Test /users/<user_id>/following"""
        
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid

            resp = c.get(f"/users/{self.uid}/following")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user1", str(resp.data))
            self.assertIn("@user2", str(resp.data))
            self.assertNotIn("@user3", str(resp.data))
            self.assertNotIn("@user4", str(resp.data))

    def test_show_followers(self):
        """Test /users/<user_id>/followers"""

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid

            resp = c.get(f"/users/{self.uid}/followers")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user1", str(resp.data))
            self.assertIn("@user2", str(resp.data))
            self.assertNotIn("@user3", str(resp.data))
            self.assertNotIn("@user4", str(resp.data))

    def test_unauth_following_access(self):
        """Test fail of /users/<user_id>/following with no session"""

        self.setup_followers()
        with self.client as c:

            resp = c.get(f"/users/{self.uid}/following", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@user1", str(resp.data))
            self.assertNotIn("@user2", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))

    def test_unauth_followers_access(self):
        """Test fail of /users/<user_id>/followers with no session"""

        self.setup_followers()
        with self.client as c:

            resp = c.get(f"/users/{self.uid}/followers", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@user1", str(resp.data))
            self.assertNotIn("@user2", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))

    #=========================================================================================================
    # Likes Tests
    #=========================================================================================================

    def test_add_like(self):
        """Test successful /users/add_like/<message_id>"""

        m = Message(id=777, text="Test add like message", user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid

            resp = c.post("/users/add_like/777", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==777).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.uid)

    def setup_likes(self):
        """Setup test data for likes"""

        m1 = Message(text="test message 1", user_id=self.uid)
        m2 = Message(text="test message 2", user_id=self.uid)
        m3 = Message(id=5555, text="test liked message", user_id=self.u1_id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        l1 = Likes(user_id=self.uid, message_id=5555)

        db.session.add(l1)
        db.session.commit()

    def test_remove_like(self):
        """Test successful remove like /users/remove_like/<message_id>"""
        self.setup_likes()

        liked_message = Message.query.filter(Message.text=="test liked message").one()
        self.assertIsNotNone(liked_message)
        self.assertNotEqual(liked_message.user_id, self.uid)

        like = Likes.query.filter(
            Likes.user_id==self.uid and Likes.message_id==liked_message.id
        ).one()

        self.assertIsNotNone(like) # User likes this message

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid

            resp = c.post(f"/users/remove_like/{liked_message.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)   

            likes = Likes.query.filter(Likes.message_id==liked_message.id).all()
            # There are no liked messages
            self.assertEqual(len(likes), 0)

    def test_like_no_auth(self):
        """Test fail of like message with no session"""

        self.setup_likes()

        m = Message.query.filter(Message.text=="test liked message").one()
        self.assertIsNotNone(m)

        num_likes = Likes.query.count()

        with self.client as c:
            resp = c.post(f"/users/add_like/{m.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized", str(resp.data))

            # The number of likes has not changed since making the request
            self.assertEqual(num_likes, Likes.query.count())

    #=========================================================================================================
    # Tests by Springboard using Beautiful Soup to study
    #=========================================================================================================

    def test_user_show_with_likes(self):
        """Test show user check likes status bar"""
        self.setup_likes()

        with self.client as c:
            resp = c.get(f"/users/{self.uid}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 2 messages
            self.assertIn("2", found[0].text)

            # Test for a count of 0 followers
            self.assertIn("0", found[1].text)

            # Test for a count of 0 following
            self.assertIn("0", found[2].text)

            # Test for a count of 1 like
            self.assertIn("1", found[3].text)

    def test_user_show_with_follows(self):
        """Test user show followers status bar"""

        self.setup_followers()

        with self.client as c:
            resp = c.get(f"/users/{self.uid}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 0 messages
            self.assertIn("0", found[0].text)

            # Test for a count of 2 following
            self.assertIn("2", found[1].text)

            # Test for a count of 1 follower
            self.assertIn("2", found[2].text)

            # Test for a count of 0 likes
            self.assertIn("0", found[3].text)