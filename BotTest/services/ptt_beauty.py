import random
import discord
from retrying import retry
from BotTest.models import Photo

def get_beauty_imgs(amount):
    imgs = []
    texts = []
    urls = []
    count = Photo.objects.count()
    for _ in range(amount):
        photo = query_img(count)
        imgs.append(photo.image_src)
        texts.append(photo.name)
        urls.append(photo.url)
    return imgs, texts, urls

@retry(stop_max_attempt_number=100)
def query_img(count):
    pk = random.randint(0, count - 1)
    return Photo.objects.get(pk=pk)

def get_someone_beauty_imgs(amount, query=None):
    if not query:
        return get_beauty_imgs(amount)
    imgs = []
    texts = []
    urls = []
    photos = list(Photo.objects.filter(name__icontains=query))
    for _ in range(amount):
        if not photos:
            break
        photo = random.choice(photos)
        imgs.append(photo.image_src)
        texts.append(photo.name)
        urls.append(photo.url)
        photos.remove(photo)
    return imgs, texts, urls

def dc_beauty_message(imgs, texts, urls):
    embeds = []
    for img, text, url in zip(imgs, texts, urls):
        embed = discord.Embed(
            title=text,
            url=url,
        )
        embed.set_image(url=img)
        embeds.append(embed)
    return embeds
