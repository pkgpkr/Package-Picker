# AWS Deploy

Check out a new branch

```
git checkout -b deploy_to_aws
```

Install Terraform and initialize it within the `terraform/` folder.

```
cd terraform
terraform init
```

You'll also need to have the AWS CLI installed and configured.

```
aws configure
```

## No custom domain

1. `terraform apply`
    1. Don't provide a value for `DOMAIN_NAME`, just hit 'enter'
    2. `DB_PASSWORD` is the desired password for your database
    3. `DB_USER` is the desired username for your database
2. Create a new GitHub OAuth application
    1. Homepage URL is `http://<ELB DNS name>`
    2. Callback URL is `http://<ELB DNS name>/callback`
3. Set up the database (choose one)
    1. Load data into your database (see "Database" section above)
    2. Start fresh by creating new tables (see "Database" section above)
4. Make sure all environment variables are set as secrets on your GitHub repository (see "Set environment variables" section above)
5. Commit the changes from step 1 and merge your branch to `dev` to trigger the deploy to AWS
6. After the GitHub deploy actions are complete, open the load balancer DNS name in your browser

## pkgpkr.com domain only

1. `terraform apply`
    1. Provide `pkgpkr.com` for `DOMAIN_NAME`
    2. `DB_PASSWORD` is the desired password for your database
    3. `DB_USER` is the desired username for your database
2. Update the `pkgpkr.com` and `*.pkgpkr.com` entries in the `pkgpkr.com` hosted zone to point at the ELB DNS name
3. Set up the database (choose one)
    1. Load data into your database (see "Database" section above)
    2. Start fresh by creating new tables (see "Database" section above)
4. Make sure all environment variables are set as secrets on your GitHub repository (see "Set environment variables" section above)
5. Commit the changes from step 1 and merge your branch to `dev` to trigger the deploy to AWS
6. After the GitHub deploy actions are complete, open pkgpkr.com in your web browser (it may take up to 5 minutes for the TTL on pkgpkr.com to expire)
