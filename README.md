# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |
| ------------ | ------------ | ------------ |
| *Azure Postgres Database* |   Basic  |       $50.51       |
| *Azure Postgres Database* |   General Purpose  |       $201.91       |
| *Azure Postgres Database* |   Memory Optimized  |       $219.72       |
| *Azure Service Bus*   |      Basic   |       $0.05       |
| *Azure Service Bus*   |      Standard   |       $9.81       |
| *Azure Service Bus*   |      Standard   |       $677.08       |
| *Azure App Service*           |      Free   |         $0.00     |
| *Azure App Service*           |      Basic   |         $13.14    |
| *Azure App Service*           |      Standard   |         $69.35    |
| *Azure App Service*           |      Premium V2   |         $83.95    |
| *Azure App Service*           |      Premium V3   |         $102.93    |
| *Azure App Service*           |      Isolated   |         $1,118.36   |
| *Azure App Service*           |      Isolated V2  |         $302.22   |
| *Azure App Service*           |      Isolated V3  |         $8,304.48   |
|*Azure Function App*|  Consumption      |      $0.00     |
|*Azure Function App*|  Consumption      |      $324.78     |

Because i choose most of the resource at the cheapest pricing tier, so the monthly estimated cost for this project at production level environment is $101.66
## Architecture Explanation
1. The Triggering mail through the web app architecture
   The previos architecture is on-premise. It include: an on-premise database and an on-premmise server.
   **it has some advantages**: simple to build, develop and mantain.
   **But it has some disavantages:**
   - The web app cannot be automatically scalable at peak time when there 's lot of user requests
   - When admin want to send out notification email for all attendees, it will take a lot of time because the app need to loop through all the attendees in DB and send email to each of them. it may cause to high CPU or disk utilization.
   - The current architecture is expensive because the app owner has to take responsibility for upfront-cost
   - There maybe much downtime when deploying because it is low availability.
2. The Azure Queue & Functions architecture
   **The Current Architecture is cloud-based and includes:**
   - An Azure App service to host the web app
   - An Azure Service Bus to transfer data in queue to an azure function app
   - An Azure Function App to hanlde sending email task.
   **it has some disadvantages like **
   - it is more complicated to build, develop and mantain
    **and it has some advantages:**
   - By using App service , The app can be scalable easily at peak time and can turn back to normal level when there few requests.
   - Sending email task is an cpu-hungry task and is outsourced to Azure Service Bus and Azure Function App. So the compute resource for web app might be at high availability.
   - Using Azure Service Bus, the app can be decoupled from sending email task, and message can be transfer to many system with no downtime rather than just one system with normal back-end service.
   - Using Azure Function App, the code is more simple (serverless) and run only when there 's message from Azure Service Bus.
   - The app owner only pay for what they use(Pay as you go model), they don't need to pay for upfront-cost, resulting in being more cost-effective.
