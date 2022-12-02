import logging
import azure.functions as func
import psycopg2 
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):
    logging.info(msg.get_body().decode())
    notification_id = msg.get_body().decode('utf-8')
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)
    # TODO: Get connection to database
    db_name = os.environ.get('db_name')
    db_user= os.environ.get('db_user')
    db_password= os.environ.get('db_password')
    url = os.environ.get('db_url')
    send_grid_api_key = os.environ.get('send_grid_api_key')
    admin_email = os.environ.get('admin_email')
    conn = psycopg2.connect( host = url, database=db_name, user=db_user, password=db_password)
    cur = conn.cursor()
    try:
        # TODO: Get notification message and subject from database using the notification_id
        cur.execute('SELECT message, subject FROM notification WHERE id = {}'.format(notification_id))
        notification = cur.fetchall()
        message = notification[0][0]
        subject = notification[0][1]
        # TODO: Get attendees email and name
        cur.execute('SELECT first_name, email FROM attendee')
        attendees = cur.fetchall()
        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            email_subject = '{} to {}- {}'.format('This is an email from HuynhNN', attendee[0], subject)
            sg = SendGridAPIClient(send_grid_api_key)
            mail_message = Mail(
                from_email=admin_email,
                to_emails=attendee[1],
                subject=email_subject,
                plain_text_content=message)
            sg.send(mail_message)
        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        completed_date = datetime.utcnow()
        status = 'Notified {} attendees'.format(len(attendees))
        sql = """
                UPDATE notification
                 SET "status" = '{}', "completed_date" = '{}'
                 WHERE id = {}
        """
        cur.execute(sql.format(status, completed_date, notification_id))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        cur.close()
        conn.close()
        logging.info('close connection')
