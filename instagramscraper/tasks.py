from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Profile, Post, Image, Change
from .instagramscraper import InstagramScraper
import os
from django.core.mail import send_mail
from datetime import datetime, timedelta
import time


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
    # print("Previous diffs")
    previous_posts = []
    for post in profile.post_set.filter(removed=False):
        previous_posts.append(post.path)

    # new posts
    # print("New posts")
    new_posts = []
    for post in data["posts"]:
        if post["path"] not in previous_posts:
            new_posts.append(post)

    # removed posts
    # print("Removed posts")
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
        print(f"Checking profile:{profile.username}")
        try:
            profile_data = scraper.scrape_profile(profile.username)
            compute_and_store_differences(profile, profile_data)
        except Exception as err:
            pass

    del scraper


# mails
@shared_task
def added_post_html(profile_url: str, username: str, post_url: str, description: str, image_links: [],
                    _time: str) -> str:

    images_html = ""
    for image_link in image_links:
        images_html += f"""\
            <img
                style="display:inline-block;float:left;margin-right:5px;margin-bottom:5px"
                src="{image_link}"
                alt="Instagram photo"
                width="auto"
                height="200"/>
        """

    return f"""\
        <div id="post_0" style="color:black;width:100%;display:block;overflow:auto">
            <p style="color:black">
                {_time} <a style="color:gray" href="{profile_url}/">{username}</a>
                added a new
                <a style="color:gray" href="{post_url}">
                post
                </a>: {description}
            </p>
            <div
                id="post_0_images
                style="width:100%;display:block;overflow-x:auto;overflow-y:hidden;white-space:nowrap"
            >
                {images_html}
            </div>
        </div>
    """


@shared_task
def removed_post_html(profile_url: str, username: str, post_url: str, description: str, image_links: [],
                      _time: str) -> str:

    images_html = ""
    for image_link in image_links:
        images_html += f"""\
            <img
                style="display:inline-block;float:left;margin-right:5px;margin-bottom:5px"
                src="{image_link}"
                alt="Instagram photo"
                width="auto"
                height="200"/>
        """

    return f"""\
        <div id="post_0" style="color:black;width:100%;display:block;overflow:auto">
            <p style="color:black">
                {_time} <a style="color:gray" href="{profile_url}/">{username}</a>
                removed a post
                <a style="color:gray" href="{post_url}">
                post
                </a>: {description}
            </p>
            <div
                id="post_0_images
                style="width:100%;display:block;overflow-x:auto;overflow-y:hidden;white-space:nowrap"
            >
                {images_html}
            </div>
        </div>
    """


@shared_task
def format_time(_time: datetime):
    return "" + str(_time.hour) + ":" + str(_time.minute)


@shared_task
def send_daily_updates_email():
    time_limit = datetime.now() - timedelta(days=1)
    changes = Change.objects\
        .exclude(notification_sent=True)\
        .filter(created_at__gte=time_limit)\
        .order_by('created_at')

    posts_html = ""
    BASE_URL = 'https://www.instagram.com/'
    new_updates = False

    for change in changes:
        new_updates = True
        change.notification_sent = True
        change.save(update_fields=["notification_sent"])

        post = change.post
        profile = post.profile
        username = profile.username
        profile_url = BASE_URL + username
        post_url = BASE_URL + post.path
        description = post.description
        image_links = [image.url for image in post.image_set.all()]
        # print(change.created_at)
        created_at = format_time(change.created_at)
        if change.change_type == Change.ChangeType.POST_ADDED:
            posts_html += added_post_html(profile_url, username, post_url, description,
                                          image_links, created_at)

        elif change.change_type == Change.ChangeType.POST_REMOVED:
            posts_html += removed_post_html(profile_url, username, post_url, description,
                                            image_links, created_at)

    if new_updates:
        html = f"""\
            <html>
            <head></head>
            <body>
                <h1 style="color:black">Good afternoon!</h1>
                <p style="color:black">Here is you daily Instagram summary 🚀</p>
                {posts_html}
            </body>
            </html>
        """
    else:
        html = f"""\
            <html>
            <head></head>
            <body>
                <h1 style="color:black">Good afternoon!</h1>
                <p style="color:black">Nothing interesting happened on Instagram today 😕</p>
                {posts_html}
            </body>
            </html>
        """

    try:
        print("Sending mail")
        send_mail(
            'InstaFeed daily update 📱',
            '',
            os.environ.get("EMAIL_ACCOUNT"),
            ["mihai_anton98@yahoo.com"],  # add your email address here
            html_message=html,
            fail_silently=False,
            auth_user=os.environ.get("EMAIL_USER"),
            auth_password=os.environ.get("EMAIL_PASS")
        )
    except Exception as err:
        print(err)
