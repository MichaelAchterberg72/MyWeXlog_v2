from django import forms

class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list':'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'

        return (text_html + data_list)

    # the "name" parameter will allow you to use the same widget more than once in the same
    # form, not setting this parameter differently will cuse all inputs display the same list.
'''
    # to be inserted inside form

    def __init__(self, *args, **kwargs):
        _country_list = kwargs.pop('data_list', None)
        super(SiteDemandSkillStatsFilter, self).__init__(*args, **kwargs)

        self.fields['designation'].widget = ListTextWidget(data_list=Designation.objects.all().only('name'), name='designation-list')
        self.fields['title'].widget = ListTextWidget(data_list=TalentRequired.objects.all().values_list('title', flat=True).distinct(), name='title-list')
'''
