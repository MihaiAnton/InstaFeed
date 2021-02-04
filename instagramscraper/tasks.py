from celery import shared_task
from .models import Profile, Post, Image, Change
from .instagramscraper import InstagramScraper
import os


def save_new_posts(profile: Profile, posts: list):
    for post_data in posts:
        post = Post(
            path=post_data["path"],
            description=post_data["data"]["description"],
            profile=profile
        )
        post.save()
        for photo_url in post_data["data"]["photo_urls"]:
            image = Image(url=photo_url, post=post)
            image.save()
            # TODO add image

        change = Change(change_type=Change.ChangeType.POST_ADDED, post=post)
        change.save()


def mark_removed_posts(profile: Profile, paths: list):
    for post_path in paths:
        posts = profile.post_set.filter(path=post_path)  # should be only 1
        if len(posts) > 0:
            posts[0].removed = True
            posts[0].save()

            change = Change(change_type=Change.ChangeType.POST_REMOVED, post=posts[0])
            change.save()


def compute_and_store_differences(profile: Profile, data: dict):
    """Checks the differences between the previous knowledge and the new one.

    Arguments:
        profile {Profile} -- [profile object]
        data {dict} -- [new scraped data]
    """
    # previous posts
    print("Previous diffs")
    previous_posts = []
    for post in profile.post_set.all():
        previous_posts.append(post.path)

    # new posts
    print("New posts")
    new_posts = []
    for post in data["posts"]:
        if post["path"] not in previous_posts:
            new_posts.append(post)

    # removed posts
    print("Removed posts")
    actual_posts = [post["path"] for post in data["posts"]]
    removed_posts = []
    for post_path in previous_posts:
        if post_path not in actual_posts:
            removed_posts.append(post_path)

    save_new_posts(profile, new_posts)
    mark_removed_posts(profile, removed_posts)


@shared_task
def scrap_and_check_for_updates():
    """Scraps instagram profiles and checks for updates. Stores any difference.
    """
    scraper = InstagramScraper(os.environ.get("INSTAGRAM_USERNAME"),
                               os.environ.get("INSTAGRAM_PASSWORD"))

    for profile in Profile.objects.all():
        print(f"Scraping profile:{profile.username}")
        profile_data = scraper.scrape_profile(profile.username)
        compute_and_store_differences(profile, profile_data)

    del scraper
