from django.contrib import admin
from accounts.importer.models import Account, Person
from accounts.importer.forms import AccountForm
from django.contrib.admin.options import IncorrectLookupParameters
from django.core.exceptions import PermissionDenied
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.http import HttpResponseRedirect, Http404
from django.contrib.admin import helpers
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from accounts.interface.client import ImporterClient
from django.contrib.admin.util import unquote
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.forms.formsets import all_valid

class AdminAccount(admin.ModelAdmin):
    form = AccountForm
    client = None
    
    def save_model(self, request, obj, form, change):
        # instead to save the obj to base it's stored on the partner
        uri = None
        if change:
            uri = obj.resource_uri[1:]
        else:
            uri = ''.join(['api/v1/account_lead', '/'])
        client = self.get_client()
        response = None
        try:
            data = form.cleaned_data
            data['birth_date'] = form.cleaned_data['birth_date'].isoformat()
            response = client.post(uri, data)
        except ValueError, e:
            print(e)
        
        message = u'{2} to {1} the account "{0}"'.format(' '.join([obj.first_name, obj.last_name]), 'changed' if change else 'Creation', 'Failed')
        status_code = response.status_code if response else 500
        if status_code == 200:
            message = u'The account "{0}" was {1} {2}'.format(''.join([obj.first_name, obj.last_name]), 'changed' if change else 'created', 'successfully')
        self.message_user(request, message)
        
        return super(AdminAccount, self).save_model(request, obj, form, change)
        
    def get_client(self):
        if not self.client: 
            self.client = ImporterClient(
                                    'http://api.travelbird.info', 
                                    {'username': 'guest@travelbird.nl',
                                     'api_key':  '4fcd19b96bb11f2bc2395b1cb767b2c102fd4acb', #'642bbb7c573da61cc3cd3461e46eef84e8467185',
                                     'format': 'json'
                                 })
        return self.client
    
    def set_account(self, obj):
        account = Account()
        account.resource_uri = obj['resource_uri']
        account.birth_date = obj['birth_date']
        account.city = obj['city']
        account.country = obj['country']
        account.email = obj['email']
        account.first_name = obj['first_name']
        account.last_name = obj['last_name']
        account.gender = obj['gender']
        account.street_name = obj['street_number']
        account.zipcode = obj['zipcode']
        account.lead = obj['lead']
        account.mailing_list = obj['mailing_lists']
        account.phone = obj['phone']
        account.tr_referral = obj['tr_referral']
        account.utm_medium = obj['utm_medium']
        account.utm_source = obj['utm_source']
        
        return account
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        
        if db_field.name == 'mailing_list':
            client = self.get_client()
            response = None
            try:
                response = client.get('api/v1/mailing_list/')
            except ValueError, e:
                pass
            content = response.content['objects'] if response.status_code <= 304 else list()
            kwargs['widget'].choices = [(i['resource_uri'], i['name'], ) for i in content]
        
        return super(AdminAccount, self).formfield_for_dbfield(db_field, **kwargs)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        "The 'change' admin view for this model."
        model = self.model
        opts = model._meta

        client = self.get_client()
        
        response = None
        try:
            response = client.get(''.join([object_id, '/']))
        except ValueError, e:
            pass
        
        status_code = response.status_code if response else 500
        obj = None
        if status_code <= 304:
            obj = self.set_account(response.content)

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and "_saveasnew" in request.POST:
            return self.add_view(request, form_url=reverse('admin:%s_%s_add' %
                                    (opts.app_label, opts.module_name),
                                    current_app=self.admin_site.name))

        ModelForm = self.get_form(request, obj)
        formsets = []
        inline_instances = self.get_inline_instances(request)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, new_object), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix,
                                  queryset=inline.queryset(request))

                formsets.append(formset)

            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, True)
                self.save_related(request, form, formsets, True)
                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)

        else:
            form = ModelForm(instance=obj)
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, obj), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
            self.get_prepopulated_fields(request, obj),
            self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj, form_url=form_url)
    
 
    def changelist_view(self, request, extra_context=None):
        """
        The 'change list' admin view for this model.
        """
        from django.contrib.admin.views.main import ERROR_FLAG
        opts = self.model._meta
        app_label = opts.app_label
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)
        if actions:
            # Add the action checkboxes if there are any actions available.
            list_display = ['action_checkbox'] +  list(list_display)

        ChangeList = self.get_changelist(request)
        try:
            cl = ChangeList(request, self.model, list_display,
                list_display_links, self.list_filter, self.date_hierarchy,
                self.search_fields, self.list_select_related,
                self.list_per_page, self.list_max_show_all, self.list_editable,
                self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given
            # and the 'invalid=1' parameter was already in the query string,
            # something is screwed up with the database, so display an error
            # page.
            if ERROR_FLAG in request.GET.keys():
                return SimpleTemplateResponse('admin/invalid_setup.html', {
                    'title': _('Database error'),
                })
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        # If the request was POSTed, this might be a bulk action or a bulk
        # edit. Try to look up an action or confirmation first, but if this
        # isn't an action the POST will fall through to the bulk edit check,
        # below.
        
        # we need to replace the query_set, root_query_set and reinvoke the get_result on the cl object
        query_set = list()
        
        client = self.get_client()
        
        response = None
        try:
            response = client.get('api/v1/account_lead/')
        except ValueError, e:
            pass
        print response.status_code
        status_code = response.status_code if response else 500
        content = response.content['objects'] if status_code == 200 else list()
        for account in content:
            query_set.append(self.set_account(account))
            
        # add remote and local accounts
        cl.root_query_set = query_set 
        cl.query_set = query_set
        cl.result_list = query_set 
        
        action_failed = False
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

        # Actions with no confirmation
        if (actions and request.method == 'POST' and
                'index' in request.POST and '_save' not in request.POST):
            if selected:
                response = self.response_action(request, queryset=cl.get_query_set(request))
                if response:
                    return response
                else:
                    action_failed = True
            else:
                msg = _("Items must be selected in order to perform "
                        "actions on them. No items have been changed.")
                self.message_user(request, msg)
                action_failed = True

        # Actions with confirmation
        if (actions and request.method == 'POST' and
                helpers.ACTION_CHECKBOX_NAME in request.POST and
                'index' not in request.POST and '_save' not in request.POST):
            if selected:
                response = self.response_action(request, queryset=cl.get_query_set(request))
                if response:
                    return response
                else:
                    action_failed = True

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if (request.method == "POST" and cl.list_editable and
                '_save' in request.POST and not action_failed):
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(request.POST, request.FILES, queryset=cl.result_list)
            if formset.is_valid():
                changecount = 0
                for form in formset.forms:
                    if form.has_changed():
                        obj = self.save_form(request, form, change=True)
                        self.save_model(request, obj, form, change=True)
                        self.save_related(request, form, formsets=[], change=True)
                        change_msg = self.construct_change_message(request, form, None)
                        self.log_change(request, obj, change_msg)
                        changecount += 1

                if changecount:
                    if changecount == 1:
                        name = force_unicode(opts.verbose_name)
                    else:
                        name = force_unicode(opts.verbose_name_plural)
                    msg = ungettext("%(count)s %(name)s was changed successfully.",
                                    "%(count)s %(name)s were changed successfully.",
                                    changecount) % {'count': changecount,
                                                    'name': name,
                                                    'obj': force_unicode(obj)}
                    self.message_user(request, msg)

                return HttpResponseRedirect(request.get_full_path())

        # Handle GET -- construct a formset for display.
        elif cl.list_editable:
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=list(cl.result_list))

        # Build the list of media to be used by the formset.
        if formset:
            media = self.media + formset.media
        else:
            media = self.media

        # Build the action form and populate it with available actions.
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
        else:
            action_form = None

        selection_note_all = ungettext('%(total_count)s selected',
            'All %(total_count)s selected', cl.result_count)

        context = {
            'module_name': force_unicode(opts.verbose_name_plural),
            'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': selection_note_all % {'total_count': cl.result_count},
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'media': media,
            'has_add_permission': self.has_add_permission(request),
            'app_label': app_label,
            'action_form': action_form,
            'actions_on_top': self.actions_on_top,
            'actions_on_bottom': self.actions_on_bottom,
            'actions_selection_counter': self.actions_selection_counter,
        }
        context.update(extra_context or {})

        return TemplateResponse(request, self.change_list_template or [
            'admin/%s/%s/change_list.html' % (app_label, opts.object_name.lower()),
            'admin/%s/change_list.html' % app_label,
            'admin/change_list.html'
        ], context, current_app=self.admin_site.name)


admin.site.register(Account, AdminAccount)
admin.site.register(Person)
