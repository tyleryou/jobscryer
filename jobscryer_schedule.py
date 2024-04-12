import jobscryer
import postgres
import email_alert
import os

dbname = os.environ.get('pg_database')
user = os.environ.get('pg_user')
password = os.environ.get('pg_pw')
host = os.environ.get('pg_host')
column_list = ['created_date',
               'description',
               'salary',
               'exp_level',
               'region']


class Schedule:
    def update_table(self):

        obj = jobscryer.Scryer()
        sender = postgres.PGPush()

        job_list = obj.clicker()

        data = obj.extracter(job_list)
        try:
            sender.pg_push(dbname, column_list, data)
            email_alert(alert='Success', db=dbname)
            print('Pipeline sucess')
        except Exception as e:
            print('Pipeline fail', e)
            email_alert(alert='Fail', db=dbname)
