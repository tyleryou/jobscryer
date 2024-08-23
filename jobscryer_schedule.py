import jobscryer
import postgres
import email_alert
import requests
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
    def push_data(self, table, data):
        sender = postgres.PGPush()
        try:
            sender.pg_push(
                dbname=dbname,
                table=table,
                column_list=column_list,
                data=data)
            email_alert.send_alert(
                alert='Success',
                db=dbname,
                table=table,
                exception='')
            print('Pipeline sucess')
        except Exception as e:
            print('Pipeline fail', e)
            email_alert.send_alert(
                alert='Fail',
                db=dbname,
                table=table,
                exception=e
                )

    def update_ai_jobs_table(self, url):
        obj = jobscryer.AIScryer()
        job_list = obj.scrape(
            text=requests.get(url).text,
            listing_regex=r'/job/\d+'
            )
        data = obj.extract(url='https://ai-jobs.net', path_list=job_list)
        self.push_data(data=data, table=os.environ.get('ai_jobs_table'))

    def update_remotive_table(self, url):
        obj = jobscryer.RemotiveScryer()
        text = obj.button_press(url=url,
                                button_path='//*[@id="morejobs"]/button',
                                popup_path='//*[@id=\'close-join' +
                                '-accelerator-popup\']'
                                )
        job_list = obj.scrape(
            text=text,
            listing_regex=r'https://remotive\.com' +
            r'/remote-jobs/[a-z-]+/[a-z-]+-\d+'
            )
        # Only passing in job_list because I was able to scrape the full URLs
        # for the job links. Extract handles the paths as url+path_list
        data = obj.extract(url='', path_list=job_list)
        self.push_data(data=data, table=os.environ.get('remotive_table'))

    def daily_update(self):
        schedule = Schedule()
# Searching for multiple job title keywords in United States.
# Job title keywords: "data engineer", "data analyst", "ai", etc
        ai_url_list = [
            'https://aijobs.net/?cou=238&reg=7' +
            '&key=data+engineer&exp=&sal=',
            'https://aijobs.net/?cou=238&reg=7' +
            '&key=data+analyst&exp=&sal=',
            'https://aijobs.net/?cou=238&reg=7' +
            '&key=analytics+engineer&exp=&sal=',
            'https://aijobs.net/?cou=238&reg=7' +
            '&key=business+intelligence&exp=&sal=',
            'https://aijobs.net/?cou=238&reg=7' +
            '&key=software+engineer&exp=&sal=',
            'https://aijobs.net/?cou=238&reg=7' +
            '&key=machine+learning&exp=&sal='
            ]

        remotive_url_list = [
            'https://remotive.com/?query=data%20engineer',
            'https://remotive.com/?query=data%20analyst',
            'https://remotive.com/?query=analytics%20engineer',
            'https://remotive.com/?query=business%20intelligence',
            'https://remotive.com/?query=software%20engineer',
            'https://remotive.com/?query=machine%20learning',
            ]
        for url in ai_url_list:
            schedule.update_ai_jobs_table(url=url)
        for url in remotive_url_list:
            schedule.update_remotive_table(url=url)


Schedule().daily_update()
