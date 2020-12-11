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
| *Azure Postgres Database* |  Basic, Single Server   |   Compute: €0.029/hour, Storage: GB/month €0.085, Locally redundant GB/month   €0.085 |
| *Azure Service Bus*   |  Basic       | €0.043 per million operations             |
| *App Service Plan*                  |   F1      |      Free        |
| *App Service* | Leverages App Service Plan | - |
| *Azure Storage Account*  | Standard | €0.049/GB per month |
| *Azure Function* | monthly free grant of 1 million requests and 400,000 GB-s of resource consumption per month per subscription in pay-as-you-go pricing across all function apps in that subscription | After free tier : €0.000014/GB-s, €0.169 per million executions |

Estimated pricing per month: €21,34*

*Calculated with free tier usage and full database compute usage for a month inlcuding backup and storage < 1GB.

## Architecture Explanation
This is a placeholder section where you can provide an explanation and reasoning for your architecture selection for both the Azure Web App and Azure Function.

Since the previous version of the conference webapp experienced HTTP timeouts when notifying attendees, a microservice architectural approach, including Azure Functions to outsource tasks of the main application, is more effiecient and effective. Notifications are now send to a Service Bus message queue which triggers an Azure Function to send out notifaction emails to the given attendees that signed up.

With this microservice architecture, there are different code units, spread on different services, doing tasks outside of the main application. It is easier to work on them seperately and debugging them in case of bugs is a lot easier. Then main application will still be available in case of an Azure Function bug for example.

Computing processes to work on sending the notification emails to the attendees are now outsourced into Azure Functions (Faas) and Service Bus queues which allows the main webapp to spare those resources for other incoming requests and workloads.
