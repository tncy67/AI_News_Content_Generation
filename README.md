# AI_News_Content_Generation


This README provides an overview of a sample project I completed while my students at Southern Methodist University were working on their Data Science Capstone Project. The project showcases how to utilize free tools and services (Google Sheet, Google News, Blogger, youtube api, make.com, pythonanywhere, cursor ai, openai, claude, dall-e) for automated content generation, image creation, and blog posting without significant manual intervention.

### Project Overview

The main goal of this project is to create an automated workflow that:

    Generates content based on a few prompts.
    Dumps the content into a Google Sheet or a local Word document or Google Sheet.
    Tags each document with a date.
    Uses AI to create related images (not included in the current repository).
    Constructs search phrases to find relevant YouTube videos and integrates them into the generated articles.
    Automates posting the content on a Blogger account.

The project aims to showcase the potential of modern AI tools for rapid content creation and publication, focusing on efficiency rather than perfection. The entire setup was completed in under two hours, demonstrating what is achievable within a short timeframe using free or low-cost resources.

### Tools & Services Used

1. Cursor (https://www.trycursor.com/)

    This tool helps with content generation using short prompts. Only minor manual adjustments were required.
    After feeding a half dozen short prompts, the AI-generated most of the content, which was then refined and used in the project.

2. Google Sheets

    Used to store the generated content.
    Provides easy integration with Make.com for automation.

3. Local Word Document

    Optionally, the content can be dumped into a Word document and tagged by the date for local storage.

4. OpenAI DALL-E

    AI image creation for the articles, though images are excluded from the repository for now.

5. YouTube Search Integration

    The generated content includes search phrases to find relevant YouTube videos, which are then integrated into the articles.
    In the two dozen test runs conducted, the system made only a few mistakes when retrieving videos.

6. Make.com

    Used to automate the process from Google Sheets to Blogger.
    After connecting the Google Sheets module to your spreadsheet, the content is passed to the Blogger module for automatic posting.
    For automation, you need to create a Blogger account and authorize Make.com’s Blogger module.

7. Google Cloud Console for API Authentication

    You'll need to create a credentials.json file for OAuth authentication.
    Follow these steps:
        Go to https://console.cloud.google.com/.
        Navigate to API & Services > Credentials.
        Create credentials for OAuth client ID, with the application type set to Web.
        Once you've obtained the credentials, during the first run, the script will prompt for Google authorization. Once successful, it will create a token.json file for future authentication.

8. Blogger

    The final step is to create a Blogger account where the content generated from Google Sheets will be posted automatically.
    You can view the live blog posts at: https://ainewsgenbot.blogspot.com/

9. Test Runs

    Over two dozen test runs were conducted; local and PythonAnywhere task scheduling, during which minimal errors occurred. This demonstrated the system's efficiency and reliability in automating content creation and publication.

### Setup Instructions

Step 1: Install Required Libraries

To replicate this project, you'll need to install the following Python libraries:

on bash console in pythonanywhere or local machine:

    pip install anthropic
    pip install openai
    pip install python-dotenv
    pip install google-auth-oauthlib
    pip install beautifulsoup4

Step 2: Set Up Google API Authentication

    Go to the Google Cloud Console.
    Navigate to API & Services > Credentials.
    Create credentials:
        Select OAuth client ID.
        Set the application type to "Web".
    Download the credentials.json file.
    During the first run of your script, it will prompt you for Google authorization. Once authenticated, a token.json file will be generated for future access.

Step 3: Set Up Make.com

    Create a free account on Make.com.
    Connect the Google Sheets module to the spreadsheet where the AI-generated content will be stored.
    Set up the Blogger module and authorize it to connect to your Blogger account for automatic posting.

[Current Google Sheet](https://docs.google.com/spreadsheets/d/1FDPMxqwd2op4sCvKBKq7w9X1h9l4JLN00qX5SQ4joio/)

Step 4: Run the Script

After setting up the credentials and automation:

    Run the content generation process via Cursor or OpenAI.
    Store the generated content in Google Sheets or a Word document.
    Make.com will handle the automation and post the content to Blogger.

### Costs and Resources

    In all test runs, the total cost incurred was:
        $2 for OpenAI’s Claude.
        $2 for DALL-E image generation.

### Free Tools

    Cursor, Google Sheets, Make.com (free plan), PythonAnywhere (free plan for lightweight tasks).

### Important Notes

The focus of this project was on rapid deployment and automation rather than the cleanliness of the final blog posts. The blog content reflects the output from the automated systems with minimal post-editing.

This project demonstrates how to utilize freely available or low-cost tools to achieve a significant level of automation in content generation and publishing.


Conclusion

This project highlights the potential of AI-driven tools and services to automate content creation and publication within a short period. By using tools like Cursor, OpenAI, ChatGPT, Dall-e, Claude, Google Sheets, Make.com, PythonAnywhere, and Blogger, you can quickly set up a system that streamlines the content creation process with minimal cost and effort.

Feel free to explore the blog where the content was posted automatically: https://ainewsgenbot.blogspot.com/.


# Added o1-preview
## UPDATE
To test the capabilities of o1-preview, that's been released today, I passed the same initial prompt to it and get the result in generate_by_o1.py file.

Even this readme is created by AI :).
