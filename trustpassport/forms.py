from django import forms
from django.contrib.auth.models import User

from .models import *


class EnterpriseTrustAddForm(forms.ModelForm):
    class Meta:
        model = EnterprisePassport
        fields = ('score_by','enterprise', 'payment_text','payment_score',
                    'cooperation_text', 'cooperation_score', 'treatment_text', 'treatment_score',
                     'information_text', 'information_score', 'engagement_text', 'engagement_score',
                      'accuracy_text', 'accuracy_score')
        labels = {
            'payment_text': ('What was the ease of receipt of payment practices?'),\
            'cooperation_text': ('What was the level of co-operation?'),
            'treatment_text': ('How did the company treat the contractors?'),
            'information_text': ('What was the accuracy of the information received?'),
            'engagement_text': ('What was the ease of engagement?'),
            'accuracy_text': ('How accurate was the task assessment?'),
            }


class TalentTrustAddForm(forms.ModelForm):
    class Meta:
        model = TalentPassport
        fields = ('score_by','q1_text', 'q1_score','q2_text',
                    'q2_score', 'q3_text', 'q3_score', 'q4_text',
                     'q4_score', 'q5_text', 'q5_score', 'q6_text',
                      'q6_score', 'q7_text', 'q7_score', 'q8_text',
                       'q8_score', 'q9_text', 'q9_score', 'q10_text',
                        'q10_score', 'q12_text', 'q12_score', 'q13_text',
                         'q13_score','q14_text','q14_score','q15_text',
                         'q15_score')
        labels = {
            'q1_text': ('They are consistent?'),
            'q2_text': ('They show compassion and humility?'),
            'q3_text': ('They respect boundries?'),
            'q4_text': ('They compromise and don\'t expect something for nothing?'),
            'q5_text': ('They\'re relaxed (and so are you)?'),
            'q6_text': ('They are respectful when it comes to time?'),
            'q7_text': ('They show gratitude?'),
            'q8_text': ('They give up all the facts, even if it hurts?'),
            'q9_text': ('They confide in you?'),
            'q10_text': ('They aren\'t materialistic or desperate for money?'),
            'q11_text': ('They\'re right a lot?'),
            'q12_text': ('They skip the water cooler gossip?'),
            'q13_text': ('They\'re learners?'),
            'q14_text': ('You know who they\'re connected to\, and they try to connect you?'),
            'q15_text': ('They\'re there for you and others?'),
            }
"""
        help_texts = {
            'q1_text': ('A trustworthy person will use roughly the same behavior and language in '
                        'any situation. THey have the self-control to maintain character and '
                        'follow through on what they say they will do, even when they are tempted '
                        'to walk it back. They won\'t wear different masks or pretend they\'re '
                        'someone they\re not just to impress. Switching gears comes from having '
                        'learned reliable new information, not from self-serving whims. What\'s '
                        'more, what they say matches what you hear from others.'),
            'q2_text': ('Both these traits demonstrate that the person can think of others
                        well and doesn\'t consider themselves as more important than anyone else.
                        Because they are more outwardly focused, they\'re less likely to step
                        on your toes or betray you to get something they need or want.'),
            'q3_text': ('Trustworthy individuals don\'t try to impoes their will on others
                        because they don\'t feel the need to control those around them. They
                        avoid bullying and acknowledge that no means no.'),
            'q4_text': ('Small sacrifices show that the individual recognizes that trust is a
                        two-way street. They\'re willing to give a little to get something back
                        later. And if they ask for something, they're sure to demonstrate the value
                        of their request.'),
            'q5_text': ('A person who is faking it and who is more likely to behave in shady
                        ways useually will display some signs of anxiety, such as agitated body
                        language. If the person seems at ease, they likely have nothing to hide and
                        are being honest and open with you. You\'ll likely feel calm, too,
                        because you won\'t be subconsciously picking up on and mirroring
                        back negitive cues.'),
            'q6_text': ('Trustworthy people do their best not to be late or cancel plans at the
                        last minute because they know doing so inconveniences you and violates
                        promises. They won\'t try to rush or drag things out for their own bennefit.'),
            'q7_text': ('Trustworthy individuals are willing to admit they can\'t do it all alone
                        and value teamwork. They give credit where it\'s due, even if it means
                        they don\'t advance as quickly or shine as much as themselves.'),
            'q8_text': ('Truth and transparency matters to trustworthy people. They won\'t
                        lie by omission or fudge data. They will give up even the information that
                        could put their reputation at risk or create conflict, believing that those
                        conflicts can be solved with good empathy and communication.'),
            'q9_text': ('Confiding in someone, exposing faults and all, involves a certain amount of
                        vulnerability. So when someone confides in you, it demonstrates that the
                        individual already trusts you and that they want you to be open with them, too.'),
            'q10_text': ('While there is zero wrong with having nice things, trustworthy people don\'t
                        put stuff ahead of people. They\'re willing to give up what they have (or
                        could have) to help. Financial stability facilitates trust because it reduces
                        the temptation to treat others poorly out of the need for self-preservation.'),
            'q11_text': ('Because trustworthy people value truth, they are willing to do their
                        homework. They do the research that leads to verifiable conclusions,
                        so they have a track record of having the right answer.'),
            'q12_text': ('Trustworthy individuals don\'t like to make assumptions about anything
                        or anybody. They prefer to get information from the source and to let the source
                        speak for themselves. They avoid rumors because they know that rumors
                        useually include negativity that tears people down instead of building
                        them up. When they do talk, their language is empowering and respectful.),
            'q13_text': ('Individuals who are worth your trust know they don\'t have all the answers.
                        They look for ways to learn and improve themselves constantly, and
                        through that process, they\'re willing to share the resources and facts
                        they find.'),
            'q14_text': ('Both these elements show that the other person sees you as important. They
                        want you to be part of their regular social group and meet the people you
                        need to succeed. Others can affirm or contradict what you know about the
                        individual, too. Subsequently, the more people the individual introduces you
                        to, the more likely it is that they\'re not hiding who they are.'),
            'q15_text': ('Trustworthy people will listen to and support you even when they don\'t
                        need something from you. They do their best to be available to help, whatever
                        you might be going through.'),
        }
"""
