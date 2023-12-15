from django.core.management import BaseCommand
from main.models import NewsletterRecipients, User
import main.mail_utils as mail_utils

class Command(BaseCommand):
    help = 'Tests if sending an email works.'

    def add_arguments(self, parser):
        pass

    subject_de = "Bronze-Gewinner Nationaler ORD-Preis"
    subject_en = "Bronze Winner National ORD Prize"
    message_de = ("<p>Liebe Abonnent:innen des transcriptiones-Newsletters</p>"
                  "<p>Freudig dürfen wir Ihnen mitteilen, dass transcriptiones den Bronze-Pokal des <a href='https://akademien-schweiz.ch/de/medien/medienmitteilungen/2023/adriano-rutz-gewinnt-ersten-schweizer-ord-preis/'>Nationalen ORD-Preises 2023</a> der Akademien der Wissenschaften Schweiz gewonnen hat. Dieser Preis zeichnet Forschende für innovative Praktiken im Bereich Open Research Data (ORD) aus und verfolgt das Ziel, den Wandel zu offenen Forschungspraktiken voranzutreiben. Das diesjährige Motto lautete «Wiederverwendung von Forschungsdaten».</p>"
                  "<p>Wir bedanken uns ganz herzlich bei der Jury, unseren Unterstützer*innen – insbesondere Prof. Dr. Lucas Burkart – und allen User*innen!</p>"
                  "<p>Auf ein weiteres Anwachsen der Community und des Transkriptionsbestands auf <a href='https://transcriptiones.ch'>transcriptiones</a>!</p>"
                  "<p>Mit besten Grüssen</p>"
                  "<p>Ihr transcriptiones-Team</p>")
    message_en = ("<p>Dear subscribers to the transcriptiones newsletter</p>"
                  "<p>We are delighted to share the exciting news that transcriptiones has won bronze at the <a href='https://akademien-schweiz.ch/en/medien/press-releases/2023/adriano-rutz-gewinnt-ersten-schweizer-ord-preis/'>National ORD Prize 2023</a>, awarded by the Swiss Academies of Arts and Sciences. This prize honours researchers for innovative practices in the field of Open Research Data (ORD) and aims to pursue the transformation towards open research practices. This year’s motto was “reuse of research data”.</p>"
                  "<p>Our heartfelt gratitude goes to the jury, our supporters, with special acknowledgment to Prof. Dr. Lucas Burkart, and, most importantly, to all transcriptiones users.</p>"
                  "<p>Here’s to a further growth of the community and the enrichment of our collection of transcriptions on <a href='https://transcriptiones.ch'>transcriptiones</a>!</p>"
                  "<p>Best regards</p>"
                  "<p>Your transcriptiones team</p>")

    plain_message, html_message = mail_utils.create_newsletter_message(subject_en, subject_de, message_en, message_de)

    def do_send_newsletter(self, recipient, plain_message, html_message):
        subject = 'Newsletter: transcriptiones'
        # mail_utils.send_transcriptiones_mail(subject, plain_message, html_message, recipient)
        print(f"Send to {recipient}")


    def handle(self, *args, **options):
        newsletter_recipients = NewsletterRecipients.objects.all()
        active_users = User.objects.filter(is_active=True)
        all_recipients = []

        for recipient in newsletter_recipients:
            all_recipients.append(recipient.email_address)

        for user in active_users:
            if user.email not in all_recipients:
                all_recipients.append(user.email)

        for recipient in all_recipients:
            self.do_send_newsletter(recipient, self.plain_message, self.html_message)
