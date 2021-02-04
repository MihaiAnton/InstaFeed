from celery import shared_task


@shared_task
def scrap_and_check_for_updates():
    """Scraps instagram profiles and checks for updates. Stores any difference.
    """
    
