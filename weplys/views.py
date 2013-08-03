from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from models import *
import json, urllib2, difflib
from django.utils import timezone
from django.core import serializers
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

def login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	else:
		if request.method == 'GET' and 'next' in request.GET:
			return render_to_response('login.html', {'next' : request.GET['next']})
		else:
			return render_to_response('login.html', {'next' : ''})

#@login_required(login_url='/login/')
def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/login/')

@login_required
def import_songs(request):
	args = {}
	args.update(csrf(request))
	return render_to_response('import_songs.html', args)

@login_required(login_url='/login/')
def add_songs(request):
	format = "json"
	key = 'b4c23ac3ddbce25921a781e058e97991'
	if request.is_ajax():
		if request.method == 'POST':
			data = json.loads(request.POST['data'])
			foldername = data['folder']
			songlist = data['songlist']
			for song in songlist:
				url = 'http://tinysong.com/s/' + song['songname'].replace(' ', '+') + '?format=' + format + '&key=' + key
				result = urllib2.urlopen(url)
				resultData = json.loads(result.read())
				if len(resultData)>0:
					artistList = [x['ArtistName'] for x in resultData]
					match = difflib.get_close_matches(song['artistname'], artistList)
					if match:
						songInfo = resultData[artistList.index(match[0])]
					else:
						songInfo = resultData[0]
					try:
						songDB = SongInfo.objects.get(songID=songInfo['SongID'])
					except:
						songDB = SongInfo(songID=songInfo['SongID'], songname=songInfo['SongName'], playcount=0, artist=songInfo['ArtistName'], album=songInfo['AlbumName'])
						songDB.save()
				else:
					songDB = SongInfo(songID="-1", songname=song['songname'],playcount=0,artist=song['artistname'],album="Unknown")
					songDB.save()
				
				try:
					userSong = UserSongs.objects.get(user=request.user, song=songDB)
				except:
					userSong = UserSongs(user=request.user, song=songDB, filelocation= foldername+'/'+song['filename'], playcount=0, lastplayed=timezone.now(), userrating=0)
					userSong.save()
				try:
					userPlaylist = UserPlaylist.objects.get(user=request.user, playlistName="All Songs")
				except:
					userPlaylist = UserPlaylist(user=request.user, playlistName="All Songs")
					userPlaylist.save()
				try:
					playlistSong = PlaylistSong.objects.get(playlist=userPlaylist, song=songDB)
				except:
					playlistSong = PlaylistSong(playlist=userPlaylist, song=songDB)
					playlistSong.save()
	return HttpResponse('OK')

@login_required(login_url='/login/')
def add_playlist(request):
	if request.is_ajax():
		if request.method == 'POST':
			data = json.loads(request.POST['data'])
			try:
				userPlaylist = UserPlaylist.objects.get(user=request.user, playlistName=data['playlistName'])
			except:
				userPlaylist = UserPlaylist(user=request.user, playlistName=data['playlistName'])
				userPlaylist.save()
	data = list(UserPlaylist.objects.filter(user=request.user).values())
	return HttpResponse(json.dumps(data), mimetype="application/json")



@login_required(login_url='/login/')
def load_playlist(request):
	if request.is_ajax():
		if request.method == 'POST':
			data = json.loads(request.POST['data'])
			try:
				userPlaylist = UserPlaylist.objects.get(user=request.user, playlistName=data['playlistName'])
				songs = PlaylistSong.objects.filter(playlist=userPlaylist).values('song')
				data = []
				for song in songs:
					songInfo  = SongInfo(pk=song['song'])
					userSong = UserSongs.objects.get(user=request.user, song=songInfo)
					data.append(userSong)
				return HttpResponse(serializers.serialize('json', data), mimetype="application/json")
			except Exception,e:
				pass
		return HttpResponse(json.dumps([]), mimetype="application/json")

@login_required(login_url='/login/')
def delete_playlist(request):
	if request.is_ajax():
		if request.method == 'POST':
			data = json.loads(request.POST['data'])
			try:
				userPlaylist = UserPlaylist.objects.get(user=request.user, playlistName=data['playlistName'])
				playlistSongs = PlaylistSong.objects.filter(playlist=userPlaylist).delete()
				userPlaylist.delete()
			except:
				pass
		return HttpResponse('OK')

@login_required(login_url='/login/')
def add_song_to_playlist(request):
	if request.is_ajax():
		if request.method == 'POST':
			data = json.loads(request.POST['data'])
			try:
				userPlaylist = UserPlaylist.objects.get(user=request.user, playlistName=data['playlistName'])
				song = SongInfo.objects.filter(songname=data['songName'])[0]
				try:
					playlistSong = PlaylistSong.objects.get(playlist=userPlaylist, song=song)
				except:
					playlistSong = PlaylistSong(playlist=userPlaylist,song=song)
					playlistSong.save()
			except:
				pass
		return load_playlist(request)

@login_required(login_url='/login/')
def delete_song_from_playlist(request):
	if request.is_ajax():
		if request.method == 'POST':
			data = json.loads(request.POST['data'])
			try:
				userPlaylist = UserPlaylist.objects.get(user=request.user, playlistName=data['playlistName'])
				song = SongInfo.objects.filter(songname=data['songName'])[0]
				PlaylistSong.objects.get(playlist=userPlaylist, song=song).delete()
			except:
				pass
		return load_playlist(request)