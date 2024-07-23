# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector
from mysql.connector import pooling
from mysql.connector import Error
import hashlib
import os
from dotenv import load_dotenv, dotenv_values


class LinkedinscraperPipeline:
    # Initialization method to open a connection to the sql server
    def __init__(self):
        load_dotenv(override=True)

        self.connPool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = "linkedInPool",
            pool_size=5,
            host = 'host.docker.internal',
            user = os.getenv("USERNAME"),
            password = os.getenv("PASSWORD"),
            database = 'internshipdatabase'
        )

        try:
            self.conn = self.connPool.get_connection()
            self.curr = self.conn.cursor()
        except:
            Error("There was an error connecting to the database")

    # Method automatically called to process the item passed into it from our spider
    def process_item(self, jobItem, spider):
        # Hashing function to hash job title to create unique key
        customID = int(hashlib.sha1(jobItem['title'].encode("utf-8")).hexdigest(), 16)
        # Get the table name
        tableName = jobItem['tableName']
        # Create the insert statement
        self.curr.execute(f"""INSERT INTO {tableName}
                          (id, webid, title, company, location, partialdesc, timeindays, url, fulladdress, exturl, fulldesc) VALUES
                          (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                          (
                            customID,  
                            jobItem['jobID'],
                            jobItem['title'],
                            jobItem['company'],
                            jobItem['location'],
                            jobItem['partDescription'],
                            jobItem['time'],
                            jobItem['url'],
                            None, 
                            None,
                            None,
                          ))
        # Commit the statement
        self.conn.commit()
    
    # Method automatically called when the spider closes
    def close_spider(self, spider):
        self.curr.close()
        self.conn.close()
