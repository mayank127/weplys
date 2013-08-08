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
from lxml import etree
from django.utils.http import urlencode
import time
def login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	else:
		if request.method == 'GET' and 'next' in request.GET:
			return render_to_response('login.html', {'next' : request.GET['next']})
		else:
			return render_to_response('login.html', {'next' : ''})

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/login/')

def import_songs(request):
	args = {}
	args.update(csrf(request))
	return render_to_response('checkpost.html', args)

@login_required(login_url='/login/')
def main_page(request):
	args = {}
	args.update(csrf(request))
	args['user'] = request.user.first_name +" " +request.user.last_name
	return render_to_response('weplys.html',args)

@login_required(login_url='/login/')
def about(request):
	return render_to_response('about.html', {'user' : request.user.first_name +" " +request.user.last_name})

@login_required(login_url='/login/')
def contact(request):
	return render_to_response('contact.html',  {'user' : request.user.first_name +" " +request.user.last_name})

@login_required(login_url='/login/')
def add_song(request):
	format = "json"
	key = 'b4c23ac3ddbce25921a781e058e97991'
	if request.is_ajax():
		if request.method == 'POST':
			song = json.loads(request.POST['song'])
			print song
			try:
				url = 'http://tinysong.com/s/' + song['songname'].replace(' ', '+') + '?format=' + format + '&key=' + key
				result = urllib2.urlopen(url)
				resultData = json.loads(result.read())
				print resultData
				print "\n\n\n"
				if len(resultData)>0:
					artistList = [x['ArtistName'] for x in resultData]
					match = difflib.get_close_matches(song['artistname'], artistList)
					print "Match", match
					if match:
						songInfo = resultData[artistList.index(match[0])]
					else:
						songInfo = resultData[0]
					try:
						print "songInfo> ",songInfo
						print songInfo['SongName']
						songDB = SongInfo.objects.get(songname=songInfo['SongName'])
						print songDB
					except Exception,e:
						print "here", e
						songDB = SongInfo(songID=songInfo['SongID'], songname=songInfo['SongName'], playcount=0, artist=songInfo['ArtistName'], album=songInfo['AlbumName'])
						songDB.save()
					try:
						user= request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
						userSong = UserSongs.objects.get(user=user, song=songDB)
					except Exception,e:
						print e
						userSong = UserSongs(user=user, song=songDB, playcount=0, lastplayed=timezone.now(), userrating=0)
						userSong.save()
					dict = model_to_dict(userSong)
					dict['lastplayed'] = str(time.mktime(dict['lastplayed'].timetuple()))
					dict['song'] = model_to_dict(userSong.song)
					print dict
					return HttpResponse(json.dumps(dict), mimetype="application/json")
			except Exception,e:
				print e
	return HttpResponse("OK")

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

@login_required(login_url='/login/')
def delete_song(request):
	if request.is_ajax():
		if request.method == 'POST':
			data = json.loads(request.POST['data'])
			try:
				song = SongInfo.objects.get(songname=data['songName'])
				usersong = UserSongs.objects.get(user=request.user, song=song)
				PlaylistSong.objects.filter(song=usersong.song).delete()
				usersong.delete()
			except:
				pass
		return HttpResponse('OK')

def get_lyrics(request):
	if request.is_ajax():
		if request.method == 'POST':
			data = json.loads(request.POST['song'])
			try:
				song = SongInfo.objects.get(songname=data)
				url = "http://lyrics.wikia.com/api.php?func=getSong&artist="+song.artist.replace(" ","_")+"&song="+song.songname.replace(" ","_")+"&fmt=json"
				result = urllib2.urlopen(url)
				strname = result.read()
				resultData = strname.split("'url':'")[-1].split("'\n")[0]
				url="http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20html%20where%20url=%22"+resultData+"%22%20and%20xpath=%27//div[@class=%22lyricbox%22]/p%27&format=json"
				result = urllib2.urlopen(url)
				strname = result.read()
				resultData = strname.split('"content":"')[-1].split('"')[0].replace("\\n", "<br>")
				dict = model_to_dict(song)
				dict['lyrics'] = resultData
				return HttpResponse(json.dumps(dict), mimetype="application/json")
			except Exception,e:
				pass
		return HttpResponse('Not Found')

