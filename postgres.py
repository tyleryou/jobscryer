from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import os

table = os.environ.get('pg_table')
dbname = os.environ.get('pg_database')
user = os.environ.get('pg_user')
password = os.environ.get('pg_pw')
host = os.environ.get('pg_host')
port = os.environ.get('pg_port')
column_list = [
               'created_date',
               'description',
               'salary',
               'exp_level',
               'region'
               ]


class PGPush:
    def pg_push(self, dbname, column_list, data):
        df = pd.DataFrame(data)
        df = df[df['description'] != '{}']
        try:
            engine = create_engine(
                f'postgresql://{user}:{password}@{host}:{port}/{dbname}')
        except SQLAlchemyError as e:
            print('Error in connecting to database.', e)

# Jobs last around 48 days on the site, so we want to only append
# non-duplicate rows. The below SQL creates an ephemeral table to join with
# the main table and only append rows not already present.
# Descriptions get pulled out as a list, but when appending it into "block"
# in jobscryer, the value in key: value gets saved as a json format.
# I'm not entirely sure why, because older values in the database didn't
# save as json format. But it isn't a big deal and the dirty quick fix
# is to simply cut all the non-necessary punctuation non-alphebetical
# values like {}, ", etc.

        df.to_sql(
            'temp_table', con=engine, index=False, if_exists='replace')
        qry = (
            f"""
                INSERT INTO
                    {table}
                select
                    created_date,
                    regexp_replace(description,
                                   '[^a-zA-Z\d\s.-]', '', 'g') as description,
                    salary,
                    exp_level,
                    region
                from (
                        select
                            *,
                            ROW_NUMBER() OVER (PARTITION BY
                                               created_date,
                                               description,
                                               salary,
                                               exp_level,
                                               region
                                               ) as ct
                        from
                            temp_table
                        left join
                            {table}
                        using
                        (
                            created_date,
                            description,
                            salary,
                            exp_level,
                            region
                        )
                    )
                where
                    ct = 1
                and
                description != ""{{}}"" --No need for empty descriptions
            """
                )

        engine.execute(qry)
#        del_temp = """DROP TABLE temp_table"""
#        engine.execute(del_temp)
