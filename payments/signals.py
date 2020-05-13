from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from paypal.standard.models import PayPalStandardBase

from paypal.standard.models import ST_PP_COMPLETED, ST_PP_EXPIRED, ST_PP_PENDING
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
def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    ipn_username = User.objects.get(pk=str(ipn_obj.custom))
    username = ipn_username.email

    if ipn_obj.item_name == "MyWeXlog Passive Subscription":
        price = "4.00"

    elif ipn_obj.item_name == "MyWeXlog 6 Month Passive Subscription":
        price = "22.00"

    elif ipn_obj.item_name == "MyWeXlog 12 Month Passive Subscription":
        price = "43.56"

    elif ipn_obj.item_name == "MyWeXlog Active Subscription" | "MyWeXlog Active Subscription Upgrade":
        price = "5.20"

    elif ipn_obj.item_name == "MyWeXlog 6 Month Active Subscription" | "MyWeXlog 6 Month Active Subscription Upgrade":
        price = "29.20"

    elif ipn_obj.item_name == "MyWeXlog 12 Month Active Subscription" | "MyWeXlog 12 Month Active Subscription Upgrade":
        price = "57.96"

    elif ipn_obj.item_name == "MyWeXlog Passive Subscription - Beta":
        price = "4.00" | "0.00"

    elif ipn_obj.item_name == "MyWeXlog 6 Month Passive Subscription - Beta":
        price = "22.00" | "0.00"

    elif ipn_obj.item_name == "MyWeXlog 12 Month Passive Subscription - Beta":
        price = "43.56" | "0.00"

    elif ipn_obj.item_name == "MyWeXlog Active Subscription - Beta":
        price = "5.20" | "0.00"

    elif ipn_obj.item_name == "MyWeXlog 6 Month Active Subscription - Beta":
        price = "29.20" | "0.00"

    elif ipn_obj.item_name == "MyWeXlog 12 Month Active Subscription - Beta":
        price = "57.96" | "0.00"

     # check for payment received IPN
     # check for subscriber sign-up IPN
     # check for recurring payment IPN
    if ipn_obj.txn_type == "recurring_payment":
        if ipn_obj.payment_status == "Completed":

            if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                # Not a valid payment
                pass

            elif ipn_obj.custom == ipn_username:
                Users.objects.filter(ipn_username).update(paid=True)
                Users.objects.filter(ipn_username).update(paid_date=datetime.now())
                # set passive subscription
                if ipn_obj.item_name == "MyWeXlog Passive Subscription" | "MyWeXlog Passive Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="1")
                    Users.objects.filter(ipn_username).update(paid_type="1")
                elif ipn_obj.item_name == "MyWeXlog 6 Month Passive Subscription" | "MyWeXlog 6 Month Passive Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="1")
                    Users.objects.filter(ipn_username).update(paid_type="2")
                elif ipn_obj.item_name == "MyWeXlog 12 Month Passive Subscription" | "MyWeXlog 12 Month Passive Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="1")
                    Users.objects.filter(ipn_username).update(paid_type="3")
                # set active subscription
                elif ipn_obj.item_name == "MyWeXlog Active Subscription" | "MyWeXlog Active Subscription Upgrade" | "MyWeXlog Active Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="2")
                    Users.objects.filter(ipn_username).update(paid_type="1")
                elif ipn_obj.item_name == "MyWeXlog 6 Month Active Subscription" | "MyWeXlog 6 Month Active Subscription Upgrade" | "MyWeXlog 6 Month Active Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="2")
                    Users.objects.filter(ipn_username).update(paid_type="2")
                elif ipn_obj.item_name == "MyWeXlog 12 Month Active Subscription" | "MyWeXlog 12 Month Active Subscription Upgrade" | "MyWeXlog 12 Month Active Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="2")
                    Users.objects.filter(ipn_username).update(paid_type="3")


            elif ipn_obj.mc_gross != price and ipn_obj.mc_currency != 'USD':
                Users.objects.filter(ipn_username).update(paid=False)
                Users.objects.filter(ipn_username).update(paid_date=datetime.now())
                Users.objects.filter(ipn_username).update(subscription="0")
                if CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.unsubscribe == True:
                    pass
                elif CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.subscription_notifications == False:
                    pass
                else:
                    SubscriptionAmountDifferentTask(username)


        elif ipn_obj.payment_status == "Expired":
            if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                # Not a valid payment
                pass

            elif ipn_obj.custom == ipn_username:
                Users.objects.filter(ipn_username).update(paid=False)
                Users.objects.filter(ipn_username).update(paid_date=datetime.now())
                Users.objects.filter(ipn_username).update(subscription="0")
                if CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.unsubscribe == True:
                    pass
                elif CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.subscription_notifications == False:
                    pass
                else:
                    SubscriptionExpiredTask(username)


        elif ipn_obj.payment_status == "Pending":
            if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                # Not a valid payment
                pass

            elif ipn_obj.custom == ipn_username:
                Users.objects.filter(ipn_username).update(paid=False)
                Users.objects.filter(ipn_username).update(paid_date=datetime.now())
                Users.objects.filter(ipn_username).update(subscription="0")


     # check for subscription payment IPN
    elif ipn_obj.txn_type == "subscr_payment" and ipn_obj.flag == "True":
        if ipn_obj.payment_status == "Completed":

            if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                # Not a valid payment
                pass

            elif ipn_obj.custom == ipn_username:
                Users.objects.filter(ipn_username).update(paid=True)
                Users.objects.filter(ipn_username).update(paid_date=datetime.now())
                # set passive subscription
                if ipn_obj.item_name == "MyWeXlog Passive Subscription" | "MyWeXlog Passive Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="1")
                    Users.objects.filter(ipn_username).update(paid_type="1")
                elif ipn_obj.item_name == "MyWeXlog 6 Month Passive Subscription" | "MyWeXlog 6 Month Passive Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="1")
                    Users.objects.filter(ipn_username).update(paid_type="2")
                elif ipn_obj.item_name == "MyWeXlog 12 Month Passive Subscription" | "MyWeXlog 12 Month Passive Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="1")
                    Users.objects.filter(ipn_username).update(paid_type="3")
                # set active subscription
                elif ipn_obj.item_name == "MyWeXlog Active Subscription" | "MyWeXlog Active Subscription Upgrade" | "MyWeXlog Active Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="2")
                    Users.objects.filter(ipn_username).update(paid_type="1")
                elif ipn_obj.item_name == "MyWeXlog 6 Month Active Subscription" | "MyWeXlog 6 Month Active Subscription Upgrade" | "MyWeXlog 6 Month Active Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="2")
                    Users.objects.filter(ipn_username).update(paid_type="2")
                elif ipn_obj.item_name == "MyWeXlog 12 Month Active Subscription" | "MyWeXlog 12 Month Subscription Upgrade" | "MyWeXlog 12 Month Active Subscription - Beta":
                    Users.objects.filter(ipn_username).update(subscription="2")
                    Users.objects.filter(ipn_username).update(paid_type="3")


            elif ipn_obj.mc_gross != price and ipn_obj.mc_currency != 'USD':
                Users.objects.filter(ipn_username).update(paid=False)
                Users.objects.filter(ipn_username).update(paid_date=datetime.now())
                Users.objects.filter(ipn_username).update(subscription="0")
                if CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.unsubscribe == True:
                    pass
                elif CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.subscription_notifications == False:
                    pass
                else:
                    SubscriptionAmountDifferentTask(username)

            elif ipn_obj.custom == ipn_username and ipn_obj.item_name != "MyWeXlog Active Subscription Upgrade" | "MyWeXlog 6 Month Active Subscription Upgrade" | "MyWeXlog 6 Month Active Subscription Upgrade":
                SubscriptionSignupTask(username)
                SubscriptionUpgradeRefund(ipn_username)

            else:
                pass


        elif ipn_obj.payment_status == "Expired":
            if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                # Not a valid payment
                pass

            elif ipn_obj.custom == ipn_username:
                Users.objects.filter(ipn_username).update(paid=False)
                Users.objects.filter(ipn_username).update(paid_date=datetime.now())
                Users.objects.filter(ipn_username).update(subscription="0")
                if CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.unsubscribe == True:
                    pass
                elif CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.subscription_notifications == False:
                    pass
                else:
                    SubscriptionExpiredTask(username)


        elif ipn_obj.payment_status == "Pending":
            if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
                # Not a valid payment
                pass

            elif ipn_obj.custom == ipn_username:
                Users.objects.filter(ipn_username).update(paid=False)
                Users.objects.filter(ipn_username).update(paid_date=datetime.now())
                Users.objects.filter(ipn_username).update(subscription="0")


     # check for failed subscription payment IPN
    elif ipn_obj.txn_type == "subscr_failed":
        if ipn_obj.custom == ipn_username:
            Users.objects.filter(ipn_username).update(paid=False)
            Users.objects.filter(ipn_username).update(paid_date=datetime.now())
            Users.objects.filter(ipn_username).update(subscription="0")
            if CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.unsubscribe == True:
                pass
            elif CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.subscription_notifications == False:
                pass
            else:
                SubscriptionFailedTask(username)
     # check for subscription cancellation IPN
    elif ipn_obj.txn_type == "subscr_cancel":
        if ipn_obj.custom == ipn_username:
            Users.objects.filter(ipn_username).update(paid=False)
            Users.objects.filter(ipn_username).update(paid_date=datetime.now())
            Users.objects.filter(ipn_username).update(subscription="0")
            if CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.unsubscribe == True:
                pass
            elif CustomUserSettings.talent.filter(ipn_username) and CustomUserSettings.subscription_notifications == False:
                pass
            else:
                SubscriptionCancelledTask(username)

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
