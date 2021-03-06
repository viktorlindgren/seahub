# encoding: utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _

from seaserv import ccnet_rpc, ccnet_threaded_rpc, seafserv_threaded_rpc, \
    is_valid_filename

from base.accounts import User
from pysearpc import SearpcError

import settings

class AddUserForm(forms.Form):
    """
    Form for adding a user.
    """

    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            raise forms.ValidationError(_("A user with this email already"))
        except User.DoesNotExist:
            return self.cleaned_data['email']            

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data

class RepoCreateForm(forms.Form):
    """
    Form for creating repo and org repo.
    """
    repo_name = forms.CharField(max_length=settings.MAX_FILE_NAME,
                                error_messages={
            'required': _(u'Name can\'t be empty'),
            'max_length': _(u'Name is too long (maximum is 255 characters)')
            })
    repo_desc = forms.CharField(max_length=100, error_messages={
            'required': _(u'Description can\'t be empty'),
            'max_length': _(u'Description is too long (maximum is 100 characters)')
            })
    encryption = forms.CharField(max_length=1)
    passwd = forms.CharField(min_length=3, max_length=30, required=False,
                             error_messages={
            'min_length': _(u'Password is too short (minimum is 3 characters)'),
            'max_length': _(u'Password is too long (maximum is 30 characters)'),
            })
    passwd_again = forms.CharField(min_length=3, max_length=30, required=False,
                                   error_messages={
            'min_length': _(u'Password is too short (minimum is 3 characters)'),
            'max_length': _(u'Password is too long (maximum is 30 characters)'),
            })

    def clean_repo_name(self):
        repo_name = self.cleaned_data['repo_name']
        if not is_valid_filename(repo_name):
            error_msg = _(u"Name %s is not valid") % repo_name
            raise forms.ValidationError(error_msg)
        else:
            return repo_name
        
    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. 
        """
        if 'passwd' in self.cleaned_data and 'passwd_again' in self.cleaned_data:
            encryption = self.cleaned_data['encryption']
            if int(encryption) == 0:
                # This prevents the case that form has passwords but the
                # encryption checkbox is not selected.
                self.cleaned_data['passwd'] = None
                self.cleaned_data['passwd_again'] = None
                return self.cleaned_data
            else:
                passwd = self.cleaned_data['passwd']
                passwd_again = self.cleaned_data['passwd_again']
                if passwd != passwd_again:
                    raise forms.ValidationError(_("Passwords don't match"))
        return self.cleaned_data

class SharedRepoCreateForm(RepoCreateForm):
    """
    Used for creating group repo and public repo
    """
    permission = forms.ChoiceField(choices=(('rw', 'read-write'), ('r', 'read-only')))

class RepoNewFileForm(forms.Form):
    """
    Form for create a new empty file.
    """
    repo_id = forms.CharField(error_messages={'required': _('Repo id is required')})
    parent_dir = forms.CharField(error_messages={'required': _('Parent dir is required')})
    new_file_name = forms.CharField(max_length=settings.MAX_FILE_NAME,
                                error_messages={
                                    'max_length': _('File name is too long'),
                                    'required': _('File name can\'t be empty'),
                                })

    def clean_new_file_name(self):
        new_file_name = self.cleaned_data['new_file_name']
        try:
            if not is_valid_filename(new_file_name):
                error_msg = _(u'File name "%s" is not valid') % new_file_name
                raise forms.ValidationError(error_msg)
            else:
                return new_file_name
        except SearpcError, e:
            raise forms.ValidationError(str(e))

class RepoRenameFileForm(forms.Form):
    """
    Form for rename a file.
    """
    repo_id = forms.CharField(error_messages={'required': _("Repo id is required")})
    parent_dir = forms.CharField(error_messages={'required': _("Parent dir is required")})
    oldname = forms.CharField(error_messages={'required': _("Oldname is required")})
    newname = forms.CharField(max_length=settings.MAX_FILE_NAME,
                                error_messages={
                                    'max_length': _('File name is too long'),
                                    'required': _('File name can\'t be empty'),
                                })

    def clean_newname(self):
        newname = self.cleaned_data['newname']
        try:
            if not is_valid_filename(newname):
                error_msg = _(u'File name "%s" is not valid') % newname
                raise forms.ValidationError(error_msg)
            else:
                return newname
        except SearpcError, e:
            raise forms.ValidationError(str(e))

class RepoNewDirForm(forms.Form):
    """
    Form for create a new empty dir.
    """
    repo_id = forms.CharField(error_messages={'required': _("Repo id is required")})
    parent_dir = forms.CharField(error_messages={'required': _("Parent dir is required")})
    new_dir_name = forms.CharField(max_length=settings.MAX_FILE_NAME,
                                error_messages={
                                    'max_length': _('Directory name is too long'),
                                    'required': _('Directory name can\'t be empty'),
                            })

    def clean_new_dir_name(self):
        new_dir_name = self.cleaned_data['new_dir_name']
        try:
            if not is_valid_filename(new_dir_name):
                error_msg = _(u'Directory name "%s" is not valid') % new_dir_name
                raise forms.ValidationError(error_msg)
            else:
                return new_dir_name
        except SearpcError, e:
            raise forms.ValidationError(str(e))

class RepoPassowrdForm(forms.Form):
    """
    Form for user to decrypt a repo in repo page.
    """
    repo_id = forms.CharField(error_messages={'required': _('Repo id is required')})
    username = forms.CharField(error_messages={'required': _('Username is required')})
    password = forms.CharField(error_messages={'required': _('Password can\'t be empty')})

    def clean(self):
        if 'password' in self.cleaned_data:
            repo_id = self.cleaned_data['repo_id']
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']
            try:
                seafserv_threaded_rpc.set_passwd(repo_id, username, password)
            except SearpcError, e:
                if e.msg == 'Bad arguments':
                    raise forms.ValidationError(_(u'Bad url format'))
                # elif e.msg == 'Repo is not encrypted':
                #     return HttpResponseRedirect(reverse('repo',
                #                                         args=[self.repo_id]))
                elif e.msg == 'Incorrect password':
                    raise forms.ValidationError(_(u'Wrong password'))
                elif e.msg == 'Internal server error':
                    raise forms.ValidationError(_(u'Inernal server error'))
                else:
                    raise forms.ValidationError(_(u'Decrypt library error'))
        
class SetUserQuotaForm(forms.Form):
    """
    Form for setting user quota.
    """
    email = forms.CharField(error_messages={'required': _('Email is required')})
    quota = forms.IntegerField(min_value=0,
                               error_messages={'required': _('Quota can\'t be empty'),
                                               'min_value': _('Quota is too low (minimum value is 0)')})

class RepoSettingForm(forms.Form):
    """
    Form for saving repo settings.
    """
    repo_id = forms.CharField(error_messages={'required': _('Repo id is required')})
    repo_name = forms.CharField(error_messages={'required': _('Library name is required')})
    repo_desc = forms.CharField(error_messages={'required': _('Library description is required')})
    days = forms.IntegerField(required=False,
                              error_messages={'invalid': _('Please enter a number')})
