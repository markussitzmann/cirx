import codecs
import os

from django.conf import settings

from chemical.file.models import *
from chemical.file.filekey import FileKey
#from chemical.file.user_file_processor import *
#from chemical.file.forms import *
#from chemical.structure.resolver import *


def prepare_upload_file(request, key, form_data_string = None):

	#if not request and not form:
	#	raise UploadError('upload failed')
	
	http_request_file = request.FILES.get('file', None)
	if not http_request_file:
		http_request_file = request.FILES.get('upload', None)
	#if not http_request_file:
	#	http_request_file = request.POST.get('file', None)

	#if form and form.is_valid():
	#	form_data_string = form.cleaned_data['string']
	#else:
	#	form_data_string = None
				
	server_file_name = 'tmp_%s.upload' % key
	server_file_path = os.path.join(settings.MEDIA_ROOT, 'tmp', server_file_name)
			
	server_file_utf8 = codecs.open(server_file_path, 'wb+', 'utf-8')
	server_file = codecs.open(server_file_path, 'wb+')
	
	if http_request_file and not form_data_string:
		for chunk in http_request_file.chunks():
			server_file.write(chunk)
		original_filename = http_request_file.name
		display_name = os.path.splitext(original_filename)[0]
	elif form_data_string and not http_request_file:
		try:
			server_file.write(form_data_string)
			wrote_utf8=False
		except:
			server_file_utf8.write(form_data_string)
			wrote_utf8=True
		original_filename = "no_name"
		display_name = "No Name"
	else:
		raise UploadError('upload failed')
		server_file.close()
		server_file_utf8.close()
	return original_filename, display_name, server_file_path



def get_user_file_from_session(session, user, file_identifier=None):
	
	if not session.has_key('user_file_dict'):
		session['user_file_dict'] = {}
		session['user_file_dict'][user] = []
		return None
	else:
		if not user.is_anonymous():	
			user_file_dict = session['user_file_dict']
			user_file_dict[user] = list(UserFile.objects.filter(user=user).order_by('date_added'))
			session['user_file_dict'] = user_file_dict
		else:
			if not session['user_file_dict'].has_key(user):
				session['user_file_dict'][user] = []
		user_file_dict = session['user_file_dict']
		if user_file_dict.has_key(user):
			user_file_list = user_file_dict[user]
		else:
			user_file_list = []
	if not session.has_key('current_user_file'):
		try:
			current_user_file = user_file_list[-1]
			session['current_user_file'] = current_user_file
		except:
			current_user_file = None
			session['current_user_file'] = None
	else:
		current_user_file = session['current_user_file']
			
	if file_identifier == 'latest' or file_identifier == 'last' or file_identifier == 'new' or file_identifier == 'newest' or not file_identifier:
		try:
			return user_file_list[-1]
		except:
			return None
	elif file_identifier == 'result_file':
		for user_file in user_file_list:
			result_file = UserFile.objects.filter(
				id=user_file.id, 
				created_from_search_result=True, 
				date_added__gte = datetime.date.today() - datetime.timedelta(1)
			).order_by('date_added')
			if result_file:
				return user_file
		return None
	else:
		for user_file in user_file_list:
			try:
				user_file_upload_key = user_file.key.upload
				if user_file_upload_key == file_identifier:
					return user_file
			except:
				pass
		try:
			file_id = int(file_identifier) - 1
			return user_file_list[file_id]
		except:
			return current_user_file


class UploadError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __expr__(self):
		return self.msg