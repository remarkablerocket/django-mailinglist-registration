"""
Forms and validation code for mailinglist registration.

"""


from mailinglist_registration.models import Subscriber
from django import forms
from django.utils.translation import ugettext_lazy as _


class RegistrationForm(forms.Form):
    """
    Form for registering a new mailinglist subscriber.
    
    Validates that the requested email is not already in use.
    
    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected subscriber data is delegated to the active
    registration backend.

    """
    required_css_class = 'required'
    
    email = forms.EmailField(label=_("Email address"))
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].error_messages['required'] = 'Please enter an email address or we\'re not going to get very far.'
        self.fields['email'].error_messages['invalid'] = 'Please enter a valid email address.'
    
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        email_address = self.cleaned_data['email']
        if Subscriber.objects.filter(email__iexact=email_address,is_active=True):
            raise forms.ValidationError(_("%s is already subscribed to our updates!" % email_address))
        if Subscriber.objects.filter(email__iexact=email_address,is_active=False):
            raise forms.ValidationError(_("A verification email has already been sent to %s. Please check your junk mail if you haven't received it." % email_address))
        return self.cleaned_data['email']



class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.
    
    """
    tos = forms.BooleanField(widget=forms.CheckboxInput,
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})


class RegistrationFormNoFreeEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which disallows registration with
    email addresses from popular free webmail services; moderately
    useful for preventing automated spam registrations.
    
    To change the list of banned domains, subclass this form and
    override the attribute ``bad_domains``.
    
    """
    bad_domains = ['aim.com', 'aol.com', 'email.com', 'gmail.com',
                   'googlemail.com', 'hotmail.com', 'hushmail.com',
                   'msn.com', 'mail.ru', 'mailinator.com', 'live.com',
                   'yahoo.com']
    
    def clean_email(self):
        """
        Check the supplied email address against a list of known free
        webmail domains.
        
        """
        email_domain = self.cleaned_data['email'].split('@')[1]
        email_address = self.cleaned_data['email']
        if email_domain in self.bad_domains:
            raise forms.ValidationError(_("Registration using free email addresses is prohibited. Please supply a different email address."))
        if Subscriber.objects.filter(email__iexact=email_address,is_active=True):
            raise forms.ValidationError(_("%s is already subscribed to our updates!" % email_address))
        if Subscriber.objects.filter(email__iexact=email_address,is_active=False):
            raise forms.ValidationError(_("A verification email has already been sent to %s. Please check your junk mail if you haven't received it." % email_address))
        return self.cleaned_data['email']
