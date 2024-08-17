import jobscryer
import postgres
import email_alert
import os

dbname = os.environ.get('pg_database')
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
    def update_ai_jobs_table(self, url):
        obj = jobscryer.AIScryer()
        job_list = obj.scrape(
            url='https://ai-jobs.net', listing_regex='/job/\d+'
            )
        data = obj.extract(url='https://ai-jobs.net', path_list=job_list)
        sender = postgres.PGPush()
        try:
            sender.pg_push(
                dbname=dbname,
                table=os.environ.get('ai_jobs_table'),
                column_list=column_list,
                data=data)
            email_alert.send_alert(
                alert='Success',
                db=dbname,
                table=os.environ.get('ai_jobs_table'),
                exception='')
            print('Pipeline sucess')
        except Exception as e:
            print('Pipeline fail', e)
            email_alert.send_alert(
                alert='Fail',
                db=dbname,
                table=os.environ.get('ai_jobs_table'),
                exception=e
                )

    def daily_update(self):
        schedule = Schedule()
# Searching for multiple job title keywords in United States.
# Job title keywords: "data engineer", "data analyst", "ai", etc
        schedule.update_ai_jobs_table(
            url='https://ai-jobs.net/?cou=238&key=data+engineer&exp=&sal=')
        schedule.update_ai_jobs_table(
            url='https://ai-jobs.net/?cou=238&key=data+analyst&exp=&sal=')
        schedule.update_ai_jobs_table(
            url='https://ai-jobs.net/?cou=238&key=ai&exp=&sal=')
        schedule.update_ai_jobs_table(url='https://ai-jobs.net/' +
                                      '?cou=238&key' +
                                      '=analytics+engineer&exp=&sal=')
        schedule.update_ai_jobs_table(url='https://ai-jobs.net/' +
                                      '?cou=238&key' +
                                      '=machine+learning+engineer&exp=&sal=')


Schedule().daily_update()
