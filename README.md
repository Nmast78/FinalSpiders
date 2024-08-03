# Job Website Scraping Spiders
Website that tracks the location and astronauts aboard the International Space Station in real time.

# About
This project uses the Scrapy framework to scrape popular job websites, including Indeed, LinkedIn, Google Jobs, and Zip Recruiter. I designed the spiders to specifically look for internships in the 50 US states.  The spiders also have the ability to send data directly to a relational database for easy storage and retrieval.  I have used docker to run the spiders in a linux environment where the browser library [![](https://img.shields.io/badge/Playwright-green)](https://playwright.dev/) can render javascript if the website needs to.  I am currently working on a Typescript-React frontend to display jobs in a simple and effective manner.
