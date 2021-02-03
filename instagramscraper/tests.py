from django.test import TestCase
from .models import Profile, Post, Image, Change
from django.db.models import ProtectedError


class ProfileTests(TestCase):
    TEST_PROFILE_1 = "mihaianton98"
    TEST_PROFILE_2 = "instagram"

    def setUp(self):
        Profile.objects.create(username=self.TEST_PROFILE_1)
        Profile.objects.create(username=self.TEST_PROFILE_2, accessible=False)

    def test_str(self):
        profile = Profile.objects.get(username=self.TEST_PROFILE_1)
        self.assertEqual(str(profile), f"<Profile {self.TEST_PROFILE_1}>")

        profile = Profile.objects.get(username=self.TEST_PROFILE_2)
        self.assertEqual(str(profile), f"<Profile {self.TEST_PROFILE_2} | inaccessible>")

    def test_get_username(self):
        profile = Profile.objects.get(username=self.TEST_PROFILE_1)
        self.assertEqual(profile.username, self.TEST_PROFILE_1)

    def test_get_accesibility(self):
        profile = Profile.objects.get(username=self.TEST_PROFILE_1)
        self.assertTrue(profile.accessible)

        profile = Profile.objects.get(username=self.TEST_PROFILE_2)
        self.assertFalse(profile.accessible)


class PostTests(TestCase):
    TEST_PROFILE_1 = "mihaianton98"
    POST_PATH = "/p/demo_path"
    POST_DESCRIPTION = "demo description"

    def setUp(self):
        profile = Profile.objects.create(username=self.TEST_PROFILE_1)
        Post.objects.create(path=self.POST_PATH, description=self.POST_DESCRIPTION, profile=profile)

    def test_str(self):
        post = Post.objects.get(path=self.POST_PATH)
        self.assertEqual(str(post), f"<Post {self.POST_DESCRIPTION}>")

    def test_profile(self):
        post = Post.objects.get(path=self.POST_PATH)
        self.assertEqual(post.profile.username, self.TEST_PROFILE_1)

    def test_posts_of_profile(self):
        profile = Profile.objects.get(username=self.TEST_PROFILE_1)
        self.assertEqual(len(profile.post_set.all()), 1)
        self.assertEqual(profile.post_set.all()[0].path, self.POST_PATH)


class ImageTest(TestCase):
    TEST_PROFILE_1 = "mihaianton98"
    POST_PATH = "/p/demo_path"
    POST_DESCRIPTION = "demo description"
    IMAGE_URL = "/image_url"

    def setUp(self):
        profile = Profile.objects.create(username=self.TEST_PROFILE_1)
        post = Post.objects.create(path=self.POST_PATH, description=self.POST_DESCRIPTION, profile=profile)
        Image.objects.create(url=self.IMAGE_URL, post=post)

    def test_str(self):
        image = Image.objects.get(url=self.IMAGE_URL)
        self.assertEqual(str(image), f"<Image {self.IMAGE_URL}>")

    def test_profile_to_image(self):
        profile = Profile.objects.get(username=self.TEST_PROFILE_1)
        self.assertEqual(len(profile.post_set.all()[0].image_set.all()), 1)
        self.assertEqual(profile.post_set.all()[0].image_set.all()[0].url, self.IMAGE_URL)

    def test_image_to_profile(self):
        image = Image.objects.get(url=self.IMAGE_URL)
        self.assertEqual(image.post.profile.username, self.TEST_PROFILE_1)


class ChangeTest(TestCase):
    TEST_PROFILE_1 = "mihaianton98"
    POST_PATH = "/p/demo_path"
    POST_DESCRIPTION = "demo description"

    def setUp(self):
        profile = Profile.objects.create(username=self.TEST_PROFILE_1)
        post = Post.objects.create(path=self.POST_PATH, description=self.POST_DESCRIPTION, profile=profile)
        Change.objects.create(change_type=Change.ChangeType.POST_ADDED, post=post)
        Change.objects.create(change_type=Change.ChangeType.POST_REMOVED, post=post)

    def test_check_post(self):
        change = Change.objects.filter(change_type=Change.ChangeType.POST_ADDED)[0]
        self.assertEqual(change.post.path, self.POST_PATH)

    def test_check_exception(self):
        change = Change.objects.filter(change_type=Change.ChangeType.POST_REMOVED)[0]
        try:
            Post.objects.filter(path=self.POST_PATH).delete()
            self.fail()
        except ProtectedError as err:
            pass
