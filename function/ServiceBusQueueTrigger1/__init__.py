import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s', notification_id)

    msg, subject = None, None

    # TODO: Get connection to database
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_URL"],
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PW"]
    )

    try:
        # TODO: Get notification message and subject from database using the notification_id
        cursor = conn.cursor()
        cmd = f"SELECT message, subject FROM notification WHERE id={notification_id}"
        cursor.execute(cmd)
        msgs = cursor.fetchall()

        for row in msgs:
            msg = row[0]
            subject = row[1]

        if not msg or not subject:
            logging.error("No msg or subject")
            raise Exception("No msg or subject")

        # TODO: Get attendees email and name
        # TODO: Loop through each attendee and send an email with a personalized subject
        cmd = f"SELECT first_name, email FROM attendee"
        cursor.execute(cmd)
        attendees = cursor.fetchall()

        attendee_count = 0

        for row in attendees:
            fname = row[0]
            email = row[1]

            message = Mail(
                from_email=os.environ['ADMIN_EMAIL_ADDRESS'],
                to_emails=email,
                subject=fname+" "+subject,
                plain_text_content=msg
            )

            sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
            sg.send(message)

            attendee_count += 1

        # TODO: Update the notification table by setting the completed date
        # and updating the status with the total number of attendees notified
        status_msg = f"Notified {str(attendee_count)} attendees"
        curr_date = datetime.now()

        cmd = """UPDATE notification
                    SET status = %s
                    WHERE id = %s"""
        cursor.execute(cmd, (status_msg, notification_id))

        cmd = """UPDATE notification
                    SET completed_date = %s
                    WHERE id = %s"""
        cursor.execute(cmd, (curr_date, notification_id))
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        conn.close()
