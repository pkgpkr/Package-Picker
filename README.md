![ML Pipeline Tests](https://github.com/pkgpkr/Package-Picker/workflows/Scraper%20Test%20CI/badge.svg) ![ML Pipeline Deploy](https://github.com/pkgpkr/Package-Picker/workflows/Deploy%20ML%20Pipeline%20to%20Amazon%20ECS/badge.svg) ![Webserver Tests](https://github.com/pkgpkr/Package-Picker/workflows/Webserver%20Django%20CI/badge.svg) ![Webserver Deploy](https://github.com/pkgpkr/Package-Picker/workflows/Deploy%20to%20Amazon%20ECS/badge.svg)

# Intro

Package Picker is a recommendation platform for JavaScript packages. It uses machine learning to predict packages that are frequently used with the packages in your projects. Check it out at [pkgpkr.com](http://pkgpkr.com).

# Get the code

NOTE: If you do not know the git CLI commands, recommend to use [sourcetree](https://www.sourcetreeapp.com/) or [gitkraren](https://www.gitkraken.com/).

1. git clone https://github.com/pkgpkr/Package-Picker.git to your local folder 
2. create a branch locally for your small features.
3. start coding.
4. make commits frequently

# Set environment variables

```
AWS_ACCESS_KEY_ID.    # Your AWS account's access key
AWS_SECRET_ACCESS_KEY # Your AWS account's secret access key
CLIENT_ID             # ID of the GitHub app used by the web server
CLIENT_SECRET         # Secret for the GitHub app
DB_HOST               # Database URL
DB_PASSWORD           # Database password
DB_USER               # Database user
DOMAIN_NAME           # The domain name where the site is hosted
MONTH                 # How many months of data to scrape
SELENIUM_TEST         # Set if running Selenium tests
TOKEN                 # Your GitHub API token
```

# Run locally

NOTE: Before running any of the components, set the environment variables listed above and install Docker.

## Data scraper

1. Switch to the `pipeline/` folder and build the Docker image.

```
cd pipeline
docker build --build-arg TOKEN=$TOKEN --build-arg MONTH=$MONTH --build-arg DB_USER=$DB_USER --build-arg DB_HOST=$DB_HOST --build-arg=DB_PASSWORD=$DB_PASSWORD .
```

2. Run the Docker image. It will automatically scrape data and train the model, and quit when done.

`docker run -i -t <id>`

### Testing

Run this inside the `pipeline/` folder.

`DB_USER=$DB_USER DB_PASSWORD=$DB_PASSWORD DB_HOST=$DB_HOST TOKEN=$TOKEN python3 -m unittest scraper/test.py -v`

## Web server

1. Switch to the `webserver/pkgpkr/` folder and build the Docker image.

```
cd webserver/pkgpkr
docker build --build-arg DOMAIN_NAME=$DOMAIN_NAME --build-arg CLIENT_ID=$CLIENT_ID --build-arg CLIENT_SECRET=$CLIENT_SECRET --build-arg DB_USER=$DB_USER --build-arg DB_PASSWORD=$DB_PASSWORD --build-arg DB_HOST=$DB_HOST .
```

2. Run the Docker image (remember the `-p` flag to expose the webserver port)

`docker run -i -t -p 80:80 <id>`

3. When the web server starts, open your browser to http://localhost:8000

### Testing

Run this inside the `webserver/pkgpkr` folder.

```
python3 manage.py collectstatic
SELENIUM_TEST=1 CLIENT_ID=$CLIENT_ID CLIENT_SECRET=$CLIENT_SECRET DB_HOST=$DB_HOST DB_USER=$DB_USER DB_PASSWORD=$DB_PASSWORD python3 manage.py test
```

# Run on AWS

## Relational Database Service (RDS)

1. Create a new PostgreSQL instance.

2. If you want to use this database for local testing.

    1. Make sure it's in a security group that allows inbound traffic (if you want to use the database while testing locally).
    
    2. Configure the database to have public accessibly.


## Elastic Container Service (ECS)

1. Create an Elastic Container Registry (ECR) named `pkgpkr`.

`aws ecr create-repository --repository-name pkgpkr --region us-east-1`

2. Create a ECS cluster named `default` and a service named `pkgpkr-web`. The service must support Fargate and have a Load Balancer assigned to it. Follow the [Getting Started](https://us-east-1.console.aws.amazon.com/ecs/home?region=us-east-1#/firstRun) guide for a nice wizard to guide you through the process.

3. Ensure that your IAM user has permission to register images with ECR, upload task definitions to ECS, and deploy images to ECS.

## Step Functions

1. Create a new State Machine with the following definition.

```
{
  "StartAt": "RunTask",
  "Comment": "Run ML Pipeline",
  "States": {
    "RunTask": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "LaunchType": "FARGATE",
        "Cluster": "arn:aws:ecs:us-east-1:<ACCOUNT_ID>:cluster/default",
        "TaskDefinition": "arn:aws:ecs:us-east-1:<ACCOUNT_ID>:task-definition/pkgpkr-ml-task-definition",
        "NetworkConfiguration": {
          "AwsvpcConfiguration": {
            "Subnets": [
              <SUBNET_LIST>
            ],
            "AssignPublicIp": "ENABLED",
            "SecurityGroups": [
              <SECURITY_GROUP_LIST>
            ]
          }
        }
      },
      "End": true
    }
  }
}
```

2. Create a new IAM Role that will allow the State Machine to execute tasks in our ECS cluster.

## CloudWatch

1. Create a new Rule that is scheduled to run daily and execute the State Machine you created.

2. Create a new IAM Role that will allow the Rule to execute the State Machine.

# Pull Request

1. make your final commit for this branch
2. send a pull request from `your branch name` to `origin/dev`

# Merge

1. need at least one peer to review code and approve the change
2. let Jenkins build and check tests(including lint) and do the merge if no error
