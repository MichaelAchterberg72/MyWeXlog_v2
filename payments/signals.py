from datetime import datetime
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
#from paypal.standard.models import PayPalStandardBase
from users.models import CustomUser, CustomUserSettings
#from paypal.standard.models import ST_PP_COMPLETED, ST_PP_EXPIRED, ST_PP_PENDING
from paypal.standard.ipn.signals import valid_ipn_received

from .tasks import (
        SubscriptionAmountDifferentTask,
        SubscriptionExpiredTask,
        SubscriptionSignupTask,
        SubscriptionCancelledTask,
        SubscriptionFailedTask,
        SubscriptionUpgradeRefund,
)

# from M2Crypto import BIO, SMIME, X509
from django.conf import settings


@receiver(valid_ipn_received)
def show_me_the_money(sender, instance, **kwargs):
    ipn_obj = instance
    ipn_username = CustomUser.objects.get(pk=ipn_obj.custom)
    username = ipn_username.email
    CustomUserSettingsUser = CustomUserSettings.objects.get(talent=ipn_username.pk)

#    import pdb
#    pdb.set_trace()

    if ipn_obj.item_name == "MyWeXlog Passive Subscription":
        price = "4.00"

    elif ipn_obj.item_name == "MyWeXlog 6 Month Passive Subscription":
        price = "22.00"

    elif ipn_obj.item_name == "MyWeXlog 12 Month Passive Subscription":
        price = "43.56"

    elif ipn_obj.item_name == "MyWeXlog Active Subscription" or "MyWeXlog Active Subscription Upgrade":
        price = "5.20"

    elif ipn_obj.item_name == "MyWeXlog 6 Month Active Subscription" or "MyWeXlog 6 Month Active Subscription Upgrade":
        price = "29.20"

    elif ipn_obj.item_name == "MyWeXlog 12 Month Active Subscription" or "MyWeXlog 12 Month Active Subscription Upgrade":
        price = "57.96"

    elif ipn_obj.item_name == "MyWeXlog Passive Subscription - Beta":
        price = "4.00" or "0.00"

    elif ipn_obj.item_name == "MyWeXlog 6 Month Passive Subscription - Beta":
        price = "22.00" or "0.00"

    elif ipn_obj.item_name == "MyWeXlog 12 Month Passive Subscription - Beta":
        price = "43.56" or "0.00"

    elif ipn_obj.item_name == "MyWeXlog Active Subscription - Beta":
        price = "5.20" or "0.00"

    elif ipn_obj.item_name == "MyWeXlog 6 Month Active Subscription - Beta":
        price = "29.20" or "0.00"

    elif ipn_obj.item_name == "MyWeXlog 12 Month Active Subscription - Beta":
        price = "57.96" or "0.00"

    else:
        pass

     # check for payment received IPN
     # check for subscriber sign-up IPN
     # check for recurring payment IPN
    if ipn_obj.txn_type == "subscr_payment":

        if ipn_obj.flag == True:

            if ipn_obj.payment_status == "Completed":

                if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                    # Not a valid payment
                    pass

                elif ipn_obj.mc_gross != price and ipn_obj.mc_currency != 'USD':
                    ipn_username.paid = False
                    ipn_username.paid_date = timezone.now()
                    ipn_username.subscription = 0
                    if CustomUserSettingsUser.unsubscribe == True:
                        pass
                    elif CustomUserSettingsUser.subscription_notifications == False:
                        pass
                    else:
#                        SubscriptionAmountDifferentTask(ipn_username)
                        pass

                elif ipn_obj.custom:

                    if "Upgrade" in ipn_obj.item_name:
                        if "Active" in ipn_obj.item_name:
                            ipn_username.subscription = 2
                            ipn_username.paid = True
                            ipn_username.paid_date = timezone.now()
#                            SubscriptionSignupTask(ipn_username)
#                            SubscriptionUpgradeRefund(ipn_username, username)

                            if "Monthly" in ipn_obj.item_name:
                                ipn_username.paid_type = 1
                                if "Beta" in ipn_obj.item_name:
                                    ipn_username.role = 1

                            elif "6 Month" in ipn_obj.item_name:
                                ipn_username.paid_type = 2
                                if "Beta" in ipn_obj.item_name:
                                    ipn_username.role = 1

                            elif "12 Month" in ipn_obj.item_name:
                                ipn_username.paid_type = 3
                                if "Beta" in ipn_obj.item_name:
                                    ipn_username.role = 1

                    elif "Passive" in ipn_obj.item_name:
                        ipn_username.subscription = 1
                        ipn_username.paid = True
                        ipn_username.paid_date = timezone.now()
                        if "Monthly" in ipn_obj.item_name:
                            ipn_username.paid_type = 1
                            if "Beta" in ipn_obj.item_name:
                                ipn_username.role = 1

                        elif "6 Month" in ipn_obj.item_name:
                            ipn_username.paid_type = 2
                            if "Beta" in ipn_obj.item_name:
                                ipn_username.role = 1

                        elif "12 Month" in ipn_obj.item_name:
                            ipn_username.paid_type = 3
                            if "Beta" in ipn_obj.item_name:
                                ipn_username.role = 1

                    elif "Active" in ipn_obj.item_name:
                        ipn_username.subscription = 2
                        ipn_username.paid = True
                        ipn_username.paid_date = timezone.now()

                        if "Monthly" in ipn_obj.item_name:
                            ipn_username.paid_type = 1
                            if "Beta" in ipn_obj.item_name:
                                ipn_username.role = 1

                        elif "6 Month" in ipn_obj.item_name:
                            ipn_username.paid_type = 2
                            if "Beta" in ipn_obj.item_name:
                                ipn_username.role = 1

                        elif "12 Month" in ipn_obj.item_name:
                            ipn_username.paid_type = 3
                            if "Beta" in ipn_obj.item_name:
                                ipn_username.role = 1


            elif ipn_obj.payment_status == "Expired":
                if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                    # Not a valid payment
                    pass

                elif ipn_obj.custom:
                    ipn_username.paid = False
                    ipn_username.paid_date = timezone.now()
                    ipn_username.subscription = 0
                    if CustomUserSettingsUser.unsubscribe == True:
                        pass
                    elif CustomUserSettingsUser.subscription_notifications == False:
                        pass
                    else:
#                        SubscriptionExpiredTask(ipn_username)
                        pass

            elif ipn_obj.payment_status == "Pending":
                if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                    # Not a valid payment
                    pass

                elif ipn_obj.custom:
                    ipn_username.paid = False
                    ipn_username.paid_date = timezone.now()
                    ipn_username.subscription = 0




         # check for failed subscription payment IPN
    elif ipn_obj.txn_type == "subscr_failed":
        if ipn_obj.custom:
            ipn_username.paid = False
            ipn_username.paid_date = timezone.now()
            ipn_username.subscription = 0
            if CustomUserSettingsUser.unsubscribe == True:
                pass
            elif CustomUserSettingsUser.subscription_notifications == False:
                pass
            else:
#                    SubscriptionFailedTask(ipn_username)
                pass
     # check for subscription cancellation IPN
    elif ipn_obj.txn_type == "subscr_cancel":
        if ipn_obj.custom:
            if CustomUserSettingsUser.unsubscribe == True:
                pass
            elif CustomUserSettingsUser.subscription_notifications == False:
                pass
            else:
#                    SubscriptionCancelledTask(ipn_username)
                pass

    ipn_username.save()


valid_ipn_received.connect(show_me_the_money)


class PaypalOrder(dict):
    """Acts as a dictionary which can be encrypted to Paypal's EWP service"""
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self['cert_id'] = settings.MY_CERT_ID

    def set_notify_url(self, notify_url):
        self['notify_url'] = notify_url

    # snip more wrapper functions
    def plaintext(self):
        """The plaintext for the cryptography operation."""
        s = ''
        for k in self:
            s += u'%s=%s\n' % (k, self[k])
        return s.encode('utf-8')

    __str__ = plaintext

    def encrypt(self):
        """Return the contents of this order, encrypted to Paypal's
        certificate and signed using the private key configured in the
        Django settings."""

        # Instantiate an SMIME object.
        s = SMIME.SMIME()

        # Load signer's key and cert.
        s.load_key_bio(
            BIO.openfile(settings.MY_KEYPAIR),
            BIO.openfile(settings.MY_CERT)
        )

        # Sign the buffer.
        p7 = s.sign(
            BIO.MemoryBuffer(self.plaintext()),
            flags=SMIME.PKCS7_BINARY
        )

        # Load target cert to encrypt the signed message to.
        x509 = X509.load_cert_bio(BIO.openfile(settings.PAYPAL_CERT))
        sk = X509.X509_Stack()
        sk.push(x509)
        s.set_x509_stack(sk)

        # Set cipher: 3-key triple-DES in CBC mode.
        s.set_cipher(SMIME.Cipher('des_ede3_cbc'))

        # Create a temporary buffer.
        tmp = BIO.MemoryBuffer()

        # Write the signed message into the temporary buffer.
        p7.write_der(tmp)

        # Encrypt the temporary buffer.
        p7 = s.encrypt(tmp, flags=SMIME.PKCS7_BINARY)

        # Output p7 in mail-friendly format.
        out = BIO.MemoryBuffer()
        p7.write(out)

        return out.read()
