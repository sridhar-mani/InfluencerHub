from celery import Celery
from celery.schedules import crontab
from app import app, mail  
from api.Models.models import Influencer, Adrequest, Sponsor, Campaign  
import requests

def make_celery(app):
    # Define redis_url inside the function before using it
    redis_url = "redis://:hqNoRpztHCBnh46RrKz4QL4CS9xkuScn@redis-10812.c322.us-east-1-2.ec2.redns.redis-cloud.com:10812/0"

    # Initialize Celery instance here
    celery = Celery(app.import_name, broker=redis_url, backend=redis_url)
    
    # Update Celery configuration
    celery.conf.update({
        'broker_transport_options': {'protocol': 3},
        'redis_backend_use_ssl': {'ssl_cert_reqs': 0},
        'beat_schedule': { 
            'send-daily-reminders-everyday-at-8pm': {
                'task': 'celery_app.send_daily_reminders', 
                'schedule': crontab(hour=20, minute=0),
            },
            'send-monthly-activity-report':{
                'task':'celery_app.send_monthly_activity_report',
                'schedule': crontab(day_of_month=1, hour=0, minute=0)
            }
        }
    })

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Initialize celery after defining make_celery
celery = make_celery(app)

@celery.task
def send_daily_reminders():
    # No need for app.app_context() here because ContextTask handles it
    influencers_with_pending_requests = Influencer.query.filter(
        Influencer.ad_requests.any(Adrequest.status == "pending")
    ).all()
    for influencer in influencers_with_pending_requests:
        send_email_via_sender(
            influencer.user.email,
            "Daily Reminder",
            "You have pending ad requests. Please check your dashboard."
        )
    print("Daily reminders sent")

@celery.task
def send_monthly_activity_report():
    # No need for app.app_context() here because ContextTask handles it
    sponsors = Sponsor.query.all()
    for sponsor in sponsors:
        report_html = generate_monthly_activity_report(sponsor)
        send_email_via_sender(
            sponsor.user.email,
            "Monthly Activity Report",
            report_html,
            is_html=True
        )

def generate_monthly_activity_report(sponsor):
    # Corrected variable names and typos
    campaigns = Campaign.query.filter(Campaign.sponsor_id == sponsor.id).all()
    total_campaigns = len(campaigns)
    total_ads = sum([len(c.ads) for c in campaigns])
    total_budget = sum([c.budget for c in campaigns])
    used_budget = sum([c.budget for c in campaigns if c.status == "completed"])
    remaining_budget = total_budget - used_budget

    report_html = f"""
    <html>
        <body>
            <h1>Monthly Activity Report</h1>
            <h2>Sponsor: {sponsor.company_name}</h2>
            <p>Total Campaigns: {total_campaigns}</p>
            <p>Total Advertisements: {total_ads}</p>
            <p>Total Budget: {total_budget}</p>
            <p>Used Budget: {used_budget}</p>
            <p>Remaining Budget: {remaining_budget}</p>
            <h3>Campaign Details:</h3>
            <ul>
    """
    for campaign in campaigns:
        report_html += f"<li>{campaign.name}: {len(campaign.ads)} ads, Budget: {campaign.budget}</li>"
    report_html += """
            </ul>
        </body>
    </html>
    """
    # Return the generated HTML
    return report_html

def send_email_via_sender(to_email, subject, body, is_html=False):
    api_key = app.config['EMAIL_API_KEY']
    api_url = app.config['EMAIL_API_URL']
    api_mail = str(app.config['EMAIL_API_MAIL'])
    data = {
        "apikey": api_key,
        "from": api_mail,
        "subject": subject,
        "recipients": [{"email": to_email}]
    }
    if is_html:
        data["html"] = body
    else:
        data["message"] = body 
    response = requests.post(api_url, json=data)
    if response.status_code == 200:
        print(f"Email sent to {to_email}")
    else:
        print(f"Failed to send email to {to_email}: {response.text}")
