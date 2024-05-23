import jobscryer
import postgres
import email_alert
import os

dbname = os.environ.get('pg_database')
user = os.environ.get('pg_user')
password = os.environ.get('pg_pw')
host = os.environ.get('pg_host')
column_list = [
               'created_date',
               'description',
               'salary',
               'exp_level',
               'region',
               'title',
               'location',
               'remote_first'
               ]


class Schedule:
    def update_table(self, url):
        obj = jobscryer.Scryer()
        job_list = obj.scrape(url)
        data = obj.extracter(url='https://ai-jobs.net', path_list=job_list)
        sender = postgres.PGPush()
        try:
            sender.pg_push(dbname, column_list, data)
            email_alert.send_alert(alert='Success', db=dbname)
            print('Pipeline sucess')
        except Exception as e:
            print('Pipeline fail', e)
            email_alert.send_alert(alert='Fail', db=dbname)

    def daily_update(self):
        schedule = Schedule()
# Searching for multiple job title keywords in United States.
# Job title keywords: "data engineer", "data analyst", "ai"
        schedule.update_table(
            url='https://ai-jobs.net/?cou=238&key=data+engineer&exp=&sal=')
        schedule.update_table(
            url='https://ai-jobs.net/?cou=238&key=data+analyst&exp=&sal=')
        schedule.update_table(
            url='https://ai-jobs.net/?cou=238&key=ai&exp=&sal=')
