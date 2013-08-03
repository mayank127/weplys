from django.db import models
from django.contrib.auth.models import User


class SongInfo(models.Model):
	songname = models.CharField(max_length=200)
	playcount = models.IntegerField(default=0)
	artist = models.CharField(max_length=200)
	album = models.CharField(max_length=200)

class UserSongs(models.Model):
	user = models.ForeignKey(User)
	song = models.ForeignKey(SongInfo)
	filelocation = models.CharField(max_length=200)
	playcount = models.IntegerField(default=0)
	lastplayed = models.DateTimeField()
	userrating = models.IntegerField(default=0)

class UserPlaylist(models.Model):
	user = models.ForeignKey(User)
	playlistName = models.CharField(max_length=200)

class PlaylistSong(models.Model):
	playlist = models.ForeignKey(UserPlaylist)
	song = models.ForeignKey(SongInfo)

