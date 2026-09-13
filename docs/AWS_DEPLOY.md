# Deploying to AWS (starting from zero)

You have no AWS account yet, so do these in order. Steps 1-2 matter more
than people think -- it's very easy to leave something running and get a
surprise bill.

## 1. Account setup and safety net (do this first, before any project work)

1. Create an AWS account at https://aws.amazon.com/ (needs a card, but the
   options below fit in the free tier if you're careful about turning things
   off).
2. Go to **Billing > Budgets** and create a budget with an alert at, say,
   $5 and $20. This emails you before things get expensive, not after.
3. Go to **IAM** and create yourself an admin IAM user to work with day to
   day, rather than using the root account login for everything.

## 2. Choose a deployment option

Two reasonable options, in order of how beginner-friendly they are:

### Option A: AWS App Runner (recommended for you)
Fully managed -- you give it a container image, it handles the server,
scaling, and HTTPS for you. No SSH, no manual server admin.

1. Push your Docker image to Amazon ECR (Elastic Container Registry):
   ```
   aws ecr create-repository --repository-name cern-demo
   docker build -t cern-demo -f app/Dockerfile .
   # then follow the "push commands" shown in the ECR console for your new repo
   ```
2. In the App Runner console, create a service pointing at that ECR image,
   port 8000.
3. App Runner gives you a public URL once deployed. Test it:
   ```
   curl https://<your-app-runner-url>/health
   ```
4. **When you're done demoing it, pause or delete the service** -- App
   Runner bills while it's running.

### Option B: A single EC2 instance with Docker (more manual, more to learn)
Better if you specifically want to practice Linux server administration.

1. Launch a `t3.micro` (free-tier eligible) Amazon Linux instance.
2. Create a security group allowing inbound TCP on port 8000 (and 22 for SSH
   from your IP only -- not `0.0.0.0/0`).
3. SSH in, install Docker, `git clone` your repo (or `scp` it over), then:
   ```
   docker build -t cern-demo -f app/Dockerfile .
   docker run -d -p 8000:8000 cern-demo
   ```
4. Visit `http://<instance-public-ip>:8000/health` in a browser.
5. **Stop or terminate the instance when you're not using it.** A stopped
   instance still costs for its storage but not compute; a terminated one
   costs nothing.

## 3. Before you call it "deployed" in your application

- Confirm `/health` and `/predict` both work from *outside* your own
  machine (e.g. from your phone's mobile data, not your home wifi) -- a
  demo that only works on localhost isn't actually deployed.
- Write down what it costs to keep running, and decide in advance whether
  you'll leave it up or take it down after applying. Either is fine --
  just be able to say which, and why, if asked in an interview.
