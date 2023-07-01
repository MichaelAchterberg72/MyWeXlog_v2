from dateutil.rrule import (
    DAILY,
    FR,
    HOURLY,
    MINUTELY,
    MO,
    MONTHLY,
    SA,
    SECONDLY,
    SU,
    TH,
    TU,
    WE,
    WEEKLY,
    YEARLY,
)
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from utils.utils import update_model

from django.contrib.auth import get_user_model

User = get_user_model()

freqs = (
    ("YEARLY", _("Yearly")),
    ("MONTHLY", _("Monthly")),
    ("WEEKLY", _("Weekly")),
    ("DAILY", _("Daily")),
    ("HOURLY", _("Hourly")),
    ("MINUTELY", _("Minutely")),
    ("SECONDLY", _("Secondly")),
)


class Rule(models.Model):
    """
    This defines a rule by which an event will recur.  This is defined by the
    rrule in the dateutil documentation.

    * name - the human friendly name of this kind of recursion.
    * description - a short description describing this type of recursion.
    * frequency - the base recurrence period
    * param - extra params required to define this type of recursion. The params
      should follow this format:

        param = [rruleparam:value;]*
        rruleparam = see list below
        value = int[,int]*

      The options are: (documentation for these can be found at
      https://dateutil.readthedocs.io/en/stable/rrule.html#module-dateutil.rrule
        ** count
        ** bysetpos
        ** bymonth
        ** bymonthday
        ** byyearday
        ** byweekno
        ** byweekday
        ** byhour
        ** byminute
        ** bysecond
        ** byeaster
    """

    talent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(_("name"), max_length=32)
    description = models.TextField(_("description"))
    frequency = models.CharField(_("frequency"), choices=freqs, max_length=10)
    params = models.TextField(_("params"), blank=True)

    _week_days = {"MO": MO, "TU": TU, "WE": WE, "TH": TH, "FR": FR, "SA": SA, "SU": SU}

    class Meta:
        verbose_name = _("rule")
        verbose_name_plural = _("rules")
        
    def __str__(self):
        """Human readable string for Rule"""
        return "Rule {} params {}".format(self.name, self.params)
        
    @classmethod
    def update_or_create(cls, id=None, instance=None, **kwargs):
        if id and not instance:
            instance = cls.objects.get(id=id)
            
        talent = kwargs.pop('talent', None)
        
        if instance:
            update_model(instance, **kwargs)
            instance.save()
        else:
            instance = cls.objects.create(**kwargs)
        
        if talent:
            instance.talent = User.objects.get(alias=talent.alias)
        
        instance.save()
            
        return instance

    def rrule_frequency(self):
        compatibility_dict = {
            "DAILY": DAILY,
            "MONTHLY": MONTHLY,
            "WEEKLY": WEEKLY,
            "YEARLY": YEARLY,
            "HOURLY": HOURLY,
            "MINUTELY": MINUTELY,
            "SECONDLY": SECONDLY,
        }
        return compatibility_dict[self.frequency]

    def _weekday_or_number(self, param):
        """
        Receives a rrule parameter value, returns a upper case version
        of the value if its a weekday or an integer if its a number
        """
        try:
            return int(param)
        except (TypeError, ValueError):
            uparam = str(param).upper()
            if uparam in Rule._week_days:
                return Rule._week_days[uparam]

    def get_params(self):
        """
        >>> rule = Rule(params = "count:1;bysecond:1;byminute:1,2,4,5")
        >>> rule.get_params()
        {'count': 1, 'byminute': [1, 2, 4, 5], 'bysecond': 1}
        """
        params = self.params.split(";")
        param_dict = []
        for param in params:
            param = param.split(":")
            if len(param) != 2:
                continue

            param = (
                str(param[0]).lower(),
                [
                    x
                    for x in [self._weekday_or_number(v) for v in param[1].split(",")]
                    if x is not None
                ],
            )

            if len(param[1]) == 1:
                param_value = self._weekday_or_number(param[1][0])
                param = (param[0], param_value)
            param_dict.append(param)
        return dict(param_dict)